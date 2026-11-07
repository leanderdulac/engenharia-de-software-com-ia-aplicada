import { existsSync, openSync, readSync, closeSync, readFileSync } from "node:fs";
import path from "node:path";
import { EAD_ROOT } from "./config.mjs";

export const APOIO_DIR = path.join(EAD_ROOT, "apoio");

const NOME = /^[a-z0-9][a-z0-9.-]{0,80}\.pdf$/i;

function nomeSeguro(arquivo) {
  return typeof arquivo === "string" && NOME.test(arquivo) && !arquivo.includes("..") && !arquivo.includes("/") && !arquivo.includes("\\");
}

export function loadApoio() {
  const abs = path.join(APOIO_DIR, "manifest.json");
  if (!existsSync(abs)) return [];
  let raw;
  try {
    raw = JSON.parse(readFileSync(abs, "utf8"));
  } catch {
    return [];
  }
  const list = Array.isArray(raw.materiais) ? raw.materiais : [];
  return list
    .filter((m) => m && typeof m.id === "string" && /^[a-z0-9-]{1,40}$/.test(m.id))
    .map((m) => {
      const ok = nomeSeguro(m.arquivo);
      const file = ok ? path.join(APOIO_DIR, m.arquivo) : null;
      const dentro = file && path.resolve(file).startsWith(path.resolve(APOIO_DIR) + path.sep);
      return {
        id: m.id,
        modulo: m.modulo || null,
        titulo: String(m.titulo || "Material de apoio").slice(0, 120),
        arquivo: ok ? m.arquivo : null,
        disponivel: Boolean(dentro && existsSync(file) && pdfDeVerdade(file)),
      };
    });
}

export function apoioPorId(id) {
  return loadApoio().find((m) => m.id === id) || null;
}

export function apoioDoModulo(modulo) {
  return loadApoio().find((m) => m.modulo === modulo) || null;
}

export function caminhoApoio(item) {
  if (!item?.arquivo || !item.disponivel) return null;
  const abs = path.resolve(APOIO_DIR, item.arquivo);
  if (!abs.startsWith(path.resolve(APOIO_DIR) + path.sep)) return null;
  if (!existsSync(abs) || !pdfDeVerdade(abs)) return null;
  return abs;
}

function pdfDeVerdade(abs) {
  let fd;
  try {
    fd = openSync(abs, "r");
    const buf = Buffer.alloc(5);
    const n = readSync(fd, buf, 0, 5, 0);
    return n === 5 && buf.toString("ascii") === "%PDF-";
  } catch {
    return false;
  } finally {
    if (fd !== undefined) closeSync(fd);
  }
}

export function contentDisposition(filename) {
  const ascii = String(filename).replace(/[^\x20-\x7e]/g, "_").replace(/["\\]/g, "_");
  return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(filename)}`;
}
