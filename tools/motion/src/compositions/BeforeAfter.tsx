import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { type Brand, resolveBrand } from "../brand";
import { VERTICAL_UI_ZONE_PCT, toFrames } from "../dimensions";
import { asset } from "../asset";
import { type FontFile, useFonts } from "../fonts";
import { LogoBug, Outro, bedVolume } from "./BrandedClip";
import { WipeEdge } from "../effects/transitions";

/**
 * Before and after: the "before" holds, an accent line wipes across and
 * uncovers the "after", the "after" holds, then an optional outro card. For a
 * renovation, a cleanup, a makeover or a redesign: any two stills shot from
 * about the same spot. The wipe follows the awesome-ai-motion `wipe` recipe
 * (a moving edge with a thin line riding it), eased so the line lingers mid-frame.
 */

export type BeforeAfterProps = {
  before: string;
  after: string;
  beforeLabel?: string;
  afterLabel?: string;
  holdSeconds?: number;
  wipeSeconds?: number;
  afterSeconds?: number;
  outroSeconds?: number;
  logo?: string;
  name?: string;
  bug?: boolean;
  outroHeadline?: string;
  cta?: string;
  onAccent?: string;
  music?: string;
  musicVolume?: number;
  fonts?: FontFile[];
  brand?: Partial<Brand>;
};

/** Frame counts for the four parts. Shared with Root.tsx for the total length. */
export const beforeAfterParts = (p: BeforeAfterProps) => ({
  hold: toFrames(p.holdSeconds, 1.5),
  wipe: toFrames(p.wipeSeconds, 1.2),
  after: toFrames(p.afterSeconds, 2),
  outro: p.outroSeconds ? toFrames(p.outroSeconds, 0) : 0,
});

const Tag: React.FC<{ text: string; b: Brand; side: "left" | "right"; opacity: number }> = ({ text, b, side, opacity }) => {
  const { width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const top = height > width ? (height * VERTICAL_UI_ZONE_PCT) / 100 + unit * 0.02 : height * 0.06;
  return (
    <div
      style={{
        position: "absolute",
        top,
        [side]: width * 0.06,
        fontFamily: b.headlineFont,
        fontWeight: 800,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        fontSize: unit * 0.042,
        color: side === "left" ? b.captionText : b.surface,
        backgroundColor: side === "left" ? b.captionPlate : b.accent,
        padding: `${unit * 0.012}px ${unit * 0.026}px`,
        borderRadius: unit * 0.01,
        opacity,
      }}
    >
      {text}
    </div>
  );
};

export const BeforeAfter: React.FC<BeforeAfterProps> = (p) => {
  const b = resolveBrand(p.brand);
  useFonts(p.fonts);
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const parts = beforeAfterParts(p);
  const revealEnd = parts.hold + parts.wipe;
  const mainEnd = revealEnd + parts.after;
  const total = mainEnd + parts.outro;

  // 0 = all before, 1 = all after.
  const t = interpolate(frame, [parts.hold, revealEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // The edge sweeps right to left, so "after" grows from the side its tag sits on.
  const lineX = width * (1 - t);
  const push = interpolate(frame, [0, mainEnd], [1, 1.05], { extrapolateRight: "clamp" });
  const imgStyle: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    objectFit: "cover",
    transform: `scale(${push})`,
  };

  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      <Sequence durationInFrames={mainEnd} name="reveal">
        <AbsoluteFill>
          <Img src={asset(p.before)} style={imgStyle} />
          <AbsoluteFill style={{ clipPath: `inset(0 0 0 ${lineX}px)` }}>
            <Img src={asset(p.after)} style={imgStyle} />
          </AbsoluteFill>
          <WipeEdge p={t} dir="right" color={b.accent} />
          <Tag text={p.beforeLabel ?? "Before"} b={b} side="left" opacity={1 - t} />
          <Tag text={p.afterLabel ?? "After"} b={b} side="right" opacity={t} />
          {p.bug !== false && p.logo ? <LogoBug logo={p.logo} /> : null}
        </AbsoluteFill>
      </Sequence>
      {parts.outro > 0 ? (
        <Sequence from={mainEnd} durationInFrames={parts.outro} name="outro">
          <Outro
            logo={p.logo}
            b={b}
            name={p.name ?? ""}
            headline={p.outroHeadline}
            cta={p.cta}
            onAccent={p.onAccent ?? "#0b0b0b"}
          />
        </Sequence>
      ) : null}
      {p.music ? <Audio src={asset(p.music)} loop volume={bedVolume(p.musicVolume ?? 0.8, total, 20)} /> : null}
    </AbsoluteFill>
  );
};
