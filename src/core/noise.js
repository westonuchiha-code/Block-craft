// Deterministic hashing and noise. Everything in the world is worked out from (x, y, z) and the world seed with these,
// so any block can be recomputed at any time and two players with the same seed get the same world.
import { clamp01 } from './math.js';

/** Hash of three integers and a salt, as a number in [0, 1). */
export function hash3(x, y, z, salt) {
  let h = Math.imul(x | 0, 0x27d4eb2d) ^ Math.imul(y | 0, 0x165667b1) ^
          Math.imul(z | 0, 0x85ebca77) ^ Math.imul(salt | 0, 0xc2b2ae3d);
  h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d);
  h ^= h >>> 12; h = Math.imul(h, 0x297a2d39);
  h ^= h >>> 15;
  return (h >>> 0) / 4294967296;
}

/** 2D value noise in [0, 1]: random values on a grid, eased between. Cheap, a little blocky. */
export function valueNoise(x, z, salt) {
  const xi = Math.floor(x), zi = Math.floor(z), xf = x - xi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf), v = zf * zf * (3 - 2 * zf);
  const a = hash3(xi, 0, zi, salt), b = hash3(xi + 1, 0, zi, salt);
  const c = hash3(xi, 0, zi + 1, salt), d = hash3(xi + 1, 0, zi + 1, salt);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}

/** 3D value noise in [0, 1]. */
export function valueNoise3(x, y, z, salt) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), w = zf * zf * (3 - 2 * zf);
  const l = (a, b, t) => a + (b - a) * t;
  const c000 = hash3(xi, yi, zi, salt), c100 = hash3(xi + 1, yi, zi, salt);
  const c010 = hash3(xi, yi + 1, zi, salt), c110 = hash3(xi + 1, yi + 1, zi, salt);
  const c001 = hash3(xi, yi, zi + 1, salt), c101 = hash3(xi + 1, yi, zi + 1, salt);
  const c011 = hash3(xi, yi + 1, zi + 1, salt), c111 = hash3(xi + 1, yi + 1, zi + 1, salt);
  return l(l(l(c000, c100, u), l(c010, c110, u), v), l(l(c001, c101, u), l(c011, c111, u), v), w);
}

const GRAD_X = [1, -1, 1, -1, 1, -1, 0, 0];
const GRAD_Z = [1, 1, -1, -1, 0, 0, 1, -1];

/** 2D gradient noise in [0, 1]: smoother and less grid-shaped than value noise. */
export function gradientNoise(x, z, salt) {
  const xi = Math.floor(x), zi = Math.floor(z), xf = x - xi, zf = z - zi;
  const u = xf * xf * xf * (xf * (xf * 6 - 15) + 10);
  const v = zf * zf * zf * (zf * (zf * 6 - 15) + 10);
  const dot = (ix, iz, dx, dz) => {
    const k = Math.floor(hash3(ix, 1, iz, salt) * 8);
    return GRAD_X[k] * dx + GRAD_Z[k] * dz;
  };
  const n00 = dot(xi, zi, xf, zf), n10 = dot(xi + 1, zi, xf - 1, zf);
  const n01 = dot(xi, zi + 1, xf, zf - 1), n11 = dot(xi + 1, zi + 1, xf - 1, zf - 1);
  const a = n00 + (n10 - n00) * u, b = n01 + (n11 - n01) * u;
  return clamp01((a + (b - a) * v) * 0.6 + 0.5);
}

/** Three octaves of gradient noise (each finer and half as strong), stretched to spread across [0, 1]. */
export function fbm(x, z, salt) {
  const n = (gradientNoise(x, z, salt) +
             gradientNoise(x * 2.03, z * 2.03, salt + 1) * 0.5 +
             gradientNoise(x * 4.11, z * 4.11, salt + 2) * 0.25) / 1.75;
  return clamp01((n - 0.5) * 2.2 + 0.5);
}

/** A small seeded random number generator (mulberry32): the same seed always gives the same sequence. */
export function makeRng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
