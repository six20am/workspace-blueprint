import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SAFE_ZONE_INSET_PCT, VERTICAL_UI_ZONE_PCT } from "../dimensions";
import { fade, type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";
import { useEntrance } from "../effects/transitions";

/**
 * Title card: a headline, an optional label above it (a date, a series name),
 * an optional photo behind it and the owner's logo. As a video the label,
 * headline and accent rule rise in one after another, then hold. As a still
 * (a .png or .jpg out file) render.mjs captures the settled last frame, which
 * makes it a cover or thumbnail.
 *
 * Vary the photo, the words and the accent, not the layout. Type is sized off
 * the short edge so a 1:1 and a 16:9 of the same headline read the same.
 */

/** Bottom band a vertical card's type block clears, in percent of frame height. */
const COVER_VERTICAL_BOTTOM_PCT = 22;

export type CoverFrameProps = {
  headline: string;
  /** Small label above the headline, for example a date. */
  eyebrow?: string;
  /** Background picture. Leave it out for a type-only card. */
  src?: string;
  /** The owner's logo, top left. */
  logo?: string;
  /** Darkening over the photo so the words stay readable. 0 to 1. */
  scrim?: number;
  /** Length as a video. */
  seconds?: number;
  brand?: Partial<Brand>;
};

export const CoverFrame: React.FC<CoverFrameProps> = ({ src, headline, eyebrow, logo, scrim = 0.65, brand }) => {
  const b = resolveBrand(brand);
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const unit = Math.min(width, height);
  const inset = (unit * SAFE_ZONE_INSET_PCT) / 100;
  const isVertical = height > width;
  // A vertical frame's top and bottom bands are covered by the phone app, so the type clears them.
  const bottomInset = isVertical
    ? Math.max(inset, (height * Math.max(VERTICAL_UI_ZONE_PCT, COVER_VERTICAL_BOTTOM_PCT)) / 100)
    : inset;
  const topInset = isVertical ? Math.max(inset, (height * VERTICAL_UI_ZONE_PCT) / 100) : inset;

  const eyebrowIn = useEntrance("slide", 4, unit * 0.03);
  const headlineIn = useEntrance("slide", 10, unit * 0.04);
  const logoIn = useEntrance("fade", 0);
  const rule = interpolate(frame, [18, 36], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // A slow push keeps a held card from reading as a frozen picture.
  const push = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [1, 1.05]);

  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      {src ? (
        <Img
          src={asset(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${push})` }}
        />
      ) : (
        <AbsoluteFill
          style={{ backgroundImage: `radial-gradient(ellipse at 30% 30%, ${fade(b.accent, 0.2)} 0%, transparent 60%)` }}
        />
      )}

      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(0,0,0,${scrim * 0.55}) 0%, rgba(0,0,0,${scrim * 0.2}) 45%, rgba(0,0,0,${scrim}) 100%)`,
        }}
      />

      {logo ? (
        <Img
          src={asset(logo)}
          style={{
            position: "absolute",
            top: topInset,
            left: inset,
            height: unit * 0.12,
            maxWidth: unit * 0.4,
            objectFit: "contain",
            ...logoIn,
          }}
        />
      ) : null}

      <AbsoluteFill
        style={{
          padding: `${topInset}px ${inset}px ${bottomInset}px ${inset}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          alignItems: "flex-start",
        }}
      >
        {eyebrow ? (
          <div
            style={{
              fontFamily: b.captionFont,
              color: b.eyebrowText ?? b.accent,
              fontSize: unit * 0.032 * (b.eyebrowScale ?? 1),
              fontWeight: 700,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              marginBottom: unit * 0.018,
              ...eyebrowIn,
            }}
          >
            {eyebrow}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: b.headlineFont,
            color: "#ffffff",
            fontSize: unit * 0.115,
            lineHeight: 1.02,
            fontWeight: 800,
            letterSpacing: "-0.025em",
            textWrap: "balance",
            textShadow: "0 4px 32px rgba(0,0,0,0.45)",
            ...headlineIn,
          }}
        >
          {headline}
        </div>
        <div
          style={{
            marginTop: unit * 0.032,
            width: unit * 0.2 * rule,
            height: unit * 0.011,
            backgroundColor: b.accent,
            borderRadius: 999,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
