import { staticFile } from "remotion";

/**
 * A file the template draws. render.mjs copies every local file named in the
 * props into a staging folder and swaps in its staged name; a web address or
 * data URL passes through untouched.
 */
export const asset = (src: string) =>
  /^(https?:|data:)/i.test(src) ? src : staticFile(src);

const IMAGE = /\.(png|jpe?g|webp|gif|avif|bmp|svg)$/i;

/** True when the file is a still picture rather than a video. */
export const isImage = (src: string) => IMAGE.test(src.split("?")[0]);
