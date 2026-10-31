import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { VERTICAL_UI_ZONE_PCT } from "./dimensions";
import type { Brand } from "./brand";

/** A caption line shown from `from` to `to`, in seconds. */
export type Cue = { from: number; to: number; text: string };

/** One spoken word with its timing in milliseconds, as a transcript gives it. */
export type Word = { text: string; startMs: number; endMs: number };

type Page = { startMs: number; endMs: number; words: Word[] };

/**
 * Group words into short pages of `perPage` words. A page also breaks at a
 * pause longer than 0.8 s, so a caption never hangs across a silence.
 */
export const pagesFromWords = (words: Word[], perPage = 4): Page[] => {
  const pages: Page[] = [];
  let current: Word[] = [];
  const flush = () => {
    if (!current.length) return;
    pages.push({ startMs: current[0].startMs, endMs: current[current.length - 1].endMs, words: current });
    current = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    if (current.length >= perPage || (prev && w.startMs - prev.endMs > 800)) flush();
    current.push(w);
  });
  flush();
  return pages;
};

/** Seconds of speech the captions cover, so a template can size itself to them. */
export const captionEndSeconds = (cues?: Cue[], words?: Word[]) => {
  const fromCues = (cues ?? []).reduce((n, c) => Math.max(n, c.to), 0);
  const fromWords = (words ?? []).reduce((n, w) => Math.max(n, w.endMs / 1000), 0);
  return Math.max(fromCues, fromWords);
};

/**
 * Burned-in captions on a plate, clear of the phone app's bottom band on a
 * vertical frame. With `words`, the word being spoken is drawn in the accent.
 * `offsetSeconds` shifts the timing, for a clip that starts after an intro.
 */
export const Captions: React.FC<{
  b: Brand;
  cues?: Cue[];
  words?: Word[];
  wordsPerPage?: number;
  offsetSeconds?: number;
}> = ({ b, cues, words, wordsPerPage = 4, offsetSeconds = 0 }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps - offsetSeconds;
  const ms = t * 1000;
  const pages = words && words.length ? pagesFromWords(words, wordsPerPage) : null;
  const page = pages?.find((p, i) => ms >= p.startMs && ms < (pages[i + 1]?.startMs ?? p.endMs + 400));
  const cue = pages ? undefined : (cues ?? []).find((c) => t >= c.from && t < c.to);
  if (!page && !cue) return null;

  const unit = Math.min(width, height);
  const bottom = height > width ? (height * VERTICAL_UI_ZONE_PCT) / 100 : height * 0.08;
  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "flex-end",
        flexDirection: "column",
        paddingBottom: bottom,
        paddingLeft: width * 0.08,
        paddingRight: width * 0.08,
      }}
    >
      <div
        style={{
          fontFamily: b.captionFont,
          color: b.captionText,
          backgroundColor: b.captionPlate,
          fontSize: unit * 0.055,
          fontWeight: 700,
          lineHeight: 1.25,
          textAlign: "center",
          textWrap: "balance",
          padding: `${unit * 0.018}px ${unit * 0.03}px`,
          borderRadius: unit * 0.018,
        }}
      >
        {page
          ? page.words.map((w, i) => (
              <span key={i} style={{ color: ms >= w.startMs && ms < w.endMs ? b.accent : b.captionText }}>
                {(i ? " " : "") + w.text.trim()}
              </span>
            ))
          : cue?.text}
      </div>
    </AbsoluteFill>
  );
};
