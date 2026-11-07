import { hashToken, newToken } from "./auth.mjs";
import { nowIso } from "./db.mjs";

const RESET_TTL_MS = 30 * 60 * 1000;

export function audit(db, { actorId, action, target }) {
  db.prepare("INSERT INTO audit_log (actor_id, action, target, created_at) VALUES (?, ?, ?, ?)").run(
    actorId || null,
    String(action).slice(0, 64),
    String(target || "").slice(0, 200),
    nowIso()
  );
}

export function setting(db, key) {
  return db.prepare("SELECT value FROM settings WHERE key = ?").get(key)?.value ?? "";
}

export function putSetting(db, key, value) {
  db.prepare(
    "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value"
  ).run(key, String(value ?? ""));
}

export function enrollmentWindow(db, now = new Date()) {
  const starts = setting(db, "cohort_starts");
  const ends = setting(db, "cohort_ends");
  const day = now.toISOString().slice(0, 10);
  if (starts && /^\d{4}-\d{2}-\d{2}$/.test(starts) && day < starts) {
    return { open: false, reason: `Matrículas abrem em ${starts}.` };
  }
  if (ends && /^\d{4}-\d{2}-\d{2}$/.test(ends) && day > ends) {
    return { open: false, reason: `Matrículas encerraram em ${ends}.` };
  }
  return { open: true, reason: "", starts, ends, name: setting(db, "cohort_name") };
}

export function issueReset(db, userId, now = Date.now()) {
  const token = newToken();
  db.prepare("DELETE FROM password_resets WHERE user_id = ? AND used_at IS NULL").run(userId);
  db.prepare(
    "INSERT INTO password_resets (user_id, token_hash, expires_at, created_at) VALUES (?, ?, ?, ?)"
  ).run(userId, hashToken(token), now + RESET_TTL_MS, nowIso(new Date(now)));
  return token;
}

export function peekReset(db, token, now = Date.now()) {
  if (!token) return null;
  const row = db.prepare("SELECT * FROM password_resets WHERE token_hash = ?").get(hashToken(token));
  if (!row || row.used_at || row.expires_at < now) return null;
  return row;
}

export function consumeReset(db, token, now = Date.now()) {
  const row = peekReset(db, token, now);
  if (!row) return null;
  db.prepare("UPDATE password_resets SET used_at = ? WHERE id = ? AND used_at IS NULL").run(nowIso(new Date(now)), row.id);
  const again = db.prepare("SELECT used_at FROM password_resets WHERE id = ?").get(row.id);
  if (!again?.used_at) return null;
  return row.user_id;
}

export function integrityOk(db) {
  const row = db.prepare("PRAGMA integrity_check").get();
  const value = row?.integrity_check || row?.["integrity_check"];
  return value === "ok";
}

export function isoDay(value) {
  const v = String(value || "").trim();
  if (!v) return "";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) return null;
  return v;
}
