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

  // light: sky light scaled by the time of day, and warm block light from torches, lava and glowstone; whichever is brighter
  // wins. Levels are turned into brightness on a curve (level 8 of 15 gives about a third), so light fades off into the dark
  // the way it does in Minecraft. A small floor keeps the darkest caves just readable. The corner shading goes on top.
  vec2 level = clamp(vLight.yz, 0.0, 1.0);
  vec2 bright = level / (3.0 - 2.0 * level);
  vec3 skyLight = vec3(bright.x * mix(0.2, 1.0, daylight)) * mix(vec3(1.0), sunTint, level.x);   // night keeps a fifth: moonlit
  vec3 glowLight = bright.y * vec3(1.0, 0.84, 0.62);
  vec3 lit = colour * max(max(skyLight, glowLight), vec3(0.055, 0.06, 0.075)) * vLight.x;   // the floor is a faint cool grey

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
