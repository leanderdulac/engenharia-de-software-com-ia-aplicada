import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { CURSO_ROOT, REPO_ROOT, isInsideRoot } from "./paths.mjs";

const LINK_MD = /\[([^\]]*)\]\(([^)]+)\)/g;
const SKIP_DIR = new Set(["node_modules", ".git", "dist"]);

export function extractMarkdownLinks(markdown) {
  const links = [];
  for (const m of String(markdown || "").matchAll(LINK_MD)) {
    const raw = m[2].trim();
    const href = raw.split(/\s+/)[0];
    if (!href) continue;
    links.push({ text: m[1], href });
  }
  return links;
}

export function classifyHref(href) {
  const bruto = href.split("#")[0];
  if (!bruto) return { kind: "empty", href };
  if (/^mailto:/i.test(bruto)) return { kind: "mailto", href: bruto };
  if (/^(https?:)?\/\//i.test(bruto) || /^https?:/i.test(bruto)) {
    return { kind: "external", href: bruto };
  }
  if (bruto.startsWith("/")) return { kind: "root-absolute", href: bruto };
  return { kind: "relative", href: bruto };
}

export async function walkMarkdownFiles(root = CURSO_ROOT) {
  const out = [];
  async function walk(dir) {
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (SKIP_DIR.has(entry.name)) continue;
      const abs = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(abs);
        continue;
      }
      if (entry.isFile() && entry.name.toLowerCase().endsWith(".md")) {
        out.push(abs);
      }
    }
  }
  await walk(root);
  return out;
}

export async function collectInternalLinkIssues() {
  const files = await walkMarkdownFiles(CURSO_ROOT);
  const missing = [];
  for (const abs of files) {
    const md = await readFile(abs, "utf8");
    const base = path.dirname(abs);
    const rel = path.relative(REPO_ROOT, abs);
    for (const { href } of extractMarkdownLinks(md)) {
      const classified = classifyHref(href);
      if (classified.kind !== "relative") continue;
      let decoded = classified.href;
      try {
        decoded = decodeURIComponent(classified.href);
      } catch {
        /* keep */
      }
      const alvo = path.resolve(base, decoded);
      let exists = false;
      try {
        await stat(alvo);
        exists = true;
      } catch {
        exists = false;
      }
      if (!exists) {
        missing.push({ from: rel, href: classified.href, target: alvo });
      } else if (!isInsideRoot(alvo, REPO_ROOT)) {
        missing.push({
          from: rel,
          href: classified.href,
          target: alvo,
          reason: "fora-do-repo",
        });
      }
    }
  }
  return missing;
}
