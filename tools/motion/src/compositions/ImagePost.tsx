import React from "react";
import { AbsoluteFill, Img, cancelRender, useVideoConfig } from "remotion";
import { darken, fade, resolveBrand, type Brand } from "../brand";
import { asset } from "../asset";
import { type FontFile, useFonts } from "../fonts";

/**
 * ImagePost: one still for a social image format.
 *
 * The pictures come in with no words in them; every word, box, frame and label
 * is drawn here, so a layout is identical from post to post and the text is
 * always spelled right.
 *
 * Layouts, by format:
 *   transforms   toy-box, figurine, anime-frame, polaroid
 *   style swaps  anime-opening, vhs, poster
 *   memes        meme-top-bottom, meme-caption, meme-two-panel, meme-labels
 *   carousels    slide-cover, slide-option, slide-pair, slide-reveal,
 *                slide-text, slide-end
 *
 * Words arrive in `text` and are placed exactly as given; a layout names the
 * keys it needs and the render stops if one is missing. `placeholder` stamps
 * the frame so test copy is never mistaken for final.
 */



export type ImageLayout =
  | "toy-box"
  | "figurine"
  | "anime-frame"
  | "polaroid"
  | "anime-opening"
  | "vhs"
  | "poster"
  | "meme-top-bottom"
  | "meme-caption"
  | "meme-two-panel"
  | "meme-labels"
  | "slide-cover"
  | "slide-option"
  | "slide-pair"
  | "slide-reveal"
  | "slide-text"
  | "slide-end";

export type ImagePostProps = {
  layout: ImageLayout;
  images: string[];
  text: Record<string, string>;
  fonts?: FontFile[];
  logo?: string;
  /** Text color on the accent color. */
  onAccent?: string;
  brand?: Partial<Brand>;
  placeholder?: boolean;
  /** "3 / 6" style counter on carousel slides. */
  counter?: string;
  /** CSS object-position per picture, e.g. "center 30%". Memes honor it. */
  focal?: string[];
};

/** Every size is in units of the short edge / 1080, so 4:5, 1:1 and 9:16 share one scale. */
const useUnit = () => {
  const { width, height } = useVideoConfig();
  return Math.min(width, height) / 1080;
};

const Photo: React.FC<{ src?: string; fit?: "cover" | "contain"; style?: React.CSSProperties }> = ({
  src,
  fit = "cover",
  style,
}) =>
  src ? (
    <Img
      src={asset(src)}
      style={{ width: "100%", height: "100%", objectFit: fit, display: "block", ...style }}
    />
  ) : (
    <div style={{ width: "100%", height: "100%", background: "#444", ...style }} />
  );

/** Balanced line breaks, so a line never ends with one word alone. */
const BALANCE = { textWrap: "balance" } as unknown as React.CSSProperties;

const need = (text: Record<string, string>, keys: string[], layout: string) => {
  const missing = keys.filter((k) => !text[k]);
  if (missing.length) {
    cancelRender(new Error(`layout ${layout} needs text: ${missing.join(", ")}`));
  }
};

// ------------------------------------------------------------------ transforms

