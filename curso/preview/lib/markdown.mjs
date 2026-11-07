import { existsSync, realpathSync } from "node:fs";
import path from "node:path";
import { marked } from "marked";
import {
  ARQUIVOS_EXT_OK,
  CURSO_ROOT,
  REPO_ROOT,
  isInsideRoot,
  toPosix,
} from "./paths.mjs";

marked.setOptions({ gfm: true, breaks: false });

export function extractTitle(markdown, fallback) {
  const match = String(markdown || "").match(/^#\s+(.+)$/m);
  if (!match) return fallback;
  return match[1].replace(/[*_`]/g, "").trim();
}

export function stripHomeHeroDuplicate(html, rel) {
  if (rel !== "README.md") return html;
  return html.replace(/<p>\s*<img[^>]*curso-capa-hero[^>]*>\s*<\/p>/i, "");
}

/**
 * Resolve a request path to a markdown file under curso/.
 * Rejects absolute paths, NUL bytes and anything that escapes CURSO_ROOT.
 */
export function resolveMarkdownPath(rawPath, cursoRoot = CURSO_ROOT) {
  if (typeof rawPath !== "string" || !rawPath.trim()) {
    const err = new Error("Informe um caminho de markdown em ?path=");
    err.status = 400;
    throw err;
  }

  const trimmed = rawPath.trim();
  if (trimmed.includes("\0") || trimmed.includes("\\") || /%2e|%2f|%5c|%00/i.test(trimmed)) {
    const err = new Error("Caminho inválido.");
    err.status = 400;
    throw err;
  }

  if (path.isAbsolute(trimmed) || /^[a-zA-Z]:[\\/]/.test(trimmed)) {
    const err = new Error("Caminho fora do pacote do curso.");
    err.status = 403;
    throw err;
  }

  const resolved = path.resolve(cursoRoot, trimmed);
  if (!isInsideRoot(resolved, cursoRoot)) {
    const err = new Error("Caminho fora do pacote do curso.");
    err.status = 403;
    throw err;
  }

  if (path.extname(resolved).toLowerCase() !== ".md") {
    const err = new Error("Apenas arquivos Markdown (.md) são permitidos.");
    err.status = 400;
    throw err;
  }

  let abs = resolved;
  if (existsSync(resolved)) {
    const real = realpathSync(resolved);
    const rootReal = realpathSync(cursoRoot);
    if (!isInsideRoot(real, rootReal) || path.basename(real).startsWith(".env")) {
      const err = new Error("Caminho fora do pacote do curso.");
      err.status = 403;
      throw err;
    }
    abs = real;
  }

  return {
    abs,
    rel: toPosix(path.relative(cursoRoot, resolved)),
  };
}

export function parseLocalUrl(url) {
  const cleaned = String(url || "")
    .trim()
    .replace(/\\/g, "/");
  if (!cleaned) return null;
  if (/^(https?:|data:|mailto:|tel:|#|\/\/)/i.test(cleaned)) return null;
  if (cleaned.startsWith("/media/")) return { kind: "media-abs", href: cleaned };
  if (cleaned.startsWith("/arquivos/")) {
    return { kind: "arquivos-abs", href: cleaned };
  }
  if (cleaned.startsWith("/")) return null;

  const hashIndex = cleaned.indexOf("#");
  const queryIndex = cleaned.indexOf("?");
  let end = cleaned.length;
  if (hashIndex >= 0) end = Math.min(end, hashIndex);
  if (queryIndex >= 0) end = Math.min(end, queryIndex);
  return {
    kind: "relative",
    href: cleaned.slice(0, end),
    suffix: cleaned.slice(end),
  };
}

export function resolveRepoFile(url, mdRelPath, cursoRoot = CURSO_ROOT, repoRoot = REPO_ROOT) {
  const parsed = parseLocalUrl(url);
  if (!parsed || parsed.kind !== "relative") return parsed;

  const mdDir = path.posix.dirname(mdRelPath);
  const joined = path.posix.normalize(path.posix.join(mdDir, parsed.href));
  const absFromCurso = path.resolve(cursoRoot, joined);
  const insideCurso = isInsideRoot(absFromCurso, cursoRoot);
  const insideRepo = isInsideRoot(absFromCurso, repoRoot);

  return {
    kind: "relative",
    href: parsed.href,
    suffix: parsed.suffix || "",
    joined,
    abs: absFromCurso,
    insideCurso,
    insideRepo,
    relRepo: insideRepo ? toPosix(path.relative(repoRoot, absFromCurso)) : null,
    ext: path.extname(absFromCurso).toLowerCase(),
  };
}

/**
 * Point relative media paths at /media/, in-package .md at hash routes,
 * and in-repo PDFs at /arquivos/… so they do not 404 as JSON and break the shell.
 */
export function rewriteHtml(
  html,
  mdRelPath,
  { arquivosPrefix = "/arquivos/" } = {}
) {
  return String(html || "").replace(/\s(src|href)="([^"]*)"/gi, (full, attr, url) => {
    const parsed = parseLocalUrl(url);
    if (!parsed) return full;

    if (parsed.kind === "media-abs" || parsed.kind === "arquivos-abs") {
      return ` ${attr}="${parsed.href}"`;
    }

    const resolved = resolveRepoFile(url, mdRelPath);
    if (!resolved || resolved.kind !== "relative") return full;

    const attrName = attr.toLowerCase();
    const suffix = resolved.suffix || "";
    const target = resolved.joined;

    if (target === "media" || target.startsWith("media/")) {
      return ` ${attr}="/${target}${suffix}"`;
    }

    if (
      attrName === "href" &&
      resolved.ext === ".pdf" &&
      resolved.insideRepo &&
      ARQUIVOS_EXT_OK.has(resolved.ext)
    ) {
      const encoded = resolved.relRepo
        .split("/")
        .map((part) => encodeURIComponent(part))
        .join("/");
      return ` ${attr}="${arquivosPrefix}${encoded}${suffix}" target="_blank" rel="noopener"`;
    }

    if (attrName === "href" && target.toLowerCase().endsWith(".md") && resolved.insideCurso) {
      return ` ${attr}="#/${target}${suffix}"`;
    }

    if (attrName === "href" && target.toLowerCase().endsWith(".md") && !resolved.insideCurso) {
      return ` ${attr}="#/fora:${resolved.relRepo || target}${suffix}"`;
    }

    return full;
  });
}

export function renderMarkdownPage(markdown, rel) {
  const html = stripHomeHeroDuplicate(rewriteHtml(marked.parse(markdown), rel), rel);
  return {
    path: rel,
    title: extractTitle(markdown, rel),
    html,
  };
}

export function arquivosRelFromRequest(raw) {
  if (typeof raw !== "string" || !raw.trim() || raw.includes("\0")) {
    const err = new Error("Caminho de arquivo inválido.");
    err.status = 400;
    throw err;
  }
  if (/%2e|%2f|%5c|%00/i.test(raw)) {
    const err = new Error("Caminho de arquivo inválido.");
    err.status = 400;
    throw err;
  }
  let decoded = raw;
  try {
    decoded = decodeURIComponent(raw);
  } catch {
    const err = new Error("Caminho de arquivo inválido.");
    err.status = 400;
    throw err;
  }
  decoded = decoded.replace(/^\/+/, "");
  if (path.isAbsolute(decoded) || /^[a-zA-Z]:[\\/]/.test(decoded)) {
    const err = new Error("Caminho fora do repositório.");
    err.status = 403;
    throw err;
  }
  let abs = path.resolve(REPO_ROOT, decoded);
  if (!isInsideRoot(abs, REPO_ROOT)) {
    const err = new Error("Caminho fora do repositório.");
    err.status = 403;
    throw err;
  }
  const ext = path.extname(abs).toLowerCase();
  if (!ARQUIVOS_EXT_OK.has(ext)) {
    const err = new Error("Apenas PDF do repositório é servido em /arquivos/.");
    err.status = 400;
    throw err;
  }
  if (existsSync(abs)) {
    const real = realpathSync(abs);
    const rootReal = realpathSync(REPO_ROOT);
    const base = path.basename(real);
    if (!isInsideRoot(real, rootReal) || base === ".env" || base.startsWith(".env.") || base.endsWith(".sqlite")) {
      const err = new Error("Caminho fora do repositório.");
      err.status = 403;
      throw err;
    }
    abs = real;
  }
  return {
    abs,
    rel: toPosix(path.relative(REPO_ROOT, abs)),
  };
}
