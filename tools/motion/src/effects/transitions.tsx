import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Transition recipes: fade, slide, wipe and push.
 *
 * Timings, distances and easing curves are adapted from the awesome-ai-motion
 * effect cards `fade`, `slide`, `wipe`, `push-transition` and `crossfade`
 * (MIT, see ../../LICENSE-awesome-ai-motion and ../../ATTRIBUTIONS.md),
 * rewritten as Remotion frame math instead of CSS keyframes.
 *
 *   fade   incoming scene fades in on top, 0.6 s, ease out. The outgoing scene
 *          holds, so the seam never dips to the background color.
 *   slide  incoming scene slides in from one edge, 100% travel, 0.6 s, ease out.
 *   wipe   a moving edge uncovers the incoming scene, 1.2 s, linear, with a thin
 *          accent line riding the edge.
 *   push   incoming scene pushes the outgoing one off by the same distance in
 *          the same direction, 1.2 s, ease in and out.
 */

export type TransitionKind = "none" | "fade" | "slide" | "wipe" | "push";
/** The edge the incoming scene arrives from. */
export type Direction = "left" | "right" | "up" | "down";

/** cubic-bezier(0.22, 1, 0.36, 1) from the fade and slide cards. */
export const EASE_OUT = Easing.bezier(0.22, 1, 0.36, 1);
/** power2.inOut from the push card. */
export const EASE_IN_OUT = Easing.inOut(Easing.quad);
const LINEAR = (t: number) => t;

export const RECIPE_SECONDS: Record<TransitionKind, number> = {
  none: 0,
  fade: 0.6,
  slide: 0.6,
  wipe: 1.2,
  push: 1.2,
};

const EASING: Record<TransitionKind, (t: number) => number> = {
  none: LINEAR,
  fade: EASE_OUT,
  slide: EASE_OUT,
  wipe: LINEAR,
  push: EASE_IN_OUT,
};

/** Length of a transition in frames; `seconds` overrides the recipe default. */
export const transitionFrames = (kind: TransitionKind, fps: number, seconds?: number) =>
  kind === "none" ? 0 : Math.max(1, Math.round((seconds ?? RECIPE_SECONDS[kind]) * fps));

/** Eased 0 to 1 progress of a transition that starts at `start` and lasts `frames`. */
export const transitionProgress = (frame: number, start: number, frames: number, kind: TransitionKind) =>
  frames <= 0
    ? 1
    : interpolate(frame, [start, start + frames], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: EASING[kind],
      });

const shift = (dir: Direction, pct: number) =>
  dir === "left"
    ? `translateX(${-pct}%)`
    : dir === "right"
      ? `translateX(${pct}%)`
      : dir === "up"
        ? `translateY(${-pct}%)`
        : `translateY(${pct}%)`;

/** Style for the incoming scene at progress `p` (0 = not yet in, 1 = settled). */
export const enterStyle = (kind: TransitionKind, p: number, dir: Direction = "right"): React.CSSProperties => {
  const rest = (1 - p) * 100;
  switch (kind) {
    case "fade":
      return { opacity: p };
    case "slide":
    case "push":
      return { transform: shift(dir, rest) };
    case "wipe":
      // The edge travels away from the side the scene arrives from.
      return {
        clipPath:
          dir === "left"
            ? `inset(0 ${rest}% 0 0)`
            : dir === "right"
              ? `inset(0 0 0 ${rest}%)`
              : dir === "up"
                ? `inset(0 0 ${rest}% 0)`
                : `inset(${rest}% 0 0 0)`,
      };
    default:
      return {};
  }
};

/** Style for the outgoing scene. Only push moves it; the others hold it still. */
export const exitStyle = (kind: TransitionKind, p: number, dir: Direction = "right"): React.CSSProperties => {
  if (kind !== "push") return {};
  const opposite: Record<Direction, Direction> = { left: "right", right: "left", up: "down", down: "up" };
  return { transform: shift(opposite[dir], p * 100) };
};

/** The thin accent line that rides a wipe's edge. Hidden before and after the move. */
export const WipeEdge: React.FC<{ p: number; dir: Direction; color: string }> = ({ p, dir, color }) => {
  const { width, height } = useVideoConfig();
  if (p <= 0 || p >= 1) return null;
  const line = Math.max(4, Math.min(width, height) * 0.006);
  const horizontal = dir === "left" || dir === "right";
  const pos = horizontal
    ? dir === "left" ? width * p : width * (1 - p)
    : dir === "up" ? height * p : height * (1 - p);
  return (
    <div
      style={{
        position: "absolute",
        backgroundColor: color,
        boxShadow: `0 0 ${line * 4}px ${color}`,
        ...(horizontal
          ? { top: 0, bottom: 0, left: pos - line / 2, width: line }
          : { left: 0, right: 0, top: pos - line / 2, height: line }),
      }}
    />
  );
};

/**
 * One scene in a run of scenes. Mount it inside a <Sequence> that starts
 * `enterFrames` before the previous scene ends; it plays its own entrance and,
 * when the next scene pushes it, its own exit.
 */
export const SceneTransition: React.FC<{
  kind: TransitionKind;
  dir?: Direction;
  /** Frames of entrance at the head of this scene. 0 for the first scene. */
  enterFrames: number;
  /** Frames at the tail of this scene that overlap the next scene's entrance. */
  exitFrames: number;
  /** Total frames this scene stays mounted. */
  span: number;
  accent: string;
  children: React.ReactNode;
}> = ({ kind, dir = "right", enterFrames, exitFrames, span, accent, children }) => {
  const frame = useCurrentFrame();
  const pIn = transitionProgress(frame, 0, enterFrames, kind);
  const pOut = exitFrames > 0 ? transitionProgress(frame, span - exitFrames, exitFrames, kind) : 0;
  const style = enterFrames > 0 && frame < enterFrames ? enterStyle(kind, pIn, dir) : exitStyle(kind, pOut, dir);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={style}>{children}</AbsoluteFill>
      {kind === "wipe" && enterFrames > 0 ? <WipeEdge p={pIn} dir={dir} color={accent} /> : null}
    </AbsoluteFill>
  );
};

/** Entrance for a single element (a title, a card): fade or slide, from the recipes. */
export const useEntrance = (kind: "fade" | "slide", delayFrames = 0, distancePx = 48) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = transitionProgress(frame, delayFrames, transitionFrames(kind, fps), kind);
  return kind === "fade"
    ? { opacity: p }
    : { opacity: Math.min(1, p * 1.6), transform: `translateY(${(1 - p) * distancePx}px)` };
};
