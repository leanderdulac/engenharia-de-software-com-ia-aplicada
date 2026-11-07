const ALLOWED = new Set([
  "a",
  "abbr",
  "b",
  "blockquote",
  "br",
  "caption",
  "code",
  "del",
  "div",
  "em",
  "figcaption",
  "figure",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "hr",
  "i",
  "img",
  "li",
  "ol",
  "p",
  "pre",
  "span",
  "strong",
  "sub",
  "sup",
  "table",
  "tbody",
  "td",
  "th",
  "thead",
  "tr",
  "ul",
  "audio",
  "source",
  "track",
  "video",
]);

const URL_ATTR = new Set(["href", "src"]);
const OK_ATTR = new Set([
  "href",
  "src",
  "alt",
  "title",
  "class",
  "id",
  "rel",
  "target",
  "controls",
  "preload",
  "kind",
  "srclang",
  "label",
  "default",
  "colspan",
  "rowspan",
  "type",
  "width",
  "height",
]);

function safeUrl(value) {
  const v = String(value || "").trim();
  if (!v) return "";
  if (v.startsWith("#") || v.startsWith("/") || v.startsWith("./") || v.startsWith("../")) {
    if (/^(javascript|vbscript|data):/i.test(v)) return "";
    return v;
  }
  if (/^https?:\/\//i.test(v) || /^mailto:/i.test(v)) return v;
  return "";
}

/**
 * Sanitização HTML do markdown da aula. Não é um motor DOM completo;
 * remove tags/handlers perigosos antes de SSR.
 */
export function sanitizeHtml(html) {
  let s = String(html || "");
  s = s.replace(/<!--[\s\S]*?-->/g, "");
  s = s.replace(/<(script|style|iframe|object|embed|form|input|textarea|link|meta|base|svg)[\s\S]*?<\/\1>/gi, "");
  s = s.replace(/<(script|style|iframe|object|embed|form|input|link|meta|base|svg)[^>]*>/gi, "");
  s = s.replace(/<\/?([a-zA-Z0-9]+)([^>]*)>/g, (full, tag, attrs) => {
    const name = tag.toLowerCase();
    const closing = full.startsWith("</");
    if (!ALLOWED.has(name)) return "";
    if (closing) return `</${name}>`;
    const kept = [];
    const re = /([a-zA-Z:_][a-zA-Z0-9:_.-]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))/g;
    let m;
    while ((m = re.exec(attrs))) {
      const attr = m[1].toLowerCase();
      if (attr.startsWith("on") || attr === "srcset" || attr === "style") continue;
      if (!OK_ATTR.has(attr)) continue;
      let val = m[3] ?? m[4] ?? m[5] ?? "";
      if (URL_ATTR.has(attr)) {
        val = safeUrl(val);
        if (!val) continue;
        if (attr === "href" && /^https?:/i.test(val)) {
          kept.push(`rel="noopener noreferrer"`);
        }
      } else {
        val = String(val).replace(/"/g, "&quot;");
      }
      kept.push(`${attr}="${val}"`);
    }
    if (name === "a" && !kept.some((k) => k.startsWith("href="))) return "<span>";
    return `<${name}${kept.length ? " " + kept.join(" ") : ""}>`;
  });
  return s;
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function safeHttpUrl(raw) {
  const v = String(raw || "").trim();
  if (!v) return "";
  if (v.length > 500) return "";
  try {
    const u = new URL(v);
    if (u.protocol !== "http:" && u.protocol !== "https:") return "";
    return u.toString();
  } catch {
    return "";
  }
}
