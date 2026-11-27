// The renderer: owns the Three.js scene, the camera and the meshes of every section of the world, and keeps them up to date.
//
// Sections are meshed on demand: when a chunk arrives (and its neighbours are there, so its edges can be shaded) and when a block
// changes. Meshing is spread over frames, nearest first, within a small time budget, so a burst of new land never stalls a frame.
import * as THREE from 'three';
import { CHUNK_SIZE, SECTIONS_PER_CHUNK } from '../world/constants.js';
import { createBlockTextures } from './textures.js';
import { createBlockMaterials } from './materials.js';
import { createSky } from './sky.js';
import { meshSection } from './mesher.js';

const sectionKey = (cx, cz, sy) => `${cx},${cz},${sy}`;
const MESH_BUDGET_MS = 6;

export class Renderer {
  /** @param {HTMLCanvasElement} canvas */
  constructor(canvas, settings) {
    this.gl = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', stencil: false });
    this.gl.outputColorSpace = THREE.LinearSRGBColorSpace;     // our colours are already the colours we want on screen
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(settings.fov, 16 / 9, 0.05, 1000);
    this.camera.rotation.order = 'YXZ';                        // yaw, then pitch: a first-person camera
    this.textures = createBlockTextures(this.gl.capabilities.getMaxAnisotropy());
    this.materials = createBlockMaterials(this.textures);
    this.sky = createSky(this.scene);
    this.world = null;
    /** @type {Map<string, {solid?: THREE.Mesh, liquid?: THREE.Mesh}>} */
    this.sections = new Map();
    this.dirty = new Set();                                    // section keys waiting to be (re)meshed
    this.urgent = new Set();                                   // sections to re-mesh this very frame (the player just changed them)
    this.highlight = makeHighlightBox();
    this.scene.add(this.highlight);
    this.stats = { sections: 0, triangles: 0, meshedThisFrame: 0 };
    this.applySettings(settings);
  }

  applySettings(settings) {
    this.settings = settings;
    this.camera.fov = settings.fov;
    this.resize();
  }

  /** Size the drawing buffer to the window, times the render scale (1 = native: every screen pixel drawn). */
  resize() {
    const w = window.innerWidth, h = window.innerHeight;
    this.gl.setPixelRatio((window.devicePixelRatio || 1) * this.settings.renderScale);
    this.gl.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  // ---- the world ----

  setWorld(world) {
    for (const s of this.sections.values()) this.disposeSection(s);
    this.sections.clear();
    this.dirty.clear();
    this.world = world;
  }

  /** A chunk arrived: mesh it, and re-mesh its loaded neighbours, whose edges facing it can now be shaded properly. */
  chunkLoaded(chunk) {
    this.markChunk(chunk.cx, chunk.cz);
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) if (this.world.getChunk(chunk.cx + dx, chunk.cz + dz)) this.markChunk(chunk.cx + dx, chunk.cz + dz);
  }

  chunkUnloaded(chunk) {
    for (let sy = 0; sy < SECTIONS_PER_CHUNK; sy++) {
      const key = sectionKey(chunk.cx, chunk.cz, sy), s = this.sections.get(key);
      if (s) { this.disposeSection(s); this.sections.delete(key); }
      this.dirty.delete(key);
    }
  }

  markChunk(cx, cz) {
    const chunk = this.world.getChunk(cx, cz);
    const top = chunk ? chunk.topSection() : -1;
    for (let sy = 0; sy < SECTIONS_PER_CHUNK; sy++) {
      if (sy <= top + 1 || this.sections.has(sectionKey(cx, cz, sy))) this.dirty.add(sectionKey(cx, cz, sy));
    }
  }

