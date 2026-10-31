import React from "react";
import { Composition } from "remotion";
import { AspectVariant } from "./compositions/AspectVariant";
import { BeforeAfter, beforeAfterParts, type BeforeAfterProps } from "./compositions/BeforeAfter";
import { BrandedClip, clipParts, type BrandedClipProps } from "./compositions/BrandedClip";
import { CaptionBurn, type CaptionBurnProps } from "./compositions/CaptionBurn";
import { CoverFrame } from "./compositions/CoverFrame";
import { DataVideo, dataScenes, totalFrames, type DataVideoProps } from "./compositions/DataVideoKit";
import { ImagePost } from "./compositions/ImagePost";
import { KenBurns } from "./compositions/KenBurns";
import { Slideshow, slideTimeline, type SlideshowProps } from "./compositions/Slideshow";
import { TalkingCards, cardsTotal, type TalkingCardsProps } from "./compositions/TalkingCards";
import { captionEndSeconds } from "./captions";
import { type Aspect, FPS, dimensionsFor, toFrames } from "./dimensions";

/**
 * The ten templates. Size comes from the `aspect` prop and length from each
 * template's own props, so one template serves 16:9, 9:16 and 1:1 alike.
 * render.mjs always passes the props; the defaults below only matter in
 * Remotion Studio (`npm run studio`).
 */

type AnyProps = Record<string, unknown> & { aspect?: string; seconds?: number };

// Remotion wants each template typed loosely here; every template checks its own props.
const loose = (c: unknown) => c as React.FC<Record<string, unknown>>;

const make = (
  id: string,
  component: unknown,
  defaultAspect: Aspect,
  frames: (p: AnyProps) => number,
  defaultProps: Record<string, unknown> = {},
) => (
  <Composition
    id={id}
    component={loose(component)}
    durationInFrames={1}
    fps={FPS}
    width={1920}
    height={1080}
    defaultProps={defaultProps}
    calculateMetadata={({ props }) => {
      const p = props as AnyProps;
      const { width, height } = dimensionsFor(p.aspect, defaultAspect);
      return { width, height, fps: FPS, durationInFrames: Math.max(1, frames(p)) };
    }}
  />
);

export const RemotionRoot: React.FC = () => (
  <>
    {make("AspectVariant", AspectVariant, "9:16", () => 1, { src: "", fit: "blur-extend" })}
    {make("BeforeAfter", BeforeAfter, "9:16", (p) => {
      const parts = beforeAfterParts(p as unknown as BeforeAfterProps);
      return parts.hold + parts.wipe + parts.after + parts.outro;
    }, { before: "", after: "" })}
    {make("BrandedClip", BrandedClip, "9:16", (p) => {
      const parts = clipParts(p as unknown as BrandedClipProps);
      return parts.intro + parts.main + parts.outro;
    }, { src: "", name: "Example Co" })}
    {make("CaptionBurn", CaptionBurn, "9:16", (p) => {
      const c = p as unknown as CaptionBurnProps;
      const end = captionEndSeconds(c.cues, c.words);
      return toFrames(c.seconds, end > 0 ? end + 0.5 : 10);
    }, { src: "", words: [] })}
    {make("CoverFrame", CoverFrame, "16:9", (p) => toFrames(p.seconds, 5), { headline: "Your headline here" })}
    {make("DataVideo", DataVideo, "9:16", (p) => totalFrames(dataScenes(p as unknown as DataVideoProps)), {
      title: "Example numbers",
      rows: [{ label: "First", value: 40 }, { label: "Second", value: 75 }],
    })}
    {make("ImagePost", ImagePost, "4:5", () => 1, { layout: "slide-text", images: [], text: { headline: "Layout preview" } })}
    {make("KenBurns", KenBurns, "9:16", (p) => toFrames(p.seconds, 5), { src: "" })}
    {make("Slideshow", Slideshow, "9:16", (p) => slideTimeline(p as unknown as SlideshowProps).total, { slides: [] })}
    {make("TalkingCards", TalkingCards, "16:9", (p) => cardsTotal(p as unknown as TalkingCardsProps), {
      scenes: [{ title: "Your point here", seconds: 4, items: [{ label: "A card", at: 0.5 }] }],
    })}
  </>
);
