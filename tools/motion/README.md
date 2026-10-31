# motion

Ten motion graphics templates over Remotion: title cards, captions, slideshows, transitions and more, rendered to .mp4 or .png on this computer. No account, no key, nothing uploaded. The `motion-video` skill drives it.

## Install once

Run `npm install` inside `tools/motion/`. It downloads several hundred MB (about 560 MB here): the packages, then the `postinstall` hook in `package.json` runs `remotion browser ensure`, which fetches the headless Chrome that draws the frames. Setup does this for you.

## The ten templates

Every template also takes `brand` (colors and fonts, see `src/brand.ts`). Files named in the props are read relative to the props file. A sample props file for each one is in `examples/`.

- `AspectVariant` (still): one picture as another aspect. `src`, `fit` (cover or blur-extend), `focal`.
- `BeforeAfter`: a wipe from a before to an after photo. `before`, `after`, labels, `logo`, `outroHeadline`, `cta`.
- `BrandedClip`: logo intro, footage, outro card, with bug, lower third and captions. `src`, `logo` or `name`, `lowerThird`, `cues` or `words`, `cta`.
- `CaptionBurn`: captions burned into a video, word by word. `src`, `words` (text, startMs, endMs) or `cues` (text, from, to).
- `CoverFrame`: a title card or thumbnail. `headline`, `eyebrow` (a date), `logo`, `src`, `seconds`.
- `DataVideo`: a numbers video from a small table. `title`, `rows` (label, value, prefix, suffix), `note`, `cta`.
- `ImagePost` (still): a social image layout, 17 layouts. `layout`, `images`, `text`, `logo`.
- `KenBurns`: a slow zoom or pan across one photo. `src`, `direction`, `zoom`, `seconds`.
- `Slideshow`: photos with slow zoom, joined by fade, slide, wipe or push. `slides`, `secondsPerSlide`, `transition`, `cards`, `music`.
- `TalkingCards`: cards that land one by one, per scene. `scenes` (title, seconds, items), `audio`, `cues`.

## Render

```
node tools/motion/render.mjs --composition CoverFrame --props my-card.json --out open-house.mp4 --aspect 9:16
```

`--aspect` is 16:9, 9:16 or 1:1. An `--out` ending in `.png` or `.jpg` gives a still. `--scale 0.5` renders a quick small test. The out file must not exist yet.

## License terms

Remotion is not free for everyone. It is free for individuals, for companies of three people or fewer, and for non-profits; a company with more people needs a Remotion company license (remotion.pro). Remotion is installed by npm, not shipped here.

The transition recipes in `src/effects/` are adapted from awesome-ai-motion by gongnyang (MIT): see `LICENSE-awesome-ai-motion` and `ATTRIBUTIONS.md`.
