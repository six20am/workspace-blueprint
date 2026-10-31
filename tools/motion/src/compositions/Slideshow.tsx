import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { FPS, SAFE_ZONE_INSET_PCT, VERTICAL_UI_ZONE_PCT, toFrames } from "../dimensions";
import { type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";
import { driftTransform, smoothProgress } from "./KenBurns";
import { bedVolume } from "./BrandedClip";
import { SceneTransition, transitionFrames, type Direction, type TransitionKind } from "../effects/transitions";

/**
 * Photo slideshow: each still gets its own slow zoom or pan, joined by a fade,
 * slide, wipe or push (the recipes in ../effects/transitions.tsx), under
 * optional text cards and a music bed that fades in and out.
 */

export type SlideDirection = "in" | "out" | "left" | "right" | "up" | "down" | "none";

export type Slide = {
  src: string;
  /** Drift for this photo. Alternates in and out when left out. */
  direction?: SlideDirection;
};

export type TextCard = {
  text: string;
  eyebrow?: string;
  /** Seconds from the start of the video. */
  at: number;
  seconds: number;
  align?: "top" | "center" | "bottom";
  /** Darkening behind the words. 0 to 1. */
  scrim?: number;
};

export type SlideshowProps = {
  slides: Slide[];
  /** Seconds each photo is fully on screen. */
  secondsPerSlide?: number;
  transition?: TransitionKind;
  /** Edge a slide, wipe or push arrives from. */
  transitionFrom?: Direction;
  /** Overrides the recipe length (fade and slide 0.6 s, wipe and push 1.2 s). */
  transitionSeconds?: number;
  /** Peak zoom. 1.08 is an 8% push across a photo. */
  zoom?: number;
  cards?: TextCard[];
  music?: string;
  musicVolume?: number;
  brand?: Partial<Brand>;
};

/**
 * Slide i owns [i * hold, (i + 1) * hold). The next slide mounts `t` frames
 * early and plays its entrance over the tail of this one. Shared with Root.tsx.
 */
export const slideTimeline = (p: SlideshowProps) => {
  const hold = toFrames(p.secondsPerSlide, 3);
  const kind = p.transition ?? "fade";
  const t = Math.min(transitionFrames(kind, FPS, p.transitionSeconds), Math.floor(hold / 2));
  const slides = (p.slides ?? []).map((s, i) => ({
    ...s,
    from: i * hold,
    span: hold,
    enter: i === 0 ? 0 : t,
    exit: i < p.slides.length - 1 ? t : 0,
  }));
  return { slides, kind, total: Math.max(1, slides.length * hold) };
};

const Photo: React.FC<{ src: string; direction: SlideDirection; zoom: number; span: number }> = ({
  src,
  direction,
  zoom,
  span,
}) => {
  const frame = useCurrentFrame();
  return (
    <Img
      src={asset(src)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        transform: driftTransform(direction, zoom, smoothProgress(frame, span)),
      }}
    />
  );
};

/** A hook or end card over the photos, inside the safe zone. Same type as CoverFrame. */
const Card: React.FC<{ card: TextCard; b: Brand; span: number }> = ({ card, b, span }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const inset = (unit * SAFE_ZONE_INSET_PCT) / 100;
  const uiZone = height > width ? (height * VERTICAL_UI_ZONE_PCT) / 100 : inset;
  const fade = 12;
  const opacity = Math.min(
    interpolate(frame, [0, fade], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    interpolate(frame, [span - fade, span], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  );
  const align = card.align ?? "center";
  const scrim = card.scrim ?? 0.5;
  const scrimGradient =
    align === "top"
      ? `linear-gradient(180deg, rgba(0,0,0,${scrim}) 0%, rgba(0,0,0,${scrim * 0.15}) 60%)`
      : align === "bottom"
        ? `linear-gradient(0deg, rgba(0,0,0,${scrim}) 0%, rgba(0,0,0,${scrim * 0.15}) 60%)`
        : `radial-gradient(ellipse at center, rgba(0,0,0,${scrim}) 0%, rgba(0,0,0,${scrim * 0.35}) 100%)`;
  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ background: scrimGradient }} />
      <AbsoluteFill
        style={{
          padding: `${uiZone}px ${inset}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: align === "top" ? "flex-start" : align === "bottom" ? "flex-end" : "center",
          alignItems: "center",
        }}
      >
        {card.eyebrow ? (
          <div
            style={{
              fontFamily: b.captionFont,
              color: b.eyebrowText ?? b.accent,
              fontSize: unit * 0.032,
              fontWeight: 700,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              textAlign: "center",
              marginBottom: unit * 0.022,
            }}
          >
            {card.eyebrow}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: b.headlineFont,
            color: "#ffffff",
            fontSize: unit * 0.098,
            lineHeight: 1.04,
            fontWeight: 800,
            letterSpacing: "-0.025em",
            textAlign: "center",
            textWrap: "balance",
            textShadow: "0 4px 32px rgba(0,0,0,0.45)",
          }}
        >
          {card.text}
        </div>
        <div style={{ marginTop: unit * 0.032, width: unit * 0.2, height: unit * 0.011, backgroundColor: b.accent, borderRadius: 999 }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Slideshow: React.FC<SlideshowProps> = (p) => {
  const b = resolveBrand(p.brand);
  const { slides, kind, total } = slideTimeline(p);
  const zoom = p.zoom ?? 1.08;
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      {slides.map((s, i) => (
        <Sequence key={`slide-${i}`} from={s.from - s.enter} durationInFrames={s.span + s.enter}>
          <SceneTransition
            kind={kind}
            dir={p.transitionFrom ?? "right"}
            enterFrames={s.enter}
            exitFrames={s.exit}
            span={s.span + s.enter}
            accent={b.accent}
          >
            <Photo src={s.src} direction={s.direction ?? (i % 2 ? "out" : "in")} zoom={zoom} span={s.span + s.enter} />
          </SceneTransition>
        </Sequence>
      ))}
      {(p.cards ?? []).map((card, i) => {
        const span = toFrames(card.seconds, 2);
        return (
          <Sequence key={`card-${i}`} from={Math.round(card.at * FPS)} durationInFrames={span}>
            <Card card={card} b={b} span={span} />
          </Sequence>
        );
      })}
      {p.music ? <Audio src={asset(p.music)} loop volume={bedVolume(p.musicVolume ?? 0.8, total, 45)} /> : null}
    </AbsoluteFill>
  );
};
