import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FPS, VERTICAL_UI_ZONE_PCT, toFrames } from "../dimensions";
import { type Brand, resolveBrand } from "../brand";
import { asset, isImage } from "../asset";
import { type FontFile, useFonts } from "../fonts";
import { Captions, type Cue, type Word } from "../captions";

/**
 * One branded clip: a logo intro, the footage, an outro card.
 *
 * The footage can be a phone video, a screen recording or a still; the
 * template does not care where it came from. The logo, colors and fonts arrive
 * in the props, so the same template serves any owner without code changes.
 * Optional: a logo bug in the corner, a lower-third name card, burned-in
 * captions, a music bed that fades in and out.
 *
 * Timeline:  [intro][footage][outro]
 * Caption and lower-third times count from the start of the footage.
 */

export type LowerThird = {
  name: string;
  title?: string;
  /** Seconds into the footage when the card appears. */
  at: number;
  /** Seconds the card stays. */
  seconds: number;
};

export type BrandedClipProps = {
  /** The footage: a video or a still picture. */
  src: string;
  /** "video" or "image". Worked out from the file name when left out. */
  kind?: "video" | "image";
  fit?: "cover" | "blur-extend";
  /** Seconds into the source video where the clip starts. */
  trimFrom?: number;
  introSeconds?: number;
  mainSeconds?: number;
  outroSeconds?: number;
  /** The owner's logo. */
  logo?: string;
  /** Shown instead of a logo when there is none. */
  name?: string;
  /** Small logo in the corner during the footage. */
  bug?: boolean;
  cues?: Cue[];
  words?: Word[];
  lowerThird?: LowerThird;
  outroHeadline?: string;
  cta?: string;
  /** Text color on the accent-colored button. */
  onAccent?: string;
  /** Music bed over the whole clip, faded in and out. */
  music?: string;
  musicVolume?: number;
  /** Volume of the footage's own sound. 0 mutes it. */
  sourceVolume?: number;
  fonts?: FontFile[];
  brand?: Partial<Brand>;
};

/** Frame counts for the three parts. Shared with Root.tsx for the total length. */
export const clipParts = (p: BrandedClipProps) => ({
  intro: p.introSeconds === 0 ? 0 : toFrames(p.introSeconds, 0.8),
  main: toFrames(p.mainSeconds, 6),
  outro: p.outroSeconds === 0 ? 0 : toFrames(p.outroSeconds, 2.5),
});

const Footage: React.FC<{
  src: string;
  kind: "video" | "image";
  fit: "cover" | "blur-extend";
  trimFrom: number;
  mainFrames: number;
  volume: number;
}> = ({ src, kind, fit, trimFrom, mainFrames, volume }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const file = asset(src);
  // A still gets a slow push so the frame is never dead.
  const push = kind === "image" ? interpolate(frame, [0, mainFrames], [1, 1.06], { extrapolateRight: "clamp" }) : 1;
  const layer = (objectFit: "cover" | "contain", muted: boolean) =>
    kind === "video" ? (
      <OffthreadVideo
        src={file}
        startFrom={Math.round(trimFrom * fps)}
        muted={muted}
        volume={muted ? 0 : volume}
        style={{ width: "100%", height: "100%", objectFit }}
      />
    ) : (
      <Img src={file} style={{ width: "100%", height: "100%", objectFit, transform: `scale(${push})` }} />
    );

  if (fit === "cover") return <AbsoluteFill>{layer("cover", false)}</AbsoluteFill>;
  // blur-extend: the footage, blurred, fills the frame; the whole shot sits on top.
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ filter: "blur(40px) brightness(0.55)", transform: "scale(1.15)" }}>
        {layer("cover", true)}
      </AbsoluteFill>
      <AbsoluteFill>{layer("contain", false)}</AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Intro: React.FC<{ logo?: string; b: Brand; name: string; frames: number }> = ({ logo, b, name, frames }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const pop = spring({ frame, fps, config: { damping: 14, stiffness: 160 } });
  const wipe = interpolate(frame, [4, Math.max(5, frames - 6)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [frames - 5, frames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface, alignItems: "center", justifyContent: "center", opacity: fadeOut }}>
      {logo ? (
        <Img
          src={asset(logo)}
          style={{ width: unit * 0.6, maxHeight: unit * 0.5, objectFit: "contain", opacity: pop, transform: `scale(${0.92 + pop * 0.08})` }}
        />
      ) : (
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.ink, fontSize: unit * 0.1, opacity: pop }}>
          {name}
        </div>
      )}
      <div
        style={{
          marginTop: unit * 0.03,
          height: Math.max(3, unit * 0.006),
          width: unit * 0.5 * wipe,
          backgroundColor: b.accent,
          borderRadius: 99,
        }}
      />
    </AbsoluteFill>
  );
};

