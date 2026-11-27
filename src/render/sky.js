// The sky: a dome coloured from the zenith down to the horizon, with the sun, the moon and the stars drawn on it (so they are
// always behind everything).
// Also works out, from the time of day, how bright the world is and what colour the fog is.
import * as THREE from 'three';
import { clamp01, smooth01 } from '../core/math.js';

const DAY_TOP = new THREE.Color(0.36, 0.55, 0.86), DAY_HORIZON = new THREE.Color(0.74, 0.83, 0.92);
const DUSK_TOP = new THREE.Color(0.24, 0.27, 0.48), DUSK_HORIZON = new THREE.Color(0.96, 0.58, 0.36);
const NIGHT_TOP = new THREE.Color(0.01, 0.015, 0.05), NIGHT_HORIZON = new THREE.Color(0.05, 0.06, 0.12);

const DOME_VERTEX = /* glsl */`
out vec3 vDir;
void main() {
  vDir = normalize(position);
  vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  gl_Position = p.xyww;            // always at the far plane
}`;
const DOME_FRAGMENT = /* glsl */`
precision highp float;
uniform vec3 topColour;
uniform vec3 horizonColour;
uniform vec3 sunDir;
uniform float starAmount;
uniform float sunAmount;
in vec3 vDir;
out vec4 outColour;
float hash(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
// a square disc (everything in this world is square) of angular half-size "size" centred on direction c
float squareDisc(vec3 d, vec3 c, float size) {
  if (dot(d, c) <= 0.0) return 0.0;
  vec3 r = normalize(cross(c, vec3(0.0, 0.0, 1.0)));
  vec3 u = cross(r, c);
  vec3 p = d / dot(d, c);
  return step(max(abs(dot(p, r)), abs(dot(p, u))), size);
}
void main() {
  vec3 d = normalize(vDir);
  float h = clamp(d.y, -0.2, 1.0);
  vec3 c = mix(horizonColour, topColour, smoothstep(0.0, 0.55, h));
  c = mix(c, horizonColour * 0.6, smoothstep(0.0, -0.2, d.y));                         // below the horizon
  float glow = pow(max(dot(d, sunDir), 0.0), 8.0);
  c += glow * horizonColour * 0.35;                                                     // haze round the sun
  vec3 cell = floor(d * 300.0);
  float star = step(0.9975, hash(cell)) * smoothstep(0.0, 0.25, d.y);
  c += vec3(star) * starAmount * 0.9 * (1.0 - squareDisc(d, -sunDir, 0.05));
  c = mix(c, vec3(1.0, 0.95, 0.75), squareDisc(d, sunDir, 0.055) * sunAmount);        // the sun
  c = mix(c, vec3(0.86, 0.89, 0.94), squareDisc(d, -sunDir, 0.04) * starAmount);       // the moon, opposite it
  outColour = vec4(c, 1.0);
}`;

export function createSky(scene) {
  const uniforms = {
    topColour: { value: new THREE.Color() },
    horizonColour: { value: new THREE.Color() },
    sunDir: { value: new THREE.Vector3(0, 1, 0) },
    starAmount: { value: 0 },
    sunAmount: { value: 1 },
  };
  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(10, 32, 16),
    new THREE.ShaderMaterial({ glslVersion: THREE.GLSL3, vertexShader: DOME_VERTEX, fragmentShader: DOME_FRAGMENT, uniforms, side: THREE.BackSide, depthWrite: false }),
  );
  dome.renderOrder = -10;
  dome.frustumCulled = false;
  scene.add(dome);

  const state = { daylight: 1, sunTint: new THREE.Color(1, 1, 1), fog: new THREE.Color(), sunDir: new THREE.Vector3() };

  /**
   * @param {number} time  time of day 0..1 (0.25 noon, 0.75 midnight)
   * @param {THREE.Vector3} eye camera position: the dome, sun and moon travel with it
   */
  function update(time, eye) {
    const angle = (time - 0.25) * Math.PI * 2;                // 0 at noon
    state.sunDir.set(Math.sin(angle) * 0.92, Math.cos(angle), 0.38).normalize();
    const elevation = state.sunDir.y;
    const day = smooth01((elevation + 0.12) / 0.4);             // 0 at night, 1 when the sun is well up
    const dusk = clamp01(1 - Math.abs(elevation) / 0.32) ;      // near sunrise and sunset
    state.daylight = day;

    const top = NIGHT_TOP.clone().lerp(DAY_TOP, day).lerp(DUSK_TOP, dusk * 0.35);
    const horizon = NIGHT_HORIZON.clone().lerp(DAY_HORIZON, day).lerp(DUSK_HORIZON, dusk * 0.6);
    uniforms.topColour.value.copy(top);
    uniforms.horizonColour.value.copy(horizon);
    uniforms.sunDir.value.copy(state.sunDir);
    uniforms.starAmount.value = 1 - day;
    uniforms.sunAmount.value = smooth01((elevation + 0.1) / 0.15);
    state.fog.copy(horizon);
    state.sunTint.setRGB(1, 1, 1).lerp(new THREE.Color(1.08, 0.86, 0.72), dusk * 0.7);

    dome.position.copy(eye);
    return state;
  }

  return { update, state };
}
