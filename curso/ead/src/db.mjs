import { chmodSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import { migrate } from "./migrate.mjs";

export function openDb(file) {
  mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec("PRAGMA foreign_keys = ON;");
  db.exec("PRAGMA journal_mode = WAL;");
  db.exec("PRAGMA busy_timeout = 5000;");
  db.exec("PRAGMA synchronous = NORMAL;");
  migrate(db);
  tightenData(file);
  return db;
}

export function tightenData(file) {
  try {
    chmodSync(path.dirname(file), 0o700);
    if (existsSync(file)) chmodSync(file, 0o600);
    for (const ext of ["-wal", "-shm"]) {
      const side = file + ext;
      if (existsSync(side)) chmodSync(side, 0o600);
    }
  } catch {
    /* filesystem sem dono POSIX; o piloto em Darwin/Linux aplica 0600/0700 */
  }
}

export function nowIso(date = new Date()) {
  return date.toISOString();
}
