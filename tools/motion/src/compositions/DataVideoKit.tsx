import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { VERTICAL_UI_ZONE_PCT, toFrames } from "../dimensions";
import { type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";
import { type FontFile, useFonts } from "../fonts";

/**
 * Numbers video from a small table: a logo sting, then each row as a bar that
 * grows while its number counts up, one row after another, then an end card.
 * The kit parts below (backdrop, sting, end card, label, button, timeline) are
 * exported so a new data template can reuse them. Every number and word comes
 * from the props; nothing here holds copy.
 */

export type Row = {
  label: string;
  value: number;
  /** Shown before the number, for example "$". */
  prefix?: string;
  /** Shown after the number, for example "%" or " jobs". */
  suffix?: string;
};

export type DataVideoProps = {
  title: string;
  eyebrow?: string;
  rows: Row[];
  /** A line under the bars, for example where the numbers come from. */
  note?: string;
  logo?: string;
  name?: string;
  outroHeadline?: string;
  cta?: string;
  onAccent?: string;
  /** Decimal places on the numbers. */
  decimals?: number;
  introSeconds?: number;
  /** Seconds between one row landing and the next. */
  secondsPerRow?: number;
  /** Seconds the full table holds before the end card. */
  holdSeconds?: number;
  outroSeconds?: number;
  music?: string;
  fonts?: FontFile[];
  brand?: Partial<Brand>;
};

export type Scene = { id: string; frames: number };

/** Scene list and lengths. Shared with Root.tsx for the total length. */
export const dataScenes = (p: DataVideoProps): Scene[] => {
  const rows = p.rows ?? [];
  const scenes: Scene[] = [];
  if ((p.logo || p.name) && p.introSeconds !== 0) scenes.push({ id: "sting", frames: toFrames(p.introSeconds, 1) });
  scenes.push({
    id: "table",
    frames: toFrames(0.6 + rows.length * (p.secondsPerRow ?? 0.8) + (p.holdSeconds ?? 2.5), 4),
  });
  if ((p.outroHeadline || p.cta || p.logo || p.name) && p.outroSeconds !== 0) {
    scenes.push({ id: "end", frames: toFrames(p.outroSeconds, 2.5) });
  }
  return scenes;
};

export const totalFrames = (scenes: Scene[]) => Math.max(1, scenes.reduce((n, s) => n + s.frames, 0));

export const useFrameBox = () => {
  const { width, height, fps } = useVideoConfig();
  const unit = Math.min(width, height);
  const isVertical = height > width;
  const uiZone = isVertical ? (height * VERTICAL_UI_ZONE_PCT) / 100 : height * 0.06;
  return { width, height, fps, unit, isVertical, uiZone };
};

export const useRise = (delay = 0, damping = 16) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping } });
};

/** Surface with a slow drifting accent glow, so a type-only frame is never dead. */
export const Backdrop: React.FC<{ b: Brand }> = ({ b }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = frame / Math.max(1, durationInFrames);
  const x = 30 + 40 * t;
  const y = 30 + 10 * Math.sin(t * Math.PI * 2);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: b.surface,
        backgroundImage: [
          `radial-gradient(ellipse at ${x}% ${y}%, ${b.accent}2e 0%, transparent 55%)`,
          `radial-gradient(ellipse at ${100 - x}% ${100 - y}%, ${b.accent}14 0%, transparent 50%)`,
        ].join(", "),
      }}
    />
  );
};

export const LogoSting: React.FC<{ b: Brand; logo?: string; name: string; frames: number }> = ({ b, logo, name, frames }) => {
  const frame = useCurrentFrame();
  const { unit } = useFrameBox();
  const pop = useRise(0, 14);
  const wipe = interpolate(frame, [4, Math.max(5, frames - 6)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const out = interpolate(frame, [frames - 5, frames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface, alignItems: "center", justifyContent: "center", opacity: out }}>
      {logo ? (
        <Img src={asset(logo)} style={{ width: unit * 0.6, maxHeight: unit * 0.5, objectFit: "contain", opacity: pop, transform: `scale(${0.92 + pop * 0.08})` }} />
      ) : (
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.ink, fontSize: unit * 0.1, opacity: pop }}>{name}</div>
      )}
      <div style={{ marginTop: unit * 0.03, height: Math.max(3, unit * 0.006), width: unit * 0.5 * wipe, backgroundColor: b.accent, borderRadius: 99 }} />
    </AbsoluteFill>
  );
};

