import { existsSync, realpathSync } from "node:fs";
import path from "node:path";

export function encodedTrick(rel) {
  return /%2e|%2f|%5c|%00/i.test(rel) || rel.includes("\0") || rel.includes("\\");
}

function blockedBase(file) {
  const base = path.basename(file);
  return (
    base === ".env" ||
    base.startsWith(".env.") ||
    base.endsWith(".sqlite") ||
    base.endsWith(".sqlite-wal") ||
    base.endsWith(".sqlite-shm") ||
    base.endsWith(".log")
  );
}

/**
 * Resolve rel dentro de root e recusa .., dupla codificação, symlink para fora
 * e ficheiros de segredo/base/log.
 */
export function safeInside(root, rel) {
  if (typeof rel !== "string" || !rel.trim() || encodedTrick(rel)) {
    const err = new Error("Caminho inválido.");
    err.status = 400;
    throw err;
  }
  const abs = path.resolve(root, rel);
  const relCheck = path.relative(root, abs);
  if (relCheck.startsWith("..") || path.isAbsolute(relCheck)) {
    const err = new Error("Caminho fora da pasta.");
    err.status = 403;
    throw err;
  }
  if (!existsSync(abs)) {
    const err = new Error("Não encontrado.");
    err.status = 404;
    throw err;
  }
  const realRoot = realpathSync(root);
  const real = realpathSync(abs);
  const relReal = path.relative(realRoot, real);
  if (relReal.startsWith("..") || path.isAbsolute(relReal) || blockedBase(real)) {
    const err = new Error("Caminho fora da pasta.");
    err.status = 403;
    throw err;
  }
  return real;
}
