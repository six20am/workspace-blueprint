import { useEffect, useState } from "react";
import { cancelRender, continueRender, delayRender } from "remotion";
import { asset } from "./asset";

/** A font file the person supplies, for example a free font they downloaded. */
export type FontFile = { family: string; weight: number; src: string };

/** Load the given font files before the first frame is captured. */
export const useFonts = (fonts: FontFile[] | undefined) => {
  const list = fonts ?? [];
  const [handle] = useState(() => (list.length ? delayRender("fonts") : null));
  useEffect(() => {
    if (handle === null) return;
    Promise.all(
      list.map((f) => {
        const face = new FontFace(f.family, `url(${asset(f.src)})`, { weight: String(f.weight) });
        const set = document.fonts as unknown as { add: (f: FontFace) => void };
        return face.load().then((loaded) => set.add(loaded));
      }),
    )
      .then(() => continueRender(handle))
      // A missing font fails the render rather than shipping in a fallback face.
      .catch((err) => cancelRender(new Error(`font failed to load: ${err}`)));
    // Fonts are fixed for the whole render; load them once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handle]);
};
