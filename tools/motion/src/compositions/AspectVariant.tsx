import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { type Aspect } from "../dimensions";
import { type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";

/**
 * Re-aspect a still: the same picture as 16:9, 9:16 or 1:1 without redrawing it.
 * The same source, focal point and fit always give the same pixels.
 *
 * Two fit modes:
 *   cover        crop to fill the new aspect, anchored at `focal`.
 *   blur-extend  the whole picture over a blurred, enlarged copy of itself.
 *                Nothing is invented and nothing is cropped off.
 */

export type Focal =
  | "center" | "top" | "bottom" | "left" | "right"
  | "top-left" | "top-right" | "bottom-left" | "bottom-right";

export type AspectVariantProps = {
  /** The picture. */
  src: string;
  aspect?: Aspect;
  fit?: "cover" | "blur-extend";
  focal?: Focal;
  brand?: Partial<Brand>;
};

const OBJECT_POSITION: Record<Focal, string> = {
  center: "50% 50%",
  top: "50% 0%",
  bottom: "50% 100%",
  left: "0% 50%",
  right: "100% 50%",
  "top-left": "0% 0%",
  "top-right": "100% 0%",
  "bottom-left": "0% 100%",
  "bottom-right": "100% 100%",
};

export const AspectVariant: React.FC<AspectVariantProps> = ({ src, fit = "blur-extend", focal = "center", brand }) => {
  const b = resolveBrand(brand);
  const url = asset(src);

  if (fit === "cover") {
    return (
      <AbsoluteFill style={{ backgroundColor: b.surface }}>
        <Img
          src={url}
          style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: OBJECT_POSITION[focal] }}
        />
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      <Img
        src={url}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "blur(64px) saturate(1.15)",
          transform: "scale(1.2)",
        }}
      />
      <AbsoluteFill style={{ backgroundColor: "rgba(0,0,0,0.18)" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <Img src={url} style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
