import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";

/**
 * Slow zoom or pan across one still, so a photo becomes a short moving shot.
 * It does not invent footage. Restrained on purpose: the frame moves from the
 * first frame, but the push stays near 8% so it never lurches.
 */

export type KenBurnsProps = {
  /** The picture. */
  src: string;
  /** Where the frame drifts. */
  direction?: "in" | "out" | "left" | "right" | "up" | "down";
  /** Peak zoom. 1.08 is an 8% push over the whole clip. */
  zoom?: number;
  seconds?: number;
  brand?: Partial<Brand>;
};

/** Scale and translate for a drift at eased progress `p`. Shared with Slideshow. */
export const driftTransform = (direction: string, zoom: number, p: number) => {
  if (direction === "none") return "scale(1)";
  const isPush = direction === "in" || direction === "out";
  const scale = isPush
    ? direction === "in"
      ? interpolate(p, [0, 1], [1, zoom])
      : interpolate(p, [0, 1], [zoom, 1])
    : zoom;
  // Pans hold a constant overscan so there is room to travel without showing an edge.
  const travelPct = (zoom - 1) * 100 * 0.5;
  const shift = interpolate(p, [0, 1], [-travelPct, travelPct]);
  const translate =
    direction === "left"
      ? `translateX(${-shift}%)`
      : direction === "right"
        ? `translateX(${shift}%)`
        : direction === "up"
          ? `translateY(${-shift}%)`
          : direction === "down"
            ? `translateY(${shift}%)`
            : "";
  return `scale(${scale}) ${translate}`;
};

/** Smoothstep 0 to 1 across `frames`, so there is motion at frame 0 without a jolt. */
export const smoothProgress = (frame: number, frames: number) => {
  const raw = interpolate(frame, [0, Math.max(1, frames - 1)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return raw * raw * (3 - 2 * raw);
};

export const KenBurns: React.FC<KenBurnsProps> = ({ src, direction = "in", zoom = 1.08, brand }) => {
  const b = resolveBrand(brand);
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = smoothProgress(frame, durationInFrames);
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface, overflow: "hidden" }}>
      <Img
        src={asset(src)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: driftTransform(direction, zoom, p) }}
      />
    </AbsoluteFill>
  );
};
