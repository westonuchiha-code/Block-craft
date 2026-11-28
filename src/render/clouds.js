// Clouds: a layer of flat-topped boxes high over the land, as in Minecraft. The sky is cut into cells 12 blocks square; a slow
// noise picks which cells hold cloud, so cells clump into clouds of all sizes. Each cloud cell is a box 4 blocks thick, and the
// sides between two cloud cells are left out, so a cloud is one solid shape.
//
// The layer drifts slowly east. It is built for the cells round the player (out to CLOUD_RANGE) and rebuilt only when the player
// or the drift crosses into another cell. Clouds take the colour of the time of day and fade out towards the edge of the layer.
import * as THREE from 'three';
import { valueNoise } from '../core/noise.js';

const CELL = 12;                 // blocks per cloud cell
const THICKNESS = 4;
export const CLOUD_HEIGHT = 182; // the bottom of the clouds
export const CLOUD_RANGE = 384;  // how far out the layer reaches, in blocks
const RADIUS = Math.ceil(CLOUD_RANGE / CELL);
const DRIFT = 1.2;               // blocks per second, eastwards
const SALT = 4242;
const NIGHT = new THREE.Color(0.1, 0.11, 0.16), WHITE = new THREE.Color(1, 1, 1);

// face shading, like the blocks: tops brightest, bottoms darkest
const SHADE_TOP = 1.0, SHADE_BOTTOM = 0.7, SHADE_EW = 0.86, SHADE_NS = 0.78;

/** Is there cloud in this cell? Two scales of noise: big shapes with ragged edges. */
function cloudAt(i, j) {
  return valueNoise(i / 5.5, j / 5.5, SALT) * 0.72 + valueNoise(i / 1.7, j / 1.7, SALT + 1) * 0.28 > 0.6;
}

const VERTEX = /* glsl */`
in float shade;
out float vShade;
out vec3 vWorldPos;
void main() {
  vShade = shade;
  vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const FRAGMENT = /* glsl */`
precision highp float;
uniform vec3 colour;             // the clouds' colour at this time of day
uniform vec3 fogColour;
uniform vec3 eye;
uniform float range;
in float vShade;
in vec3 vWorldPos;
out vec4 outColour;
void main() {
  float distance = length(vWorldPos.xz - eye.xz);
  float near = 1.0 - smoothstep(range * 0.45, range * 0.95, distance);   // 1 close by, 0 at the edge of the layer
  vec3 c = mix(fogColour, colour * vShade, 0.35 + 0.65 * near);
  outColour = vec4(c, 0.88 * near);
}`;

export function createClouds(scene) {
  const material = new THREE.ShaderMaterial({
    glslVersion: THREE.GLSL3, vertexShader: VERTEX, fragmentShader: FRAGMENT,
    uniforms: { colour: { value: new THREE.Color(1, 1, 1) }, fogColour: { value: new THREE.Color() }, eye: { value: new THREE.Vector3() }, range: { value: CLOUD_RANGE } },
    transparent: true, depthWrite: false,
  });
  const mesh = new THREE.Mesh(new THREE.BufferGeometry(), material);
  mesh.frustumCulled = false;
  mesh.renderOrder = 0.5;          // after the land, before water (so water seen in front of clouds blends over them)
  scene.add(mesh);
  let builtFor = null;

  /** Build the boxes for the cells round cell (ci, cj); positions relative to that cell's corner. */
  function build(ci, cj) {
    const pos = [], shade = [], index = [];
    const quad = (corners, s) => {
      const n = pos.length / 3;
      for (const c of corners) { pos.push(...c); shade.push(s); }
      index.push(n, n + 1, n + 2, n, n + 2, n + 3);
    };
    const T = THICKNESS;
    for (let di = -RADIUS; di <= RADIUS; di++) for (let dj = -RADIUS; dj <= RADIUS; dj++) {
      if (di * di + dj * dj > RADIUS * RADIUS || !cloudAt(ci + di, cj + dj)) continue;
      const x0 = di * CELL, x1 = x0 + CELL, z0 = dj * CELL, z1 = z0 + CELL;
      // corners wound counter-clockwise seen from outside
      quad([[x0, T, z1], [x1, T, z1], [x1, T, z0], [x0, T, z0]], SHADE_TOP);
      quad([[x0, 0, z0], [x1, 0, z0], [x1, 0, z1], [x0, 0, z1]], SHADE_BOTTOM);
      if (!cloudAt(ci + di + 1, cj + dj)) quad([[x1, 0, z1], [x1, 0, z0], [x1, T, z0], [x1, T, z1]], SHADE_EW);
      if (!cloudAt(ci + di - 1, cj + dj)) quad([[x0, 0, z0], [x0, 0, z1], [x0, T, z1], [x0, T, z0]], SHADE_EW);
      if (!cloudAt(ci + di, cj + dj + 1)) quad([[x0, 0, z1], [x1, 0, z1], [x1, T, z1], [x0, T, z1]], SHADE_NS);
      if (!cloudAt(ci + di, cj + dj - 1)) quad([[x1, 0, z0], [x0, 0, z0], [x0, T, z0], [x1, T, z0]], SHADE_NS);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
    g.setAttribute('shade', new THREE.BufferAttribute(new Float32Array(shade), 1));
    g.setIndex(new THREE.BufferAttribute(new Uint32Array(index), 1));
    mesh.geometry.dispose();
    mesh.geometry = g;
  }

  /**
   * @param {THREE.Vector3} eye
   * @param {number} seconds  a steady clock, for the drift
   * @param {{daylight:number, sunTint:THREE.Color, fog:THREE.Color, horizon:THREE.Color}} sky
   */
  function update(eye, seconds, sky) {
    const drift = (seconds * DRIFT) % (CELL * 100000);
    const ci = Math.floor((eye.x + drift) / CELL), cj = Math.floor(eye.z / CELL);
    if (!builtFor || builtFor[0] !== ci || builtFor[1] !== cj) { build(ci, cj); builtFor = [ci, cj]; }
    mesh.position.set(ci * CELL - drift, CLOUD_HEIGHT, cj * CELL);
    // white by day, dark blue-grey at night, and at dawn and dusk they take the warm glow of the sky near the horizon
    const dusk = 1 - Math.abs(2 * sky.daylight - 1);
    const glow = sky.horizon.clone().multiplyScalar(1.25);
    material.uniforms.colour.value.copy(NIGHT).lerp(WHITE, sky.daylight).multiply(sky.sunTint).lerp(glow, dusk * 0.6);
    material.uniforms.fogColour.value.copy(sky.fog);
    material.uniforms.eye.value.copy(eye);
  }

  return { mesh, update };
}
