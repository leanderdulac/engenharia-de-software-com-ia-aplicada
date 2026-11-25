import { closeSync, existsSync, openSync, readdirSync, readFileSync, readSync, realpathSync, statSync } from "node:fs";
import path from "node:path";

const MODULES = [
  ["modulo01-fundamentos-de-ia-e-llms-para-programadores", "01"],
  ["modulo02-integracao-apis-llms", "02"],
  ["modulo03-mcp-na-pratica", "03"],
  ["modulo04-criacao-de-agentes-autonomos-novo", "04"],
  ["modulo05-ferramentas-de-IA-para-UI-UX", "05"],
  ["modulo06-aiops-engenharia-agentica", "06"],
  ["modulo07-ferramentas-de-ia-para-gestao-de-projetos", "07"],
  ["modulo08-arquitetura-de-sistemas-com-ia", "08"],
  ["modulo09-processamento-de-dados-e-fine-tuning-de-modelos", "09"],
];

const ROOT_FILES = new Set(["README.md", "LICENSE.md", "NOTICE"]);
const IMAGE_EXT = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp"]);
const OMIT_EXT = new Set([
  ".mp4",
  ".mp3",
  ".wav",
  ".ogg",
  ".m4a",
  ".webm",
  ".bin",
  ".onnx",
  ".pt",
  ".safetensors",
  ".gguf",
  ".wasm",
  ".zip",
  ".gz",
  ".tgz",
  ".woff",
  ".woff2",
  ".ttf",
  ".otf",
  ".exe",
  ".dll",
  ".so",
  ".dylib",
  ".pyc",
]);
const BLOCK_SEGMENTS = new Set([
  "node_modules",
  ".git",
  "backup",
  "backups",
  "dist",
  ".next",
  "coverage",
  "__pycache__",
  ".venv",
  "venv",
]);

const TEXT_CAP = 200_000;
const IMAGE_CAP = 1_500_000;

function under(rel, prefix) {
  return rel === prefix || rel.startsWith(`${prefix}/`);
}

export function recursoPolicy(rel) {
  if (ROOT_FILES.has(rel)) return { modulo: null, enrolledOnly: true };
  if (under(rel, "curso")) {
    if (under(rel, "curso/ead")) return null;
    return { modulo: null, enrolledOnly: true };
  }
  if (under(rel, "referencia/llm-course")) return { modulo: null, enrolledOnly: true };
  if (under(rel, "troubleshooting") || under(rel, "skills/windowsfy")) return { modulo: null, enrolledOnly: true };
  if (under(rel, "lives/2026-02-24")) return { modulo: "03", enrolledOnly: false };
  if (under(rel, "lives/2026-05-27")) return { modulo: "04", enrolledOnly: false };
  if (under(rel, "lives/2026-07-28")) return { modulo: "05", enrolledOnly: false };
  if (under(rel, "lives")) return { modulo: "03", enrolledOnly: false };
  for (const [prefix, id] of MODULES) {
    if (under(rel, prefix)) return { modulo: id, enrolledOnly: false };
  }
  return null;
}

function blockedSegment(rel) {
  const parts = String(rel || "").split("/");
  for (const part of parts) {
    if (!part || part === "." || part === "..") return true;
    if (BLOCK_SEGMENTS.has(part)) return true;
    if (part === ".env" || (part.startsWith(".env.") && part !== ".env.example")) return true;
    const lower = part.toLowerCase();
    if (lower.endsWith(".sqlite") || lower.endsWith(".sqlite-wal") || lower.endsWith(".sqlite-shm")) return true;
    if (lower.endsWith(".pem") || lower.endsWith(".key") || lower === "id_rsa" || lower === "credentials.json") return true;
    if (lower.endsWith(".db")) return true;
  }
  return false;
}

export function parseRecursoPath(raw) {
  if (typeof raw !== "string" || !raw.trim() || raw.includes("\0") || raw.includes("\\") || /%2e|%2f|%5c|%00/i.test(raw)) {
    return { ok: false, status: 400, message: "Caminho inválido." };
  }
  let decoded;
  try {
    decoded = decodeURIComponent(raw);
  } catch {
    return { ok: false, status: 400, message: "Caminho inválido." };
  }
  if (decoded.includes("\0") || decoded.includes("\\") || /%2e|%2f|%5c|%00/i.test(decoded)) {
    return { ok: false, status: 400, message: "Caminho inválido." };
  }
  decoded = decoded.replace(/^\/+/, "").replace(/\/+$/, "");
  if (!decoded || path.posix.isAbsolute(decoded) || decoded.split("/").includes("..")) {
    return { ok: false, status: 403, message: "Caminho recusado." };
  }
  return { ok: true, rel: decoded };
}

