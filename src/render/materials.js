// The shaders that draw blocks. One material for everything opaque or cut out (rock, leaves, glass, plants), one for liquids.
import * as THREE from 'three';
import { TINT_BASE } from './tiles.js';

const VERTEX = /* glsl */`
in float layer;
in vec3 light;
in vec3 tint;
out vec3 vUv;
out vec3 vLight;
out vec3 vTint;
out float vFogDepth;
void main() {
  vUv = vec3(uv, layer);
  vLight = light;
  vTint = tint;
  vec4 viewPos = modelViewMatrix * vec4(position, 1.0);
  vFogDepth = length(viewPos.xyz);
  gl_Position = projectionMatrix * viewPos;
}`;

const FRAGMENT = /* glsl */`
precision highp float;
precision highp sampler2DArray;
uniform sampler2DArray colourMap;
uniform sampler2DArray tintMap;
uniform float daylight;          // 0 at midnight .. 1 at noon
uniform vec3 sunTint;            // warm at dawn and dusk, white at noon
uniform vec3 fogColour;
uniform float fogNear;
uniform float fogFar;
uniform float alphaCut;          // texels below this alpha are holes (leaves); 0 for liquids
uniform float opacity;           // liquids are drawn see-through
in vec3 vUv;
in vec3 vLight;
in vec3 vTint;
in float vFogDepth;
out vec4 outColour;
void main() {
  vec4 tex = texture(colourMap, vUv);
  if (tex.a < alphaCut) discard;
  float tintAmount = texture(tintMap, vUv).r;
  vec3 colour = tex.rgb * mix(vec3(1.0), vTint / ${TINT_BASE.toFixed(3)}, tintAmount);

  // light: daylight where the sky reaches, a dim floor so caves are dark but not black, the corner shading on top
  float sky = vLight.y * mix(0.24, 1.0, daylight);     // night keeps a quarter of the light: moonlit, dark but playable
  float ambient = max(sky, max(vLight.z, 0.045));
  vec3 lit = colour * ambient * vLight.x * mix(vec3(1.0), sunTint, vLight.y);

  float fog = smoothstep(fogNear, fogFar, vFogDepth);
  outColour = vec4(mix(lit, fogColour, fog), opacity);
}`;

export function createBlockMaterials(textures) {
  const uniforms = {
    colourMap: { value: textures.colour },
    tintMap: { value: textures.tintMask },
    daylight: { value: 1 },
    sunTint: { value: new THREE.Color(1, 1, 1) },
    fogColour: { value: new THREE.Color(0.7, 0.75, 0.8) },
    fogNear: { value: 100 },
    fogFar: { value: 200 },
  };
  const make = (extra, options) => new THREE.ShaderMaterial({
    glslVersion: THREE.GLSL3,
    vertexShader: VERTEX,
    fragmentShader: FRAGMENT,
    uniforms: { ...uniforms, ...extra },
    ...options,
  });
  const solid = make({ alphaCut: { value: 0.5 }, opacity: { value: 1 } }, { alphaToCoverage: true });
  const liquid = make({ alphaCut: { value: 0 }, opacity: { value: 0.72 } }, { transparent: true, depthWrite: false, side: THREE.DoubleSide });
  return { solid, liquid, uniforms };
}
