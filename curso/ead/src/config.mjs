import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const EAD_ROOT = path.resolve(HERE, "..");
export const CURSO_ROOT = path.resolve(EAD_ROOT, "..");
export const REPO_ROOT = path.resolve(CURSO_ROOT, "..");
export const PUBLIC_DIR = path.join(EAD_ROOT, "public");

export function dataDir() {
  return path.resolve(process.env.EAD_DATA_DIR || path.join(EAD_ROOT, "data"));
}

export function dbFile(dir = dataDir()) {
  return path.join(dir, "ead.sqlite");
}

export function listenHost() {
  return process.env.HOST || "127.0.0.1";
}

export function listenPort() {
  return Number.parseInt(process.env.PORT, 10) || 3850;
}

export function secureCookies() {
  return process.env.EAD_SECURE_COOKIES === "1";
}

export const SESSION_TTL_MS = 12 * 60 * 60 * 1000;
export const LOGIN_WINDOW_MS = 15 * 60 * 1000;
export const LOGIN_MAX = 8;
export const TEXT_MAX = 8000;
export const URL_MAX = 500;
export const NAME_MAX = 80;
export const PASSWORD_MIN = 10;
export const PASSWORD_MAX = 128;
