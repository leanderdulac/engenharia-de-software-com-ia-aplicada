import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { marked } from "marked";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PREVIEW_ROOT = __dirname;
const PUBLIC_DIR = path.join(PREVIEW_ROOT, "public");
const CURSO_ROOT = path.resolve(PREVIEW_ROOT, "..");
const MEDIA_DIR = path.join(CURSO_ROOT, "media");
const PORT = Number.parseInt(process.env.PORT, 10) || 3847;

marked.setOptions({ gfm: true, breaks: false });

function toPosix(filePath) {
  return filePath.split(path.sep).join("/");
}

function isInsideRoot(candidate, root) {
  const rel = path.relative(root, candidate);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

/**
 * Resolve a request path to a markdown file under curso/.
 * Rejects absolute paths, NUL bytes and anything that escapes CURSO_ROOT.
 */
export function resolveMarkdownPath(rawPath) {
  if (typeof rawPath !== "string" || !rawPath.trim()) {
    const err = new Error("Informe um caminho de markdown em ?path=");
    err.status = 400;
    throw err;
  }

  const trimmed = rawPath.trim();
  if (trimmed.includes("\0")) {
    const err = new Error("Caminho inválido.");
    err.status = 400;
    throw err;
  }

  if (path.isAbsolute(trimmed) || /^[a-zA-Z]:[\\/]/.test(trimmed)) {
    const err = new Error("Caminho fora do pacote do curso.");
    err.status = 403;
    throw err;
  }

  const resolved = path.resolve(CURSO_ROOT, trimmed);
  if (!isInsideRoot(resolved, CURSO_ROOT)) {
    const err = new Error("Caminho fora do pacote do curso.");
    err.status = 403;
    throw err;
  }

  if (path.extname(resolved).toLowerCase() !== ".md") {
    const err = new Error("Apenas arquivos Markdown (.md) são permitidos.");
    err.status = 400;
    throw err;
  }

  return {
    abs: resolved,
    rel: toPosix(path.relative(CURSO_ROOT, resolved)),
  };
}

function resolveLocalUrl(url, mdRelPath) {
  const cleaned = String(url || "")
    .trim()
    .replace(/\\/g, "/");
  if (!cleaned) return null;
  if (/^(https?:|data:|mailto:|tel:|#|\/\/)/i.test(cleaned)) return null;
  if (cleaned.startsWith("/media/")) return { kind: "media", href: cleaned };
  if (cleaned.startsWith("/")) return null;

  const hashIndex = cleaned.indexOf("#");
  const queryIndex = cleaned.indexOf("?");
  let end = cleaned.length;
  if (hashIndex >= 0) end = Math.min(end, hashIndex);
  if (queryIndex >= 0) end = Math.min(end, queryIndex);
  const withoutSuffix = cleaned.slice(0, end);
  const suffix = cleaned.slice(end);

  const mdDir = path.posix.dirname(mdRelPath);
  const joined = path.posix.normalize(path.posix.join(mdDir, withoutSuffix));
  if (joined.startsWith("../") || joined === "..") return null;

  return { kind: "local", href: joined, suffix };
}

/**
 * Point relative media paths at /media/ and in-package .md links at hash routes.
 */
export function rewriteHtml(html, mdRelPath) {
  return html.replace(/\s(src|href)="([^"]*)"/gi, (full, attr, url) => {
    const resolved = resolveLocalUrl(url, mdRelPath);
    if (!resolved) return full;

    if (resolved.kind === "media") {
      return ` ${attr}="${resolved.href}"`;
    }

    const target = resolved.href;
    const suffix = resolved.suffix || "";
    const attrName = attr.toLowerCase();

    if (target === "media" || target.startsWith("media/")) {
      return ` ${attr}="/${target}${suffix}"`;
    }

    if (attrName === "href" && target.toLowerCase().endsWith(".md")) {
      return ` ${attr}="#/${target}${suffix}"`;
    }

    return full;
  });
}