const ToyBox: React.FC<Inner> = ({ images, text, b, u, onAccent, logo }) => {
  need(text, ["name", "line"], "toy-box");
  return (
    <AbsoluteFill style={{ background: b.surface, padding: 54 * u }}>
      {/* backer card */}
      <div
        style={{
          position: "relative",
          flex: 1,
          borderRadius: 34 * u,
          background: `linear-gradient(160deg, ${b.accent} 0%, ${darken(b.accent, 0.35)} 100%)`,
          boxShadow: `0 ${30 * u}px ${60 * u}px rgba(0,0,0,0.55)`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          overflow: "hidden",
        }}
      >
        {/* hang tab */}
        <div
          style={{
            width: 150 * u,
            height: 26 * u,
            marginTop: 22 * u,
            borderRadius: 13 * u,
            background: b.surface,
            opacity: 0.85,
          }}
        />
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 800,
            color: onAccent,
            fontSize: 92 * u,
            lineHeight: 1,
            letterSpacing: -2 * u,
            textTransform: "uppercase",
            marginTop: 26 * u,
            textAlign: "center",
            padding: `0 ${40 * u}px`,
          }}
        >
          {text.name}
        </div>
        <div
          style={{
            fontFamily: b.captionFont,
            fontWeight: 700,
            color: onAccent,
            fontSize: 34 * u,
            marginTop: 12 * u,
            textAlign: "center",
            padding: `0 ${50 * u}px`,
          }}
        >
          {text.line}
        </div>
        {/* blister window */}
        <div
          style={{
            position: "relative",
            flex: 1,
            width: "86%",
            margin: `${28 * u}px 0 ${24 * u}px`,
            borderRadius: 40 * u,
            overflow: "hidden",
            background: "#d9d9d6",
            boxShadow: `inset 0 0 0 ${6 * u}px rgba(255,255,255,0.55), 0 ${10 * u}px ${24 * u}px rgba(0,0,0,0.35)`,
          }}
        >
          <Photo src={images[0]} fit="cover" style={{ objectPosition: "center 55%" }} />
          {/* plastic sheen */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(115deg, rgba(255,255,255,0.38) 0%, rgba(255,255,255,0.05) 28%, rgba(255,255,255,0) 55%, rgba(255,255,255,0.18) 78%, rgba(255,255,255,0) 100%)",
            }}
          />
          {text.badge ? (
            <div
              style={{
                position: "absolute",
                top: 26 * u,
                right: 26 * u,
                transform: "rotate(6deg)",
                background: b.surface,
                color: b.ink,
                fontFamily: b.headlineFont,
                fontWeight: 800,
                fontSize: 26 * u,
                padding: `${12 * u}px ${20 * u}px`,
                borderRadius: 999,
                boxShadow: `0 ${6 * u}px ${14 * u}px rgba(0,0,0,0.35)`,
              }}
            >
              {text.badge}
            </div>
          ) : null}
        </div>
        <div
          style={{
            width: "86%",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 30 * u,
            gap: 20 * u,
          }}
        >
          <div
            style={{
              fontFamily: b.captionFont,
              fontWeight: 700,
              color: onAccent,
              fontSize: 34 * u,
              lineHeight: 1.2,
              ...BALANCE,
              whiteSpace: "pre-line",
            }}
          >
            {text.includes ?? ""}
          </div>
          {logo ? (
            <div
              style={{
                background: b.surface,
                borderRadius: 14 * u,
                padding: `${10 * u}px ${16 * u}px`,
                flexShrink: 0,
              }}
            >
              <Img src={asset(logo)} style={{ height: 52 * u, display: "block" }} />
            </div>
          ) : null}
        </div>

      </div>
    </AbsoluteFill>
  );
};

const Figurine: React.FC<Inner> = ({ images, text, b, u }) => (
  <AbsoluteFill style={{ background: b.surface }}>
    <Photo src={images[0]} />
    {text.label ? (
      <div
        style={{
          position: "absolute",
          left: 54 * u,
          bottom: 54 * u,
          background: fade(b.surface, 0.86),
          color: b.ink,
          fontFamily: b.captionFont,
          fontWeight: 700,
          fontSize: 32 * u,
          padding: `${14 * u}px ${22 * u}px`,
          borderRadius: 12 * u,
          borderLeft: `${8 * u}px solid ${b.accent}`,
        }}
      >
        {text.label}
      </div>
    ) : null}
  </AbsoluteFill>
);

/** An anime screencap: the frame, a subtitle line, nothing else. */
const AnimeFrame: React.FC<Inner> = ({ images, text, b, u }) => {
  need(text, ["subtitle"], "anime-frame");
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo src={images[0]} />
      <div
        style={{
          position: "absolute",
          left: 60 * u,
          right: 60 * u,
          bottom: 110 * u,
          textAlign: "center",
          fontFamily: b.captionFont,
          fontWeight: 700,
          fontSize: 46 * u,
          lineHeight: 1.25,
          color: "#fff",
          WebkitTextStroke: `${7 * u}px #000`,
          paintOrder: "stroke fill",
          textShadow: `0 ${3 * u}px ${6 * u}px rgba(0,0,0,0.6)`,
        }}
      >
        {text.subtitle}
      </div>
    </AbsoluteFill>
  );
};

