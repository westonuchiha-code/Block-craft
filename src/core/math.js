// Small math helpers used everywhere.

export const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
export const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
export const lerp = (a, b, t) => a + (b - a) * t;

/** Smooth 0..1 step (Hermite), clamped. */
export function smooth01(t) {
  t = clamp01(t);
  return t * t * (3 - 2 * t);
}

/** Linear blend of two [r,g,b] colours. */
export const mixRgb = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

/** Scale an [r,g,b] colour by k, clamped to 0..255. */
export const shadeRgb = (c, k) => [clamp(c[0] * k, 0, 255), clamp(c[1] * k, 0, 255), clamp(c[2] * k, 0, 255)];

/**
 * Walk a curve given as [input, output] points, easing between neighbours.
 * Two points very close together make a sharp step: that is how cliffs and terraces happen.
 */
export function spline(t, points) {
  if (t <= points[0][0]) return points[0][1];
  for (let i = 1; i < points.length; i++) {
    if (t <= points[i][0]) {
      const [x0, y0] = points[i - 1], [x1, y1] = points[i];
      return y0 + (y1 - y0) * smooth01((t - x0) / (x1 - x0));
    }
  }
  return points[points.length - 1][1];
}