export const Outro: React.FC<{
  logo?: string;
  b: Brand;
  name: string;
  headline?: string;
  cta?: string;
  onAccent: string;
}> = ({ logo, b, name, headline, cta, onAccent }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const rise = spring({ frame: frame - 4, fps, config: { damping: 16 } });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: b.surface,
        backgroundImage: `radial-gradient(ellipse at 50% 38%, ${b.accent}33 0%, transparent 60%)`,
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: unit * 0.05,
        padding: width * 0.1,
        opacity: fadeIn,
      }}
    >
      {logo ? (
        <Img src={asset(logo)} style={{ width: unit * 0.5, maxHeight: unit * 0.4, objectFit: "contain" }} />
      ) : (
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.ink, fontSize: unit * 0.09 }}>{name}</div>
      )}
      {headline ? (
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 700,
            color: b.ink,
            fontSize: unit * 0.065,
            lineHeight: 1.15,
            textAlign: "center",
            textWrap: "balance",
            transform: `translateY(${(1 - rise) * unit * 0.03}px)`,
            opacity: rise,
          }}
        >
          {headline}
        </div>
      ) : null}
      {cta ? (
        <div
          style={{
            fontFamily: b.captionFont,
            fontWeight: 700,
            color: onAccent,
            backgroundColor: b.accent,
            fontSize: unit * 0.045,
            padding: `${unit * 0.022}px ${unit * 0.05}px`,
            borderRadius: 999,
            opacity: rise,
            transform: `scale(${0.94 + rise * 0.06})`,
          }}
        >
          {cta}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** The lower-third name card: slides in from the left, holds, fades out. */
const LowerThirdCard: React.FC<{ b: Brand; card: LowerThird }> = ({ b, card }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const isVertical = height > width;
  const span = toFrames(card.seconds, 3);
  const inn = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const out = interpolate(frame, [span - 8, span], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const show = Math.min(inn, out);
  const bottom = (isVertical ? (height * VERTICAL_UI_ZONE_PCT) / 100 : height * 0.08) + unit * (isVertical ? 0.28 : 0.2);
  return (
    <div
      style={{
        position: "absolute",
        left: width * 0.07,
        bottom,
        display: "flex",
        gap: unit * 0.02,
        opacity: show,
        transform: `translateX(${(1 - show) * -unit * 0.05}px)`,
      }}
    >
      <div style={{ width: Math.max(4, unit * 0.008), backgroundColor: b.accent, borderRadius: 99 }} />
      <div style={{ backgroundColor: b.captionPlate, padding: `${unit * 0.016}px ${unit * 0.028}px`, borderRadius: unit * 0.012 }}>
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.captionText, fontSize: unit * 0.048 }}>
          {card.name}
        </div>
        {card.title ? (
          <div style={{ fontFamily: b.captionFont, fontWeight: 600, color: b.accent, fontSize: unit * 0.032 }}>
            {card.title}
          </div>
        ) : null}
      </div>
    </div>
  );
};

/** A small logo in the top corner, clear of the phone app's top band. */
export const LogoBug: React.FC<{ logo: string }> = ({ logo }) => {
  const { width, height } = useVideoConfig();
  const unit = Math.min(width, height);
  const isVertical = height > width;
  return (
    <Img
      src={asset(logo)}
      style={{
        position: "absolute",
        right: width * 0.05,
        top: isVertical ? (height * VERTICAL_UI_ZONE_PCT) / 100 * 0.75 : height * 0.05,
        width: unit * 0.2,
        maxHeight: unit * 0.12,
        objectFit: "contain",
        opacity: 0.9,
      }}
    />
  );
};

/** Music volume curve: fades in over `fade` frames and out over the last `fade`. */
export const bedVolume = (volume: number, total: number, fade: number) => (f: number) =>
  volume *
  Math.min(
    interpolate(f, [0, fade], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    interpolate(f, [total - fade, total - 1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  );

export const BrandedClip: React.FC<BrandedClipProps> = (p) => {
  const b = resolveBrand(p.brand);
  useFonts(p.fonts);
  const { intro, main, outro } = clipParts(p);
  const total = intro + main + outro;
  const kind = p.kind ?? (isImage(p.src) ? "image" : "video");
  const name = p.name ?? "";
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      {intro > 0 ? (
        <Sequence durationInFrames={intro} name="intro">
          <Intro logo={p.logo} b={b} name={name} frames={intro} />
        </Sequence>
      ) : null}
      <Sequence from={intro} durationInFrames={main} name="footage">
        <Footage
          src={p.src}
          kind={kind}
          fit={p.fit ?? "cover"}
          trimFrom={p.trimFrom ?? 0}
          mainFrames={main}
          volume={p.sourceVolume ?? 1}
        />
        {p.bug !== false && p.logo ? <LogoBug logo={p.logo} /> : null}
        {p.lowerThird ? (
          <Sequence from={Math.round(p.lowerThird.at * FPS)} durationInFrames={toFrames(p.lowerThird.seconds, 3)} layout="none">
            <LowerThirdCard b={b} card={p.lowerThird} />
          </Sequence>
        ) : null}
        <Captions b={b} cues={p.cues} words={p.words} />
      </Sequence>
      {outro > 0 ? (
        <Sequence from={intro + main} durationInFrames={outro} name="outro">
          <Outro logo={p.logo} b={b} name={name} headline={p.outroHeadline} cta={p.cta} onAccent={p.onAccent ?? "#0b0b0b"} />
        </Sequence>
      ) : null}
      {p.music ? <Audio src={asset(p.music)} loop volume={bedVolume(p.musicVolume ?? 0.8, total, 45)} /> : null}
    </AbsoluteFill>
  );
};
