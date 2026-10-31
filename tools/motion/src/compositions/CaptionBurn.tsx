import React from "react";
import { AbsoluteFill, Img, OffthreadVideo } from "remotion";
import { type Brand, resolveBrand } from "../brand";
import { asset, isImage } from "../asset";
import { Captions, type Cue, type Word } from "../captions";

/**
 * Burn captions into a video, so they survive muted autoplay.
 *
 * Timing comes from a transcript: `words` (each word with start and end in
 * milliseconds, the spoken word lit in the accent) or `cues` (whole lines with
 * from and to in seconds). The `video-watcher` skill makes a timed transcript.
 * A still picture works as the background too.
 */

export type CaptionBurnProps = {
  /** The video (or a still picture) the captions go over. */
  src: string;
  cues?: Cue[];
  words?: Word[];
  /** Words shown at once in word mode. */
  wordsPerPage?: number;
  /** Length. Defaults to the end of the last caption plus half a second. */
  seconds?: number;
  brand?: Partial<Brand>;
};

export const CaptionBurn: React.FC<CaptionBurnProps> = ({ src, cues, words, wordsPerPage, brand }) => {
  const b = resolveBrand(brand);
  const style = { width: "100%", height: "100%", objectFit: "cover" as const };
  return (
    <AbsoluteFill style={{ backgroundColor: b.surface }}>
      {isImage(src) ? <Img src={asset(src)} style={style} /> : <OffthreadVideo src={asset(src)} style={style} />}
      <Captions b={b} cues={cues} words={words} wordsPerPage={wordsPerPage} />
    </AbsoluteFill>
  );
};
