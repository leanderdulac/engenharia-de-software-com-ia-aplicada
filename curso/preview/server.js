import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  CURSO_ROOT,
  MEDIA_DIR,
  PUBLIC_DIR,
} from "./lib/paths.mjs";
import {
  arquivosRelFromRequest,
  extractTitle,
  renderMarkdownPage,
  resolveMarkdownPath,
  stripHomeHeroDuplicate,
} from "./lib/markdown.mjs";

const PORT = Number.parseInt(process.env.PORT, 10) || 3847;
const HOST = process.env.HOST || "0.0.0.0";

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

    if (String(req.query.raw) === "1") {
      res.setHeader("Content-Type", "text/markdown; charset=utf-8");
      res.send(markdown);
      return;
    }

    res.json(renderMarkdownPage(markdown, rel));
  } catch (err) {
    const status = err.status || 500;
    res.status(status).json({
      error: true,
      message: err.message || "Falha ao ler a página.",
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

export async function grokVideosPayload() {
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
      src: `media/videos/grok/${file}`,
      request_id: item.request_id || null,
      duration: item.duration ?? null,
      status: item.status || null,
    };
  });

  return { source: "Grok Imagine (xAI)", videos };
}

export async function ttsAudiosPayload() {
  const raw = await fs.readFile(TTS_MANIFEST, "utf8");
  const data = JSON.parse(raw);
  const items = Array.isArray(data) ? data : data.files;
  if (!Array.isArray(items)) {
    throw new Error("manifest.json inválido: esperado um array em files.");
  }

  const audios = items.map((item) => {
    const modulo = String(item.modulo || "")
      .replace(/^modulo-/, "")
      .padStart(2, "0");
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
      src: `media/audios/tts/${file}`,
      vtt,
      vtt_src: `media/audios/tts/${vtt}`,
      source_path: toPreviewPath(item.source_path),
      voice: item.voice || data.voice || "pt-BR-FranciscaNeural",
      rate: item.rate || data.rate || "-18%",
      pitch: item.pitch || data.pitch || "-2Hz",
      duration_seconds: item.duration_seconds ?? null,
      bytes: item.bytes ?? null,
      status: item.status || null,
    };
  });

  return {
    source: "Azure Neural TTS",
    voice: data.voice || "pt-BR-FranciscaNeural",
    rate: data.rate || "-18%",
    pitch: data.pitch || "-2Hz",
    audios,
  };
}

async function handleGrokVideos(_req, res) {
  try {
    res.json(await grokVideosPayload());
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

async function handleTtsAudios(_req, res) {
  try {
    res.json(await ttsAudiosPayload());
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

async function handleArquivo(req, res) {
  try {
    const relParam = req.params[0] || "";
    const { abs, rel } = arquivosRelFromRequest(relParam);
    try {
      await fs.access(abs);
    } catch {
      const err = new Error(`PDF não encontrado: ${rel}`);
      err.status = 404;
      throw err;
    }
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.sendFile(abs);
  } catch (err) {
    const status = err.status || 500;
    res.status(status).json({
      error: true,
      message: err.message || "Falha ao ler o PDF.",
    });
  }
}

async function handleMarkdownFile(req, res, next) {
  const rel = decodeURIComponent(req.path.replace(/^\/+/, ""));
  if (!rel.toLowerCase().endsWith(".md")) return next();

  if (String(req.query.raw) === "1") {
    try {
      const { abs } = resolveMarkdownPath(rel);
      const markdown = await fs.readFile(abs, "utf8");
      res.setHeader("Content-Type", "text/markdown; charset=utf-8");
      res.send(markdown);
      return;
    } catch (err) {
      const status = err.status || (err.code === "ENOENT" ? 404 : 500);
      res.status(status).json({
        error: true,
        message: err.message || "Markdown não encontrado.",
      });
      return;
    }
  }

  const accept = req.get("accept") || "";
  if (accept.includes("text/html")) {
    res.redirect(302, `/#/${rel}`);
    return;
  }

  res.status(400).json({
    error: true,
    message:
      "Markdown não é servido como HTML. Abra /#/" +
      rel +
      " no preview ou acrescente ?raw=1 para text/markdown.",
  });
}

export function createApp() {
  const app = express();
  app.disable("x-powered-by");

  app.get("/api/page", handlePage);
  app.get("/api/grok-videos", handleGrokVideos);
  app.get("/api/tts-audios", handleTtsAudios);
  app.get(/^\/arquivos\/(.+)$/, handleArquivo);

  express.static.mime.define({
    "text/vtt": ["vtt"],
    "application/pdf": ["pdf"],
  });

  app.use(
    "/media",
    express.static(MEDIA_DIR, {
      index: false,
      dotfiles: "deny",
      fallthrough: false,
      setHeaders(res, filePath) {
        const ext = path.extname(filePath).toLowerCase();
        if (ext === ".vtt") {
          res.setHeader("Content-Type", "text/vtt; charset=utf-8");
        }
        if (ext === ".md") {
          res.setHeader("Content-Type", "text/markdown; charset=utf-8");
        }
      },
    })
  );

  app.use(
    express.static(PUBLIC_DIR, {
      index: "index.html",
      fallthrough: true,
      setHeaders(res, filePath) {
        if (path.extname(filePath).toLowerCase() === ".md") {
          res.setHeader("Content-Type", "text/markdown; charset=utf-8");
        }
      },
    })
  );

  app.get(/^\/.+\.md$/i, handleMarkdownFile);

  app.use((req, res, next) => {
    if (req.method !== "GET" && req.method !== "HEAD") return next();
    if (req.path.startsWith("/api/") || req.path.startsWith("/media/") || req.path.startsWith("/arquivos/")) {
      return next();
    }
    if (req.accepts("html")) {
      res.sendFile(path.join(PUBLIC_DIR, "index.html"));
      return;
    }
    next();
  });

  app.use((req, res) => {
    res.status(404).json({ error: true, message: "Recurso não encontrado." });
  });

  return app;
}

export { extractTitle, stripHomeHeroDuplicate, CURSO_ROOT };

function start() {
  const app = createApp();
  const server = app.listen(PORT, HOST, () => {
    const shownHost = HOST === "0.0.0.0" ? "localhost" : HOST;
    console.log(`Preview do curso em http://${shownHost}:${PORT}`);
    console.log(`Pacote servido a partir de ${CURSO_ROOT} (bind ${HOST}:${PORT})`);
  });
  server.on("error", (err) => {
    console.error(err);
    process.exit(1);
  });
  return server;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  start();
}