  /** A block changed: re-mesh its section, and the neighbouring sections it touches (their faces and shading change too). */
  blockChanged(x, y, z) {
    const cx = Math.floor(x / CHUNK_SIZE), cz = Math.floor(z / CHUNK_SIZE), sy = y >> 4;
    for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) for (let dy = -1; dy <= 1; dy++) {
      const ncx = Math.floor((x + dx) / CHUNK_SIZE), ncz = Math.floor((z + dz) / CHUNK_SIZE), nsy = (y + dy) >> 4;
      if (nsy >= 0 && nsy < SECTIONS_PER_CHUNK) this.urgent.add(sectionKey(ncx, ncz, nsy));
    }
    this.urgent.add(sectionKey(cx, cz, sy));
  }

  /** Mesh waiting sections, nearest first, within the frame's time budget. */
  updateMeshes(eye) {
    const t0 = performance.now();
    let n = 0;
    for (const key of this.urgent) { this.dirty.delete(key); this.rebuild(key); n++; }
    this.urgent.clear();
    if (this.dirty.size) {
      const pcx = eye.x / CHUNK_SIZE, pcz = eye.z / CHUNK_SIZE, psy = eye.y / 16;
      const order = [...this.dirty].map(k => { const [cx, cz, sy] = k.split(',').map(Number); return [k, cx, cz, (cx + 0.5 - pcx) ** 2 + (cz + 0.5 - pcz) ** 2 + 0.3 * (sy + 0.5 - psy) ** 2]; });
      order.sort((a, b) => a[3] - b[3]);
      for (const [key, cx, cz] of order) {
        if (performance.now() - t0 > MESH_BUDGET_MS) break;
        if (!this.neighboursLoaded(cx, cz)) continue;          // wait, so its edges are drawn right the first time
        this.dirty.delete(key);
        this.rebuild(key);
        n++;
      }
    }
    this.stats.meshedThisFrame = n;
  }

  /** Is everything within `radius` chunks of this one meshed (nothing there still waiting)? */
  isAreaMeshed(cx, cz, radius) {
    for (const key of this.dirty) {
      const [x, z] = key.split(',').map(Number);
      if (Math.abs(x - cx) <= radius && Math.abs(z - cz) <= radius) return false;
    }
    return true;
  }

  neighboursLoaded(cx, cz) {
    const w = this.world;
    return w.getChunk(cx, cz) && w.getChunk(cx + 1, cz) && w.getChunk(cx - 1, cz) && w.getChunk(cx, cz + 1) && w.getChunk(cx, cz - 1);
  }

  rebuild(key) {
    const [cx, cz, sy] = key.split(',').map(Number);
    const old = this.sections.get(key);
    if (old) { this.disposeSection(old); this.sections.delete(key); }
    if (!this.world.getChunk(cx, cz)) return;
    const data = meshSection(this.world, cx, cz, sy, this.textures.faceLayer);
    const entry = {};
    for (const kind of ['solid', 'liquid']) {
      if (!data[kind]) continue;
      const mesh = new THREE.Mesh(toGeometry(data[kind]), this.materials[kind]);
      mesh.position.set(cx * CHUNK_SIZE, sy * 16, cz * CHUNK_SIZE);
      mesh.matrixAutoUpdate = false;
      mesh.updateMatrix();
      if (kind === 'liquid') mesh.renderOrder = 1;
      this.scene.add(mesh);
      entry[kind] = mesh;
    }
    if (entry.solid || entry.liquid) this.sections.set(key, entry);
  }

  disposeSection(s) {
    for (const m of [s.solid, s.liquid]) if (m) { this.scene.remove(m); m.geometry.dispose(); }
  }

  // ---- each frame ----

  /**
   * @param {{x:number,y:number,z:number,yaw:number,pitch:number}} view  where the eye is and where it looks
   * @param {number} time  time of day 0..1
   * @param {{x:number,y:number,z:number}|null} target  the block the player is pointing at, outlined
   */
  render(view, time, target) {
    this.camera.position.set(view.x, view.y, view.z);
    this.camera.rotation.set(view.pitch, view.yaw, 0);
    this.updateMeshes(this.camera.position);

    const sky = this.sky.update(time, this.camera.position);
    const u = this.materials.uniforms;
    u.daylight.value = sky.daylight;
    u.sunTint.value.copy(sky.sunTint);
    u.fogColour.value.copy(sky.fog);
    const reach = this.settings.renderDistance * CHUNK_SIZE;
    u.fogNear.value = reach * 0.6;
    u.fogFar.value = reach * 0.95;
    this.camera.far = reach * 1.2 + 32;
    this.camera.updateProjectionMatrix();

    this.highlight.visible = !!target;
    if (target) this.highlight.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);

    this.gl.render(this.scene, this.camera);
    const info = this.gl.info.render;
    this.stats.sections = this.sections.size;
    this.stats.triangles = info.triangles;
  }
}

function toGeometry(d) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(d.position, 3));
  g.setAttribute('uv', new THREE.BufferAttribute(d.uv, 2));
  g.setAttribute('layer', new THREE.BufferAttribute(d.layer, 1));
  g.setAttribute('light', new THREE.BufferAttribute(d.light, 3));
  g.setAttribute('tint', new THREE.BufferAttribute(d.tint, 3));
  g.setIndex(new THREE.BufferAttribute(d.index, 1));
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(8, 8, 8), 14);
  return g;
}

/** A thin dark outline round the block the player is pointing at. */
function makeHighlightBox() {
  const box = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.004, 1.004, 1.004)),
    new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.55 }),
  );
  box.visible = false;
  return box;
}
