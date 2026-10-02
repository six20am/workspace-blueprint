// Logo scoring + founder-hint scoring.
// Inputs: discovery context per image (where it was found, what tags surrounded it),
// plus sharp metadata (dimensions, format, bytes).

const LOGO_KEYWORDS = /(^|[\W_])(logo|brand|wordmark|sitemark|monogram)([\W_]|$)/i;

export function scoreLogo({ discovery, meta }) {
  let score = 0;
  const signals = [];

  if (discovery.from === "favicon") {
    score += 40;
    signals.push("favicon");
  }
  if (discovery.from === "apple-touch-icon") {
    score += 40;
    signals.push("apple-touch-icon");
  }
  if (discovery.from === "og-image") {
    score += 30;
    signals.push("og-image");
  }
  if (discovery.from === "schema-org-logo") {
    score += 50;
    signals.push("schema-org");
  }
  if (discovery.from === "img-in-header") {
    score += 20;
    signals.push("in-header");
  }
  if (discovery.from === "img-in-footer") {
    score += 10;
    signals.push("in-footer");
  }

  const tokens = [
    discovery.altText || "",
    discovery.className || "",
    discovery.id || "",
    discovery.sourceUrl || "",
  ].join(" ");
  if (LOGO_KEYWORDS.test(tokens)) {
    score += 30;
    signals.push("logo-token-in-attr");
  }

  if (meta.format === "svg") {
    score += 20;
    signals.push("svg");
  }
  if (meta.format === "png" && meta.hasAlpha) {
    score += 15;
    signals.push("transparent-png");
  }
  if (meta.bytes && meta.bytes < 50_000) {
    score += 10;
    signals.push("small-file");
  }

  const longEdge = Math.max(meta.width || 0, meta.height || 0);
  if (longEdge > 0 && longEdge < 400) {
    score += 10;
    signals.push("small-dimensions");
  }
  if (longEdge > 1200) {
    score -= 30;
    signals.push("too-large-for-logo");
  }

  if (meta.width && meta.height) {
    const ratio = meta.width / meta.height;
    if (ratio > 1.5 && ratio < 6) {
      score += 5;
      signals.push("wordmark-aspect");
    }
    if (ratio > 0.8 && ratio < 1.25 && longEdge < 400) {
      score += 5;
      signals.push("square-mark");
    }
  }

  return { score: Math.max(0, Math.min(100, score)), signals };
}

export function founderHint({ pagesAppearedOn, meta, altText }) {
  if (pagesAppearedOn < 3) return false;

  const width = meta.width || 0;
  const height = meta.height || 0;
  if (!width || !height) return false;

  const ratio = width / height;
  const portraitish = ratio >= 0.5 && ratio <= 0.95;
  const decentSize = Math.min(width, height) >= 300;
  if (!portraitish || !decentSize) return false;

  const nameLike = /\b[A-Z][a-z]{2,}\b/.test(altText || "");
  return nameLike || pagesAppearedOn >= 4;
}
