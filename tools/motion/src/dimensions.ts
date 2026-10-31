/**
 * Aspect ratio to pixel size. One template serves every aspect: Root.tsx reads
 * the `aspect` prop (set by render.mjs from --aspect) and sizes the frame.
 */

export type Aspect = "1:1" | "16:9" | "9:16" | "4:3" | "3:4" | "4:5" | "5:4";

export const DIMENSIONS: Record<Aspect, { width: number; height: number }> = {
  "16:9": { width: 1920, height: 1080 },
  "9:16": { width: 1080, height: 1920 },
  "1:1": { width: 1080, height: 1080 },
  "4:5": { width: 1080, height: 1350 },
  "5:4": { width: 1350, height: 1080 },
  "4:3": { width: 1440, height: 1080 },
  "3:4": { width: 1080, height: 1440 },
};

export const isAspect = (v: unknown): v is Aspect => typeof v === "string" && v in DIMENSIONS;

export const dimensionsFor = (aspect: unknown, fallback: Aspect = "16:9") =>
  DIMENSIONS[isAspect(aspect) ? aspect : fallback];

/** Text stays inside the inner 80% of the frame. Percent inset of the short edge. */
export const SAFE_ZONE_INSET_PCT = 10;

/**
 * On a vertical frame the top and bottom sixth are covered by the phone app's
 * buttons and caption, so text and logos stay out of them.
 */
export const VERTICAL_UI_ZONE_PCT = 100 / 6;

export const FPS = 30;

/** Seconds to whole frames, never below one. */
export const toFrames = (seconds: number | undefined, fallback: number, fps = FPS) =>
  Math.max(1, Math.round((seconds ?? fallback) * fps));