function extractTitle(markdown, fallback) {
  const match = markdown.match(/^#\s+(.+)$/m);
  if (!match) return fallback;
  return match[1].replace(/[*_`]/g, "").trim();
}

function stripHomeHeroDuplicate(html, rel) {
  if (rel !== "README.md") return html;
  return html.replace(/<p>\s*<img[^>]*curso-capa-hero[^>]*>\s*<\/p>/i, "");
}

async function handlePage(req, res) {
  try {
    const { abs, rel } = resolveMarkdownPath(req.query.path);
    let markdown;
    try {
      markdown = await fs.readFile(abs, "utf8");
    } catch (ioErr) {
      if (ioErr && ioErr.code === "ENOENT") {
        const err = new Error(`Arquivo não encontrado: ${rel}`);
        err.status = 404;
        throw err;
      }
      throw ioErr;
    }

    const html = stripHomeHeroDuplicate(
      rewriteHtml(marked.parse(markdown), rel),
      rel
    );

    res.json({
      path: rel,
      title: extractTitle(markdown, rel),
      html,
    });
  } catch (err) {
    const status = err.status || 500;
    res.status(status).json({
      error: true,
      message: err.message || "Falha ao ler a página.",
    });
  }
}

const app = express();
app.disable("x-powered-by");

const GROK_MANIFEST = path.join(MEDIA_DIR, "videos", "grok", "manifest.json");
const TTS_MANIFEST = path.join(MEDIA_DIR, "audios", "tts", "manifest.json");

const MODULE_TITLES = {
  "01": "Fundamentos de IA e LLMs",
  "02": "Integração de APIs de LLMs",
  "03": "MCP na prática",
  "04": "Agentes autônomos",
  "05": "IA para UI/UX",
  "06": "AIOps e engenharia agêntica",
  "07": "Gestão de projetos com IA",
  "08": "Arquitetura de sistemas com IA",
  "09": "Dados e fine-tuning",
};

async function handleGrokVideos(_req, res) {
  try {
    const raw = await fs.readFile(GROK_MANIFEST, "utf8");
    const items = JSON.parse(raw);
    if (!Array.isArray(items)) {
      throw new Error("manifest.json inválido: esperado um array.");
    }

    const videos = items.map((item) => {
      const modulo = String(item.modulo || "").padStart(2, "0");
      const file = path.basename(item.file || `modulo-${modulo}-intro.mp4`);
      if (!/^modulo-\d{2}-intro\.mp4$/.test(file)) {
        throw new Error(`Arquivo Grok inválido no manifesto: ${file}`);
      }
      return {
        modulo,
        title: MODULE_TITLES[modulo] || `Módulo ${modulo}`,
        file,
        src: `/media/videos/grok/${file}`,
        request_id: item.request_id || null,
        duration: item.duration ?? null,
        status: item.status || null,
      };
    });

    res.json({
      source: "Grok Imagine (xAI)",
      videos,
    });
  } catch (err) {
    const status = err.code === "ENOENT" ? 404 : 500;
    res.status(status).json({
      error: true,
      message:
        status === 404
          ? "Manifesto Grok não encontrado em media/videos/grok/manifest.json."
          : err.message || "Falha ao ler as intros Grok.",
    });
  }
}

function toPreviewPath(sourcePath) {
  const posix = String(sourcePath || "")
    .trim()
    .replace(/\\/g, "/");
  if (!posix) return null;
  return posix.replace(/^curso\//, "");
}

async function handleTtsAudios(_req, res) {
  try {
    const raw = await fs.readFile(TTS_MANIFEST, "utf8");
    const data = JSON.parse(raw);
    const items = Array.isArray(data) ? data : data.files;
    if (!Array.isArray(items)) {
      throw new Error("manifest.json inválido: esperado um array em files.");
    }

    const audios = items.map((item) => {
      const modulo = String(item.modulo || "").replace(/^modulo-/, "").padStart(2, "0");
      const file = path.basename(item.file || `modulo-${modulo}-narracao.mp3`);
      if (!/^modulo-\d{2}-narracao\.mp3$/.test(file)) {
        throw new Error(`Arquivo TTS inválido no manifesto: ${file}`);
      }
      const vtt = path.basename(item.vtt || `modulo-${modulo}-narracao.vtt`);
      if (!/^modulo-\d{2}-narracao\.vtt$/.test(vtt)) {
        throw new Error(`Legenda VTT inválida no manifesto: ${vtt}`);
      }
      return {
        modulo,
        title: MODULE_TITLES[modulo] || `Módulo ${modulo}`,
        file,
        src: `/media/audios/tts/${file}`,
        vtt,
        vtt_src: `/media/audios/tts/${vtt}`,
        source_path: toPreviewPath(item.source_path),
        voice: item.voice || data.voice || "pt-BR-FranciscaNeural",
        rate: item.rate || data.rate || "-18%",
        pitch: item.pitch || data.pitch || "-2Hz",
        duration_seconds: item.duration_seconds ?? null,
        bytes: item.bytes ?? null,
        status: item.status || null,
      };
    });

    res.json({
      source: "Azure Neural TTS",
      voice: data.voice || "pt-BR-FranciscaNeural",
      rate: data.rate || "-18%",
      pitch: data.pitch || "-2Hz",
      audios,
    });
  } catch (err) {
    const status = err.code === "ENOENT" ? 404 : 500;
    res.status(status).json({
      error: true,
      message:
        status === 404
          ? "Manifesto TTS não encontrado em media/audios/tts/manifest.json."
          : err.message || "Falha ao ler as narrações TTS.",
    });
  }
}

app.get("/api/page", handlePage);
app.get("/api/grok-videos", handleGrokVideos);
app.get("/api/tts-audios", handleTtsAudios);

express.static.mime.define({ "text/vtt": ["vtt"] });

app.use(
  "/media",
  express.static(MEDIA_DIR, {
    index: false,
    dotfiles: "deny",
    fallthrough: false,
    setHeaders(res, filePath) {
      if (path.extname(filePath).toLowerCase() === ".vtt") {
        res.setHeader("Content-Type", "text/vtt; charset=utf-8");
      }
    },
  })
);

app.use(express.static(PUBLIC_DIR, { index: "index.html" }));

app.use((req, res) => {
  res.status(404).json({ error: true, message: "Recurso não encontrado." });
});

const server = app.listen(PORT, () => {
  console.log(`Preview do curso em http://localhost:${PORT}`);
  console.log(`Pacote servido a partir de ${CURSO_ROOT}`);
});

server.on("error", (err) => {
  console.error(err);
  process.exit(1);
});
