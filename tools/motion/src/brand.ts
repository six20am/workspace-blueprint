/**
 * Look tokens: colors and font stacks.
 *
 * These are neutral defaults only. Every template takes a `brand` prop that
 * overrides any of them, so the owner's colors arrive in the props file and
 * this file never changes. Example: "brand": { "accent": "#e4572e" }.
 */

export type Brand = {
  /** Main text color on the surface (light on the dark default surface). */
  ink: string;
  /** Accent for rules, highlights, progress and the spoken word in captions. */
  accent: string;
  /** Small label color. Falls back to `accent` when unset. */
  eyebrowText?: string;
  /** Multiplier on the cover label size. Defaults to 1. */
  eyebrowScale?: number;
  /** Background behind letterboxed content and on type-only frames. */
  surface: string;
  /** Caption text color. */
  captionText: string;
  /** Plate behind burned-in captions. */
  captionPlate: string;
  /** Headline font stack. System fonts only, so nothing is fetched at render time. */
  headlineFont: string;
  /** Caption and body font stack. */
  captionFont: string;
};

export const DEFAULT_BRAND: Brand = {
  ink: "#f4f5f7",
  accent: "#2bb5a8",
  surface: "#16191f",
  captionText: "#ffffff",
  captionPlate: "rgba(16, 18, 22, 0.82)",
  headlineFont: '"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif',
  captionFont: '"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif',
};

export const resolveBrand = (override?: Partial<Brand>): Brand => ({
  ...DEFAULT_BRAND,
  ...(override ?? {}),
});