export const Pill: React.FC<{ b: Brand; onAccent: string; text: string; size: number; style?: React.CSSProperties }> = ({
  b,
  onAccent,
  text,
  size,
  style,
}) => {
  const { unit } = useFrameBox();
  return (
    <div
      style={{
        fontFamily: b.captionFont,
        fontWeight: 700,
        color: onAccent,
        backgroundColor: b.accent,
        fontSize: unit * size,
        padding: `${unit * size * 0.5}px ${unit * size * 1.1}px`,
        borderRadius: 999,
        textAlign: "center",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

export const Eyebrow: React.FC<{ b: Brand; text: string; size?: number; style?: React.CSSProperties }> = ({
  b,
  text,
  size = 0.034,
  style,
}) => {
  const { unit } = useFrameBox();
  return (
    <div
      style={{
        fontFamily: b.captionFont,
        fontWeight: 700,
        color: b.eyebrowText ?? b.accent,
        fontSize: unit * size,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

export const EndCard: React.FC<{
  b: Brand;
  logo?: string;
  name: string;
  headline?: string;
  cta?: string;
  onAccent: string;
}> = ({ b, logo, name, headline, cta, onAccent }) => {
  const frame = useCurrentFrame();
  const { unit, width } = useFrameBox();
  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const rise = useRise(4);
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
      ) : name ? (
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.ink, fontSize: unit * 0.09 }}>{name}</div>
      ) : null}
      {headline ? (
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 700,
            color: b.ink,
            fontSize: unit * 0.062,
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
      {cta ? <Pill b={b} onAccent={onAccent} text={cta} size={0.045} style={{ opacity: rise, transform: `scale(${0.94 + rise * 0.06})` }} /> : null}
    </AbsoluteFill>
  );
};

/** Plays scenes in order; `render` draws each one. */
export const Timeline: React.FC<{ scenes: Scene[]; render: (scene: Scene, index: number) => React.ReactNode }> = ({
  scenes,
  render,
}) => {
  let from = 0;
  return (
    <>
      {scenes.map((s, i) => {
        const at = from;
        from += s.frames;
        return (
          <Sequence key={s.id} from={at} durationInFrames={s.frames} name={s.id}>
            {render(s, i)}
          </Sequence>
        );
      })}
    </>
  );
};

const format = (n: number, decimals: number) =>
  n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

/** The table scene: title, then one bar per row that grows while its number counts up. */
const Table: React.FC<{ p: DataVideoProps; b: Brand; onAccent: string }> = ({ p, b }) => {
  const frame = useCurrentFrame();
  const { unit, width, isVertical, uiZone, fps } = useFrameBox();
  const rows = p.rows ?? [];
  const max = Math.max(1, ...rows.map((r) => Math.abs(r.value)));
  const step = Math.round((p.secondsPerRow ?? 0.8) * fps);
  const first = Math.round(0.6 * fps);
  const titleRise = useRise(0);
  const pad = isVertical ? width * 0.08 : width * 0.1;
  return (
    <AbsoluteFill style={{ padding: `${uiZone + unit * 0.04}px ${pad}px`, justifyContent: "center", gap: unit * 0.035 }}>
      <div style={{ opacity: titleRise, transform: `translateY(${(1 - titleRise) * unit * 0.03}px)` }}>
        {p.eyebrow ? <Eyebrow b={b} text={p.eyebrow} style={{ marginBottom: unit * 0.015 }} /> : null}
        <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.ink, fontSize: unit * 0.075, lineHeight: 1.08, textWrap: "balance" }}>
          {p.title}
        </div>
      </div>
      {rows.map((r, i) => {
        const start = first + i * step;
        const grow = interpolate(frame, [start, start + Math.round(fps * 0.9)], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: (t) => 1 - Math.pow(1 - t, 3),
        });
        const show = interpolate(frame, [start, start + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={i} style={{ opacity: show }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: unit * 0.02 }}>
              <div style={{ fontFamily: b.captionFont, fontWeight: 600, color: b.ink, fontSize: unit * 0.04 }}>{r.label}</div>
              <div style={{ fontFamily: b.headlineFont, fontWeight: 800, color: b.accent, fontSize: unit * 0.05, fontVariantNumeric: "tabular-nums" }}>
                {(r.prefix ?? "") + format(r.value * grow, p.decimals ?? 0) + (r.suffix ?? "")}
              </div>
            </div>
            <div style={{ marginTop: unit * 0.01, height: unit * 0.026, borderRadius: 999, background: "rgba(255,255,255,0.09)" }}>
              <div
                style={{
                  height: "100%",
                  width: `${(Math.abs(r.value) / max) * 100 * grow}%`,
                  borderRadius: 999,
                  backgroundColor: b.accent,
                }}
              />
            </div>
          </div>
        );
      })}
      {p.note ? (
        <div style={{ fontFamily: b.captionFont, color: `${b.ink}99`, fontSize: unit * 0.028, marginTop: unit * 0.01 }}>{p.note}</div>
      ) : null}
    </AbsoluteFill>
  );
};

export const DataVideo: React.FC<DataVideoProps> = (p) => {
  const b = resolveBrand(p.brand);
  useFonts(p.fonts);
  const scenes = dataScenes(p);
  const onAccent = p.onAccent ?? "#0b0b0b";
  return (
    <AbsoluteFill>
      <Backdrop b={b} />
      <Timeline
        scenes={scenes}
        render={(s) =>
          s.id === "sting" ? (
            <LogoSting b={b} logo={p.logo} name={p.name ?? ""} frames={s.frames} />
          ) : s.id === "table" ? (
            <Table p={p} b={b} onAccent={onAccent} />
          ) : (
            <EndCard b={b} logo={p.logo} name={p.name ?? ""} headline={p.outroHeadline} cta={p.cta} onAccent={onAccent} />
          )
        }
      />
      {p.music ? <Audio src={asset(p.music)} loop volume={0.7} /> : null}
    </AbsoluteFill>
  );
};