const Polaroid: React.FC<Inner> = ({ images, text, b, u, logo }) => {
  need(text, ["caption"], "polaroid");
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 40%, #2a2522 0%, ${b.surface} 75%)`,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: "90%",
          background: "#f7f4ee",
          padding: `${40 * u}px ${40 * u}px 0`,
          transform: "rotate(-2.2deg)",
          boxShadow: `0 ${30 * u}px ${70 * u}px rgba(0,0,0,0.65)`,
        }}
      >
        <div style={{ width: "100%", aspectRatio: "1 / 1", overflow: "hidden" }}>
          <Photo src={images[0]} />
        </div>
        <div
          style={{
            minHeight: 170 * u,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            fontFamily: b.headlineFont,
            fontWeight: 700,
            color: "#1d1b19",
            fontSize: 60 * u,
            lineHeight: 1.15,
            padding: `${20 * u}px ${10 * u}px`,
          }}
        >
          {text.caption}
        </div>
      </div>
      {logo ? (
        <Img
          src={asset(logo)}
          style={{ position: "absolute", left: 60 * u, bottom: 40 * u, height: 44 * u, mixBlendMode: "screen" }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

// ----------------------------------------------------------------- style swaps

const AnimeOpening: React.FC<Inner> = ({ images, text, b, u }) => {
  need(text, ["title"], "anime-opening");
  return (
    <AbsoluteFill style={{ background: "#000", justifyContent: "center" }}>
      {/* 4:3 broadcast frame inside the post */}
      <div style={{ position: "relative", width: "100%", height: 810 * u, overflow: "hidden" }}>
        <Photo src={images[0]} />
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 50 * u,
            textAlign: "center",
          }}
        >
          <div
            style={{
              display: "inline-block",
              fontFamily: b.headlineFont,
              fontWeight: 800,
              fontStyle: "italic",
              fontSize: 104 * u,
              lineHeight: 1,
              letterSpacing: -2 * u,
              color: "#fff",
              WebkitTextStroke: `${10 * u}px ${b.accent}`,
              paintOrder: "stroke fill",
              transform: "skewX(-8deg)",
              textShadow: `${8 * u}px ${8 * u}px 0 #000`,
            }}
          >
            {text.title}
          </div>
          {text.subtitle ? (
            <div
              style={{
                marginTop: 14 * u,
                fontFamily: b.captionFont,
                fontWeight: 700,
                fontSize: 30 * u,
                letterSpacing: 6 * u,
                textTransform: "uppercase",
                color: "#fff",
                textShadow: `0 0 ${10 * u}px #000, 0 0 ${4 * u}px #000`,
              }}
            >
              {text.subtitle}
            </div>
          ) : null}
        </div>
      </div>
      {text.credit ? (
        <div
          style={{
            position: "absolute",
            bottom: 40 * u,
            width: "100%",
            textAlign: "center",
            fontFamily: b.captionFont,
            fontWeight: 600,
            fontSize: 26 * u,
            color: "rgba(255,255,255,0.75)",
            letterSpacing: 2 * u,
          }}
        >
          {text.credit}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const OSD_FONT = '"Consolas", "Lucida Console", "Courier New", monospace';

const Vhs: React.FC<Inner> = ({ images, text, b, u, logo }) => {
  const osd: React.CSSProperties = {
    position: "absolute",
    fontFamily: OSD_FONT,
    fontWeight: 700,
    fontSize: 48 * u,
    color: "#fff",
    textShadow: `${3 * u}px 0 0 rgba(255,0,60,0.7), ${-3 * u}px 0 0 rgba(0,200,255,0.7)`,
    letterSpacing: 2 * u,
  };
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo
        src={images[0]}
        style={{ filter: "saturate(1.25) contrast(1.08) blur(0.6px)" }}
      />
      {/* chroma bleed */}
      <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.22, transform: `translateX(${6 * u}px)` }}>
        <Photo src={images[0]} style={{ filter: "blur(2px) hue-rotate(-30deg)" }} />
      </AbsoluteFill>
      {/* scanlines */}
      <AbsoluteFill
        style={{
          background: `repeating-linear-gradient(0deg, rgba(0,0,0,0.28) 0px, rgba(0,0,0,0.28) ${2 * u}px, rgba(0,0,0,0) ${2 * u}px, rgba(0,0,0,0) ${5 * u}px)`,
        }}
      />
      {/* tracking band */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "78%",
          height: 34 * u,
          background:
            "linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.35) 45%, rgba(255,255,255,0.1) 60%, rgba(255,255,255,0) 100%)",
          filter: "blur(1px)",
        }}
      />
      <AbsoluteFill
        style={{ boxShadow: `inset 0 0 ${180 * u}px rgba(0,0,0,0.75)` }}
      />
      {text.osd ? <div style={{ ...osd, top: 60 * u, left: 64 * u }}>{text.osd}</div> : null}
      {text.headline ? (
        <div
          style={{
            position: "absolute",
            left: 60 * u,
            right: 60 * u,
            bottom: 150 * u,
            padding: `${18 * u}px 0`,
            background: "linear-gradient(180deg, rgba(10,4,24,0) 0%, rgba(10,4,24,0.72) 22%, rgba(10,4,24,0.72) 78%, rgba(10,4,24,0) 100%)",
            transform: "skewX(-10deg)",
            textAlign: "center",
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontStyle: "italic",
            fontSize: 98 * u,
            lineHeight: 1,
            textTransform: "uppercase",
            color: "#fff4d6",
            // An outline from shadows, not a stroke: a stroke on skewed italic
            // draws slashes inside the letters.
            textShadow: [-1, 1].flatMap((x) => [-1, 1].map((y) => `${x * 3 * u}px ${y * 3 * u}px 0 #ff2fa0`))
              .concat([`0 0 ${18 * u}px rgba(255,47,160,0.85)`, `${7 * u}px ${7 * u}px 0 #1b0b3a`])
              .join(", "),
          }}
        >
          {text.headline}
        </div>
      ) : null}
      <div style={{ ...osd, bottom: 70 * u, right: 64 * u, fontSize: 40 * u, textAlign: "right" }}>
        {text.date ?? ""}
      </div>
      {logo ? (
        <Img
          src={asset(logo)}
          style={{ position: "absolute", left: 64 * u, bottom: 66 * u, height: 44 * u, mixBlendMode: "screen" }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

const Poster: React.FC<Inner> = ({ images, text, b, u, logo }) => {
  need(text, ["title"], "poster");
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Photo src={images[0]} />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.85) 100%)",
        }}
      />
      {text.tagline ? (
        <div
          style={{
            position: "absolute",
            top: 60 * u,
            left: 80 * u,
            right: 80 * u,
            textAlign: "center",
            fontFamily: b.captionFont,
            fontWeight: 600,
            fontSize: 34 * u,
            letterSpacing: 4 * u,
            textTransform: "uppercase",
            color: "#fff",
          }}
        >
          {text.tagline}
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 60 * u, right: 60 * u, bottom: 64 * u, textAlign: "center" }}>
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 120 * u,
            lineHeight: 0.95,
            letterSpacing: -3 * u,
            color: "#fff",
            textShadow: `0 ${6 * u}px ${24 * u}px rgba(0,0,0,0.6)`,
          }}
        >
          {text.title}
        </div>
        {text.date ? (
          <div
            style={{
              marginTop: 18 * u,
              fontFamily: b.headlineFont,
              fontWeight: 700,
              fontSize: 36 * u,
              color: b.accent,
              letterSpacing: 3 * u,
              textTransform: "uppercase",
            }}
          >
            {text.date}
          </div>
        ) : null}
        {text.credits ? (
          <div
            style={{
              marginTop: 18 * u,
              fontFamily: b.captionFont,
              fontWeight: 600,
              fontSize: 20 * u,
              lineHeight: 1.3,
              color: "rgba(255,255,255,0.7)",
              letterSpacing: 1 * u,
              textTransform: "uppercase",
            }}
          >
            {text.credits}
          </div>
        ) : null}
        {logo ? (
          <Img
            src={asset(logo)}
            style={{ height: 56 * u, marginTop: 20 * u, mixBlendMode: "screen" }}
          />
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

// ----------------------------------------------------------------------- memes
// Memes are native artifacts: deliberately plain, no brand frame.

const IMPACT = '"Impact", "Anton", "Arial Black", sans-serif';

const memeImpact = (u: number, size: number): React.CSSProperties => ({
  fontFamily: IMPACT,
  fontSize: size * u,
  lineHeight: 1.05,
  color: "#fff",
  textTransform: "uppercase",
  textAlign: "center",
  WebkitTextStroke: `${8 * u}px #000`,
  paintOrder: "stroke fill",
});

const MemeTopBottom: React.FC<Inner> = ({ images, text, u }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Photo src={images[0]} />
    <div style={{ position: "absolute", top: 36 * u, left: 40 * u, right: 40 * u, ...memeImpact(u, 92) }}>
      {text.top ?? ""}
    </div>
    <div style={{ position: "absolute", bottom: 40 * u, left: 40 * u, right: 40 * u, ...memeImpact(u, 92) }}>
      {text.bottom ?? ""}
    </div>
  </AbsoluteFill>
);

/** The modern caption meme: a white band of plain text over the picture. */
const MemeCaption: React.FC<Inner> = ({ images, text, u }) => {
  need(text, ["caption"], "meme-caption");
  return (
    <AbsoluteFill style={{ background: "#fff", flexDirection: "column" }}>
      <div
        style={{
          padding: `${44 * u}px ${54 * u}px`,
          fontFamily: '"Helvetica Neue", Arial, sans-serif',
          fontSize: 50 * u,
          lineHeight: 1.22,
          color: "#111",
          whiteSpace: "pre-line",
        }}
      >
        {text.caption}
      </div>
      <div style={{ flex: 1, overflow: "hidden" }}>
        <Photo src={images[0]} />
      </div>
    </AbsoluteFill>
  );
};

/** Two rows: picture left, words right. The "no / yes" layout. */
const MemeTwoPanel: React.FC<Inner> = ({ images, text, u, focal }) => {
  need(text, ["top", "bottom"], "meme-two-panel");
  const row = (src: string | undefined, words: string, pos?: string) => (
    <div style={{ height: "50%", display: "flex", borderBottom: `${3 * u}px solid #000` }}>
      <div style={{ width: "50%", height: "100%", overflow: "hidden" }}>
        <Photo src={src} style={{ objectPosition: pos }} />
      </div>
      <div
        style={{
          width: "50%",
          background: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 40 * u,
          fontFamily: '"Helvetica Neue", Arial, sans-serif',
          fontWeight: 700,
          fontSize: 50 * u,
          lineHeight: 1.18,
          color: "#111",
          textAlign: "center",
          ...BALANCE,
          whiteSpace: "pre-line",
        }}
      >
        {words}
      </div>
    </div>
  );
  return (
    <AbsoluteFill style={{ background: "#fff", flexDirection: "column" }}>
      {row(images[0], text.top, focal?.[0])}
      {row(images[1], text.bottom, focal?.[1])}
    </AbsoluteFill>
  );
};

/** Two stacked pictures with a label on each: expectation and reality. */
const MemeLabels: React.FC<Inner> = ({ images, text, u, focal }) => {
  need(text, ["labelA", "labelB"], "meme-labels");
  const panel = (src: string | undefined, label: string, pos?: string) => (
    <div style={{ position: "relative", height: "50%", overflow: "hidden", borderBottom: `${4 * u}px solid #fff` }}>
      <Photo src={src} style={{ objectPosition: pos }} />
      <div style={{ position: "absolute", left: 30 * u, right: 30 * u, bottom: 44 * u, ...memeImpact(u, 76) }}>
        {label}
      </div>
    </div>
  );
  return (
    <AbsoluteFill style={{ background: "#fff", flexDirection: "column" }}>
      {panel(images[0], text.labelA, focal?.[0])}
      {panel(images[1], text.labelB, focal?.[1])}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------- carousels

const Mark: React.FC<{ logo?: string; u: number; b: Brand }> = ({ logo, u }) =>
  logo ? (
    <Img
      src={asset(logo)}
      style={{ position: "absolute", top: 62 * u, left: 80 * u, height: 50 * u, mixBlendMode: "screen" }}
    />
  ) : null;

const Counter: React.FC<{ counter?: string; u: number; b: Brand }> = ({ counter, u, b }) =>
  counter ? (
    <div
      style={{
        position: "absolute",
        top: 62 * u,
        right: 80 * u,
        fontFamily: b.captionFont,
        fontWeight: 700,
        fontSize: 26 * u,
        color: fade(b.ink, 0.9),
        background: fade(b.surface, 0.6),
        border: `${2 * u}px solid ${fade(b.ink, 0.35)}`,
        padding: `${6 * u}px ${14 * u}px`,
        borderRadius: 999,
        letterSpacing: 2 * u,
      }}
    >
      {counter}
    </div>
  ) : null;

const Eyebrow: React.FC<{ children?: string; u: number; b: Brand }> = ({ children, u, b }) =>
  children ? (
    <div
      style={{
        fontFamily: b.captionFont,
        fontWeight: 700,
        fontSize: 30 * u,
        letterSpacing: 4 * u,
        textTransform: "uppercase",
        color: b.accent,
        marginBottom: 22 * u,
      }}
    >
      {children}
    </div>
  ) : null;

const SlideCover: React.FC<Inner> = ({ images, text, b, u, logo, counter }) => {
  need(text, ["headline"], "slide-cover");
  return (
    <AbsoluteFill style={{ background: b.surface }}>
      {images[0] ? (
        <>
          <Photo src={images[0]} />
          <AbsoluteFill
            style={{
              background:
                `linear-gradient(180deg, ${fade(b.surface, 0.55)} 0%, ${fade(b.surface, 0.1)} 35%, ${fade(b.surface, 0.92)} 72%)`,
            }}
          />
        </>
      ) : null}
      <Mark logo={logo} u={u} b={b} />
      <Counter counter={counter} u={u} b={b} />
      <div style={{ position: "absolute", left: 80 * u, right: 80 * u, bottom: 120 * u }}>
        <Eyebrow u={u} b={b}>{text.eyebrow}</Eyebrow>
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 104 * u,
            lineHeight: 1.0, ...BALANCE,
            letterSpacing: -3 * u,
            color: b.ink,
          }}
        >
          {text.headline}
        </div>
        <div style={{ width: 140 * u, height: 12 * u, background: b.accent, marginTop: 34 * u }} />
      </div>
      {text.cue ? (
        <div
          style={{
            position: "absolute",
            right: 70 * u,
            bottom: 70 * u,
            fontFamily: b.captionFont,
            fontWeight: 700,
            fontSize: 30 * u,
            color: b.ink,
          }}
        >
          {text.cue} →
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Badge: React.FC<{ children: string; u: number; b: Brand; onAccent: string; size?: number }> = ({
  children,
  u,
  b,
  onAccent,
  size = 120,
}) => (
  <div
    style={{
      minWidth: size * u,
      height: size * u,
      padding: `0 ${24 * u}px`,
      borderRadius: 999,
      background: b.accent,
      color: onAccent,
      fontFamily: b.headlineFont,
      fontWeight: 800,
      fontSize: size * 0.5 * u,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: `0 ${8 * u}px ${20 * u}px rgba(0,0,0,0.45)`,
    }}
  >
    {children}
  </div>
);

const SlideOption: React.FC<Inner> = ({ images, text, b, u, onAccent, counter }) => {
  need(text, ["badge", "title"], "slide-option");
  return (
    <AbsoluteFill style={{ background: b.surface, flexDirection: "column" }}>
      <div style={{ position: "relative", height: "68%", overflow: "hidden" }}>
        <Photo src={images[0]} />
        <Counter counter={counter} u={u} b={b} />
      </div>
      <div
        style={{
          position: "relative",
          flex: 1,
          padding: `${70 * u}px ${80 * u}px ${30 * u}px`,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <div style={{ position: "absolute", top: -60 * u, left: 80 * u }}>
          <Badge u={u} b={b} onAccent={onAccent}>{text.badge}</Badge>
        </div>
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 72 * u,
            lineHeight: 1.05,
            letterSpacing: -2 * u,
            color: b.ink,
          }}
        >
          {text.title}
        </div>
        {text.body ? (
          <div
            style={{
              marginTop: 22 * u,
              fontFamily: b.captionFont,
              fontWeight: 600,
              fontSize: 38 * u,
              ...BALANCE,
              lineHeight: 1.3,
              color: fade(b.ink, 0.82),
            }}
          >
            {text.body}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const SlidePair: React.FC<Inner> = ({ images, text, b, u, onAccent, counter }) => {
  need(text, ["question"], "slide-pair");
  const half = (src: string | undefined, label: string) => (
    <div style={{ position: "relative", flex: 1, overflow: "hidden", borderRadius: 24 * u }}>
      <Photo src={src} />
      <div style={{ position: "absolute", left: 24 * u, top: 24 * u }}>
        <Badge u={u} b={b} onAccent={onAccent} size={90}>{label}</Badge>
      </div>
    </div>
  );
  return (
    <AbsoluteFill style={{ background: b.surface, padding: `${150 * u}px ${54 * u}px ${54 * u}px`, flexDirection: "column" }}>
      <Counter counter={counter} u={u} b={b} />
      <div
        style={{
          position: "absolute",
          top: 54 * u,
          left: 54 * u,
          right: 160 * u,
          fontFamily: b.headlineFont,
          fontWeight: 800,
          fontSize: 54 * u,
          lineHeight: 1.05,
          color: b.ink,
        }}
      >
        {text.question}
      </div>
      <div style={{ flex: 1, display: "flex", gap: 24 * u, marginTop: 20 * u }}>
        {half(images[0], text.labelA ?? "A")}
        {half(images[1], text.labelB ?? "B")}
      </div>
    </AbsoluteFill>
  );
};

const SlideReveal: React.FC<Inner> = ({ images, text, b, u, counter }) => {
  need(text, ["stamp", "title"], "slide-reveal");
  return (
    <AbsoluteFill style={{ background: b.surface, flexDirection: "column" }}>
      <div style={{ position: "relative", height: "62%", overflow: "hidden" }}>
        <Photo src={images[0]} />
        <Counter counter={counter} u={u} b={b} />
        <div
          style={{
            position: "absolute",
            right: 60 * u,
            bottom: 50 * u,
            transform: "rotate(-8deg)",
            border: `${10 * u}px solid ${b.accent}`,
            color: b.accent,
            background: fade(b.surface, 0.75),
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 84 * u,
            lineHeight: 1,
            padding: `${14 * u}px ${30 * u}px`,
            borderRadius: 16 * u,
            textTransform: "uppercase",
          }}
        >
          {text.stamp}
        </div>
      </div>
      <div style={{ flex: 1, padding: `${50 * u}px ${80 * u}px 0` }}>
        <div
          style={{
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 64 * u,
            lineHeight: 1.05,
            letterSpacing: -2 * u,
            color: b.ink,
          }}
        >
          {text.title}
        </div>
        {text.body ? (
          <div
            style={{
              marginTop: 20 * u,
              fontFamily: b.captionFont,
              fontWeight: 600,
              fontSize: 36 * u,
              ...BALANCE,
              lineHeight: 1.3,
              color: fade(b.ink, 0.82),
            }}
          >
            {text.body}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/**
 * A text slide. Up to three pictures give it a strip of crops above the words,
 * so a result slide can bring back the options it sums up.
 */
const SlideText: React.FC<Inner> = ({ images, text, b, u, logo, counter, focal }) => {
  need(text, ["headline"], "slide-text");
  const strip = images.slice(0, 3);
  return (
    <AbsoluteFill style={{ background: b.surface, justifyContent: "center", padding: `0 ${80 * u}px` }}>
      <Mark logo={logo} u={u} b={b} />
      <Counter counter={counter} u={u} b={b} />
      {strip.length ? (
        <div style={{ display: "flex", gap: 20 * u, marginBottom: 56 * u }}>
          {strip.map((src, i) => (
            <div key={src + i} style={{ flex: 1, aspectRatio: "1 / 1", overflow: "hidden", borderRadius: 20 * u }}>
              <Photo src={src} style={{ objectPosition: focal?.[i] ?? "center 30%" }} />
            </div>
          ))}
        </div>
      ) : null}
      <Eyebrow u={u} b={b}>{text.eyebrow}</Eyebrow>
      <div
        style={{
          fontFamily: b.headlineFont,
          fontWeight: 800,
          fontSize: (strip.length ? 124 : 84) * u, ...BALANCE,
          lineHeight: 1.05,
          letterSpacing: -2 * u,
          color: b.ink,
        }}
      >
        {text.headline}
      </div>
      {text.body ? (
        <div
          style={{
            marginTop: 34 * u,
            fontFamily: b.captionFont,
            fontWeight: 600,
            fontSize: 42 * u,
            ...BALANCE,
            lineHeight: 1.35,
            color: fade(b.ink, 0.85),
            whiteSpace: "pre-line",
          }}
        >
          {text.body}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** The last slide reads as an ending: accent ground, logo, the one ask. */
const SlideEnd: React.FC<Inner> = ({ text, b, u, onAccent, logo, counter }) => {
  need(text, ["headline"], "slide-end");
  return (
    <AbsoluteFill
      style={{
        background: b.accent,
        justifyContent: "center",
        alignItems: "flex-start",
        padding: `0 ${80 * u}px`,
      }}
    >
      <Counter counter={counter} u={u} b={b} />
      <div
        style={{
          fontFamily: b.headlineFont,
          fontWeight: 800,
          fontSize: 92 * u,
          lineHeight: 1.02, ...BALANCE,
          letterSpacing: -2 * u,
          color: onAccent,
        }}
      >
        {text.headline}
      </div>
      {text.body ? (
        <div
          style={{
            marginTop: 30 * u,
            fontFamily: b.captionFont,
            fontWeight: 700,
            fontSize: (text.cta ? 42 : 64) * u,
            ...BALANCE,
            lineHeight: 1.3,
            color: onAccent,
            whiteSpace: "pre-line",
          }}
        >
          {text.body}
        </div>
      ) : null}
      {text.cta ? (
        <div
          style={{
            marginTop: 50 * u,
            background: b.surface,
            color: b.ink,
            fontFamily: b.headlineFont,
            fontWeight: 800,
            fontSize: 40 * u,
            padding: `${24 * u}px ${40 * u}px`,
            borderRadius: 999,
          }}
        >
          {text.cta}
        </div>
      ) : null}
      {logo ? (
        <div
          style={{
            position: "absolute",
            left: 80 * u,
            bottom: 80 * u,
            background: b.surface,
            borderRadius: 16 * u,
            padding: `${12 * u}px ${20 * u}px`,
          }}
        >
          <Img src={asset(logo)} style={{ height: 60 * u, display: "block" }} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------- shell

type Inner = {
  images: string[];
  text: Record<string, string>;
  b: Brand;
  u: number;
  onAccent: string;
  logo?: string;
  counter?: string;
  focal?: string[];
};

const LAYOUTS: Record<ImageLayout, React.FC<Inner>> = {
  "toy-box": ToyBox,
  figurine: Figurine,
  "anime-frame": AnimeFrame,
  polaroid: Polaroid,
  "anime-opening": AnimeOpening,
  vhs: Vhs,
  poster: Poster,
  "meme-top-bottom": MemeTopBottom,
  "meme-caption": MemeCaption,
  "meme-two-panel": MemeTwoPanel,
  "meme-labels": MemeLabels,
  "slide-cover": SlideCover,
  "slide-option": SlideOption,
  "slide-pair": SlidePair,
  "slide-reveal": SlideReveal,
  "slide-text": SlideText,
  "slide-end": SlideEnd,
};

export const ImagePost: React.FC<ImagePostProps> = (p) => {
  useFonts(p.fonts);
  const u = useUnit();
  const b = resolveBrand(p.brand);
  const Layout = LAYOUTS[p.layout];
  if (!Layout) cancelRender(new Error(`unknown layout: ${p.layout}`));
  return (
    <AbsoluteFill>
      <Layout
        images={p.images}
        text={p.text}
        b={b}
        u={u}
        onAccent={p.onAccent ?? b.onAccent}
        logo={p.logo}
        counter={p.counter}
        focal={p.focal}
      />
      {p.placeholder ? (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            background: "#ff1f5a",
            color: "#fff",
            fontFamily: b.captionFont,
            fontWeight: 700,
            fontSize: 24 * u,
            letterSpacing: 3 * u,
            textAlign: "center",
            padding: `${8 * u}px 0`,
          }}
        >
          PLACEHOLDER COPY: NOT FOR POSTING
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
