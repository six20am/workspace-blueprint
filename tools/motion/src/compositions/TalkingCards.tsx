import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FPS, toFrames } from "../dimensions";
import { type Brand, resolveBrand } from "../brand";
import { asset } from "../asset";
import { Captions, type Cue, type Word } from "../captions";

/**
 * Card video: one scene per point, cards that land one after another, an
 * optional crossed-out line ("not this"), an optional voiceover and captions.
 * Good for a tip, a how-it-works or a three-reasons video. Every time is in
 * seconds; a card's `at` counts from the start of its scene.
 */

export type CardItem = {
  label: string;
  sub?: string;
  /** Seconds into the scene when this card lands. */
  at?: number;
  tone?: "accent" | "warn" | "dim";
};

export type CardScene = {
  title: string;
  seconds: number;
  /** "hero" stacks big cards under a big title; "cards" lays them out in a grid. */
  layout?: "hero" | "cards";
  /** A line shown and then crossed out, before the title. */
  strike?: string;
  strikeAt?: number;
  items: CardItem[];
};

export type TalkingCardsProps = {
  scenes: CardScene[];
  /** Voiceover for the whole video. */
  audio?: string;
  /** Captions, timed from the start of the video. */
  cues?: Cue[];
  words?: Word[];
  brand?: Partial<Brand>;
};

const WARN = "#ff7a66";

/** Total length in frames. Shared with Root.tsx. */
export const cardsTotal = (p: TalkingCardsProps) =>
  Math.max(1, (p.scenes ?? []).reduce((n, s) => n + toFrames(s.seconds, 4), 0));

const useUnit = () => {
  const { width, height } = useVideoConfig();
  return Math.min(width, height) / 1080;
};

const useEnter = (atFrame: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - atFrame, fps, config: { damping: 18, stiffness: 150 } });
  return { opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 26}px)` };
};

const Card: React.FC<{ item: CardItem; big?: boolean; b: Brand }> = ({ item, big, b }) => {
  const u = useUnit();
  const style = useEnter(Math.round((item.at ?? 0) * FPS));
  const color = item.tone === "warn" ? WARN : item.tone === "dim" ? `${b.ink}99` : b.accent;
  return (
    <div
      style={{
        ...style,
        background: "rgba(255,255,255,0.07)",
        border: `${2 * u}px solid rgba(255,255,255,0.14)`,
        borderLeft: `${8 * u}px solid ${color}`,
        borderRadius: 18 * u,
        padding: big ? `${30 * u}px ${36 * u}px` : `${24 * u}px ${36 * u}px`,
        flex: big ? "0 0 auto" : "1 1 40%",
        minWidth: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      <div style={{ color: b.ink, fontFamily: b.headlineFont, fontSize: (big ? 54 : 48) * u, fontWeight: 700, lineHeight: 1.15 }}>
        {item.label}
      </div>
      {item.sub ? (
        <div style={{ color: `${b.ink}bb`, fontFamily: b.captionFont, fontSize: 34 * u, marginTop: 10 * u, lineHeight: 1.25 }}>
          {item.sub}
        </div>
      ) : null}
    </div>
  );
};

const Title: React.FC<{ text: string; size: number; b: Brand }> = ({ text, size, b }) => {
  const u = useUnit();
  const style = useEnter(0);
  return (
    <div style={{ ...style, color: b.ink, fontFamily: b.headlineFont, fontSize: size * u, fontWeight: 800, lineHeight: 1.1, textWrap: "balance" }}>
      {text}
    </div>
  );
};

const Strike: React.FC<{ text: string; atFrame: number; b: Brand }> = ({ text, atFrame, b }) => {
  const frame = useCurrentFrame();
  const u = useUnit();
  const width = interpolate(frame, [atFrame, atFrame + 14], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "relative", alignSelf: "flex-start", marginBottom: 30 * u }}>
      <span style={{ color: `${b.ink}99`, fontFamily: b.headlineFont, fontSize: 60 * u, fontWeight: 600 }}>{text}</span>
      <div style={{ position: "absolute", left: 0, top: "52%", height: 7 * u, width: `${width}%`, background: WARN, borderRadius: 4 }} />
    </div>
  );
};

/** Slow drifting glow, so a scene that holds on its cards never looks frozen. */
const Drift: React.FC<{ b: Brand }> = ({ b }) => {
  const frame = useCurrentFrame();
  const x = 50 + 42 * Math.sin(frame / 70);
  const y = 40 + 34 * Math.cos(frame / 95);
  return <AbsoluteFill style={{ background: `radial-gradient(60% 60% at ${x}% ${y}%, ${b.accent}4d, transparent 70%)` }} />;
};

const Breathe: React.FC<{ frames: number; children: React.ReactNode }> = ({ frames, children }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, frames], [1, 1.035]);
  return <AbsoluteFill style={{ transform: `scale(${scale})` }}>{children}</AbsoluteFill>;
};

const SceneView: React.FC<{ scene: CardScene; b: Brand }> = ({ scene, b }) => {
  const u = useUnit();
  const { width, height } = useVideoConfig();
  const side = (width > height ? 120 : 70) * u;
  const strike = scene.strike ? <Strike text={scene.strike} atFrame={Math.round((scene.strikeAt ?? 0) * FPS)} b={b} /> : null;
  if ((scene.layout ?? "cards") === "hero") {
    return (
      <AbsoluteFill style={{ padding: `0 ${side}px ${200 * u}px`, justifyContent: "center" }}>
        {strike}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 * u }}>
          {scene.title ? <Title text={scene.title} size={100} b={b} /> : null}
          {scene.items.map((item, i) => (
            <Card key={i} item={item} big b={b} />
          ))}
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ padding: `${height > width ? 320 * u : 84 * u}px ${side}px ${height > width ? 400 * u : 210 * u}px`, gap: 36 * u }}>
      {strike}
      <Title text={scene.title} size={70} b={b} />
      <div style={{ display: "flex", flexWrap: "wrap", gap: 24 * u, flex: 1, minHeight: 0, alignContent: "flex-start" }}>
        {scene.items.map((item, i) => (
          <Card key={i} item={item} b={b} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const TalkingCards: React.FC<TalkingCardsProps> = ({ audio, scenes, cues, words, brand }) => {
  const b = resolveBrand(brand);
  let from = 0;
  return (
    <AbsoluteFill style={{ background: b.surface, fontFamily: b.captionFont }}>
      <Drift b={b} />
      {audio ? <Audio src={asset(audio)} /> : null}
      {scenes.map((scene, i) => {
        const frames = toFrames(scene.seconds, 4);
        const at = from;
        from += frames;
        return (
          <Sequence key={i} from={at} durationInFrames={frames}>
            <Breathe frames={frames}>
              <SceneView scene={scene} b={b} />
            </Breathe>
          </Sequence>
        );
      })}
      <Captions b={b} cues={cues} words={words} />
    </AbsoluteFill>
  );
};
