export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const ease = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
export const pad3 = (n: number) => String(Math.round(n)).padStart(3, "0");

export type StageName = "Solid" | "Soft" | "Gooey" | "Puddle";
export const stageName = (m: number): StageName =>
  m < 17 ? "Solid" : m < 50 ? "Soft" : m < 83 ? "Gooey" : "Puddle";

export const MOODS: { name: StageName; m: number }[] = [
  { name: "Solid", m: 0 },
  { name: "Soft", m: 33 },
  { name: "Gooey", m: 66 },
  { name: "Puddle", m: 100 },
];

type Cache = { m?: number; b?: number; s?: number };
const cache = new WeakMap<HTMLElement, Cache>();

/** Write --m / --b / --s on an element, skipping changes smaller than .15. */
export function setAxes(el: HTMLElement, m?: number | null, b?: number | null, s?: number | null) {
  let c = cache.get(el);
  if (!c) cache.set(el, (c = {}));
  if (m != null && Math.abs((c.m ?? -9) - m) > 0.15) { c.m = m; el.style.setProperty("--m", m.toFixed(1)); }
  if (b != null && Math.abs((c.b ?? -9) - b) > 0.15) { c.b = b; el.style.setProperty("--b", b.toFixed(1)); }
  if (s != null && Math.abs((c.s ?? -9) - s) > 0.15) { c.s = s; el.style.setProperty("--s", s.toFixed(1)); }
}