function looksBinary(abs) {
  const fd = openSync(abs, "r");
  try {
    const buf = Buffer.alloc(4096);
    const n = readSync(fd, buf, 0, 4096, 0);
    return buf.subarray(0, n).includes(0);
  } finally {
    closeSync(fd);
  }
}

export function inspectRecurso(repoRoot, rel) {
  const requested = recursoPolicy(rel);
  if (!requested || blockedSegment(rel)) {
    return { status: 403, message: "Caminho recusado." };
  }
  const abs = path.resolve(repoRoot, rel);
  const relCheck = path.relative(repoRoot, abs);
  if (!relCheck || relCheck.startsWith("..") || path.isAbsolute(relCheck)) {
    return { status: 403, message: "Caminho recusado." };
  }
  if (!existsSync(abs)) {
    return {
      status: 404,
      kind: "missing",
      rel,
      modulo: requested.modulo,
      enrolledOnly: requested.enrolledOnly,
      message: "Este caminho não está nesta instalação.",
    };
  }
  let real;
  try {
    real = realpathSync(abs);
  } catch {
    return { status: 403, message: "Caminho recusado." };
  }
  const realRoot = realpathSync(repoRoot);
  const relReal = path.relative(realRoot, real).split(path.sep).join("/");
  if (!relReal || relReal.startsWith("..") || path.isAbsolute(relReal) || blockedSegment(relReal)) {
    return { status: 403, message: "Caminho recusado." };
  }
  const realPolicy = recursoPolicy(relReal);
  if (!realPolicy) return { status: 403, message: "Caminho recusado." };
  const st = statSync(real);
  const base = { rel: relReal, abs: real, modulo: realPolicy.modulo, enrolledOnly: realPolicy.enrolledOnly, size: st.size };
  if (st.isDirectory()) return { status: 200, kind: "dir", ...base };
  const ext = path.extname(real).toLowerCase();
  if (ext === ".pdf") return { status: 200, kind: "pdf", ...base };
  if (IMAGE_EXT.has(ext)) {
    if (st.size > IMAGE_CAP) return { status: 200, kind: "omitted", ...base };
    return { status: 200, kind: "image", ...base };
  }
  if (OMIT_EXT.has(ext) || st.size > TEXT_CAP || looksBinary(real)) return { status: 200, kind: "omitted", ...base };
  return { status: 200, kind: ext === ".md" ? "markdown" : "text", ...base };
}

export function listRecurso(repoRoot, rel) {
  const abs = path.resolve(repoRoot, rel);
  const entries = readdirSync(abs, { withFileTypes: true });
  const out = [];
  for (const ent of entries) {
    if (ent.name.startsWith(".") && ent.name !== ".env.example") continue;
    const child = rel ? `${rel}/${ent.name}` : ent.name;
    if (blockedSegment(child) || !recursoPolicy(child)) continue;
    let kind = "file";
    if (ent.isDirectory()) kind = "dir";
    else if (ent.isSymbolicLink()) {
      try {
        const real = realpathSync(path.join(abs, ent.name));
        const relReal = path.relative(realpathSync(repoRoot), real).split(path.sep).join("/");
        if (!relReal || relReal.startsWith("..") || !recursoPolicy(relReal) || blockedSegment(relReal)) continue;
        kind = statSync(real).isDirectory() ? "dir" : "file";
      } catch {
        continue;
      }
    }
    out.push({ name: ent.name, rel: child, kind });
  }
  out.sort((a, b) => {
    if (a.kind !== b.kind) return a.kind === "dir" ? -1 : 1;
    return a.name.localeCompare(b.name, "pt");
  });
  return out;
}

export function readRecursoText(abs) {
  const st = statSync(abs);
  if (st.size > TEXT_CAP) return { truncated: true, text: "" };
  return { truncated: false, text: readFileSync(abs, "utf8") };
}
