import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

export const PREVIEW_ROOT = path.resolve(HERE, "..");
export const PUBLIC_DIR = path.join(PREVIEW_ROOT, "public");
export const CURSO_ROOT = path.resolve(PREVIEW_ROOT, "..");
export const REPO_ROOT = path.resolve(CURSO_ROOT, "..");
export const MEDIA_DIR = path.join(CURSO_ROOT, "media");

export function toPosix(filePath) {
  return filePath.split(path.sep).join("/");
}

export function isInsideRoot(candidate, root) {
  const rel = path.relative(root, candidate);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

export const ARQUIVOS_EXT_OK = new Set([".pdf"]);
