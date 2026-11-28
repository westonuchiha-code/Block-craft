// The shaders that draw blocks. One material for everything opaque or cut out (rock, leaves, glass, plants), one for liquids.
// Both share the vertex shader and the lighting; the liquid material is the same fragment shader compiled with LIQUID defined,
// which adds water's moving surface, sky reflection and depth, and lava's slow flow.
import * as THREE from 'three';
import { TINT_BASE } from './tiles.js';

const VERTEX = /* glsl */`
in float layer;
in vec3 light;
in vec3 tint;
out vec3 vUv;
out vec3 vLight;
out vec3 vTint;
out vec3 vWorldPos;
out float vFogDepth;
void main() {
  vUv = vec3(uv, layer);
  vLight = light;
  vTint = tint;
  vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
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
in vec3 vWorldPos;
in float vFogDepth;
out vec4 outColour;

// Light: sky light scaled by the time of day, and warm block light from torches, lava and glowstone; whichever is brighter
// wins. Levels are turned into brightness on a curve (level 8 of 15 gives about a third), so light fades off into the dark the
// way it does in Minecraft. A small floor keeps the darkest caves just readable. The corner shading goes on top.
// Returns the light to multiply a colour by; skyBright is the sky part alone (for reflections).
vec3 blockLight(out float skyBright) {
  vec2 level = clamp(vLight.yz, 0.0, 1.0);
  vec2 bright = level / (3.0 - 2.0 * level);
  skyBright = bright.x;
  vec3 skyLight = vec3(bright.x * mix(0.2, 1.0, daylight)) * mix(vec3(1.0), sunTint, level.x);   // night keeps a fifth: moonlit
  vec3 glowLight = bright.y * vec3(1.0, 0.84, 0.62);
  return max(max(skyLight, glowLight), vec3(0.055, 0.06, 0.075)) * vLight.x;              // the floor is a faint cool grey
}

#ifndef LIQUID

void main() {
  vec4 tex = texture(colourMap, vUv);
  if (tex.a < alphaCut) discard;
  float tintAmount = texture(tintMap, vUv).r;
  vec3 colour = tex.rgb * mix(vec3(1.0), vTint / ${TINT_BASE.toFixed(3)}, tintAmount);
  float skyBright;
  vec3 lit = colour * blockLight(skyBright);
  float fog = smoothstep(fogNear, fogFar, vFogDepth);
  outColour = vec4(mix(lit, fogColour, fog), opacity);
}

#else

uniform float time;              // seconds, wrapped so the waves keep their precision
uniform vec3 sunDir;
uniform float sunAmount;         // 0 when the sun is down
uniform vec3 skyTop;             // the sky straight up, and at the horizon: what the water reflects
uniform vec3 skyHorizon;

// The height of the ripples at a point on the water: three slow waves crossing at angles.
float ripple(vec2 p) {
  return sin(p.x * 1.7 + p.y * 0.9 + time * 1.3) + 0.7 * sin(-p.x * 0.8 + p.y * 2.1 + time * 0.9) + 0.35 * sin((p.x + p.y) * 3.3 - time * 1.9);
}

void main() {
  bool water = vTint.y > 0.5;
  float depth = vTint.x;                               // 0 at the shore .. 1 where it is deep

  // the texture drifts slowly across the surface (lava more slowly), sampled with the unmoved gradients so tile edges stay clean
  vec2 flow = water ? vec2(0.025, 0.015) * time : vec2(0.008, 0.005) * time;
  vec4 tex = textureGrad(colourMap, vec3(fract(vUv.xy + flow), vUv.z), dFdx(vUv.xy), dFdy(vUv.xy));
  float skyBright;
  vec3 lit = tex.rgb * blockLight(skyBright);
  float fog = smoothstep(fogNear, fogFar, vFogDepth);
  if (!water) { outColour = vec4(mix(lit, fogColour, fog), 0.97); return; }      // lava: nearly opaque, lit by its own glow

  vec3 toEye = normalize(cameraPosition - vWorldPos);
  vec3 normal = normalize(cross(dFdx(vWorldPos), dFdy(vWorldPos)));
  if (dot(normal, toEye) < 0.0) normal = -normal;      // the side facing the eye
  bool underneath = normal.y < -0.5;                   // looking up at the surface from under the water

  // ripples on the top surface: the normal tilts with the slope of the waves, in steps of one texture pixel so the surface
  // stays blocky; they fade out with distance, where pixel-sized ripples would only shimmer
  if (normal.y > 0.5) {
    vec2 p = floor(vWorldPos.xz * 16.0) / 16.0;
    float e = 1.0 / 16.0, h = ripple(p);
    float strength = 1.4 * (1.0 - smoothstep(12.0, 56.0, vFogDepth));
    normal = normalize(vec3((h - ripple(p + vec2(e, 0.0))) * strength, 1.0, (h - ripple(p + vec2(0.0, e))) * strength));
  }

  // deep water is darker and less see-through
  lit *= mix(1.0, 0.5, depth);
  float alpha = mix(0.58, 0.9, sqrt(depth));

  if (!underneath) {
    // reflection of the sky, strong at a glancing angle and weak looking straight down (Fresnel), only where the sky reaches
    float facing = max(dot(normal, toEye), 0.0);
    float fresnel = 0.05 + 0.6 * pow(1.0 - facing, 4.0);
    vec3 r = reflect(-toEye, normal);
    vec3 sky = mix(skyHorizon, skyTop, sqrt(clamp(r.y, 0.0, 1.0))) * skyBright;
    float glint = pow(max(dot(r, sunDir), 0.0), 350.0) * sunAmount * skyBright * 2.0;
    lit = mix(lit, sky, fresnel * skyBright) + glint * vec3(1.0, 0.95, 0.85);
    alpha = mix(alpha, 1.0, fresnel * skyBright);
  }
  outColour = vec4(mix(lit, fogColour, fog), alpha);
}

#endif
`;

export function createBlockMaterials(textures) {
  const uniforms = {
    colourMap: { value: textures.colour },
    tintMap: { value: textures.tintMask },
    daylight: { value: 1 },
    sunTint: { value: new THREE.Color(1, 1, 1) },
    fogColour: { value: new THREE.Color(0.7, 0.75, 0.8) },
    fogNear: { value: 100 },
    fogFar: { value: 200 },
    time: { value: 0 },
    sunDir: { value: new THREE.Vector3(0, 1, 0) },
    sunAmount: { value: 1 },
    skyTop: { value: new THREE.Color(0.4, 0.6, 0.9) },
    skyHorizon: { value: new THREE.Color(0.7, 0.8, 0.9) },
  };
  const make = (extra, options) => new THREE.ShaderMaterial({
    glslVersion: THREE.GLSL3,
    vertexShader: VERTEX,
    fragmentShader: FRAGMENT,
    uniforms: { ...uniforms, ...extra },
    ...options,
  });
  const solid = make({ alphaCut: { value: 0.5 }, opacity: { value: 1 } }, { alphaToCoverage: true });
  const liquid = make({ alphaCut: { value: 0 }, opacity: { value: 1 } }, { defines: { LIQUID: '' }, transparent: true, depthWrite: false, side: THREE.DoubleSide });
  return { solid, liquid, uniforms };
}
