import { createHash, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import { LOGIN_MAX, LOGIN_WINDOW_MS, PASSWORD_MAX, PASSWORD_MIN, SESSION_TTL_MS } from "./config.mjs";
import { nowIso } from "./db.mjs";

export function hashPassword(password) {
  const salt = randomBytes(16).toString("hex");
  const key = scryptSync(password, salt, 32, { N: 16384, r: 8, p: 1 }).toString("hex");
  return `scrypt$16384$8$1$${salt}$${key}`;
}

export function verifyPassword(password, stored) {
  const parts = String(stored || "").split("$");
  if (parts.length !== 6 || parts[0] !== "scrypt") return false;
  const [, n, r, p, salt, key] = parts;
  let derived;
  try {
    derived = scryptSync(password, salt, 32, {
      N: Number(n),
      r: Number(r),
      p: Number(p),
    });
  } catch {
    return false;
  }
  const expected = Buffer.from(key, "hex");
  if (expected.length !== derived.length) return false;
  return timingSafeEqual(expected, derived);
}

export function hashToken(token) {
  return createHash("sha256").update(token).digest("hex");
}

export function newToken() {
  return randomBytes(32).toString("hex");
}

export function validEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || "").toLowerCase());
}

export function validPassword(password) {
  const p = String(password || "");
  return p.length >= PASSWORD_MIN && p.length <= PASSWORD_MAX;
}

export function parseCookies(header) {
  const out = {};
  for (const part of String(header || "").split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    const k = part.slice(0, i).trim();
    const v = part.slice(i + 1).trim();
    if (k) out[k] = decodeURIComponent(v);
  }
  return out;
}

export function cookieHeader(name, value, { maxAge, secure }) {
  const bits = [
    `${name}=${encodeURIComponent(value)}`,
    "Path=/",
    "HttpOnly",
    "SameSite=Lax",
    `Max-Age=${Math.floor(maxAge / 1000)}`,
  ];
  if (secure) bits.push("Secure");
  return bits.join("; ");
}

export function clearCookie(name, secure) {
  return `${name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure ? "; Secure" : ""}`;
}

export function loginAllowed(db, key, now = Date.now()) {
  db.prepare("DELETE FROM login_attempts WHERE at < ?").run(now - LOGIN_WINDOW_MS);
  const rows = db.prepare("SELECT COUNT(*) AS n FROM login_attempts WHERE key = ?").get(key);
  return (rows?.n || 0) < LOGIN_MAX;
}

export function recordLoginFail(db, key, now = Date.now()) {
  db.prepare("INSERT INTO login_attempts (key, at) VALUES (?, ?)").run(key, now);
}

export function createSession(db, userId, now = Date.now()) {
  const token = newToken();
  const csrf = newToken();
  db.prepare(
    "INSERT INTO sessions (token_hash, user_id, csrf, expires_at, created_at) VALUES (?, ?, ?, ?, ?)"
  ).run(hashToken(token), userId, csrf, now + SESSION_TTL_MS, nowIso(new Date(now)));
  return { token, csrf };
}

export function loadSession(db, token, now = Date.now()) {
  if (!token) return null;
  const row = db
    .prepare(
      `SELECT s.csrf, s.expires_at, u.id, u.email, u.name, u.role, u.demo, u.diagnostic_done
       FROM sessions s JOIN users u ON u.id = s.user_id
       WHERE s.token_hash = ? AND u.disabled = 0`
    )
    .get(hashToken(token));
  if (!row || row.expires_at < now) return null;
  return {
    csrf: row.csrf,
    user: {
      id: row.id,
      email: row.email,
      name: row.name,
      role: row.role,
      demo: Boolean(row.demo),
      diagnostic_done: Boolean(row.diagnostic_done),
    },
  };
}

export function destroySession(db, token) {
  if (!token) return;
  db.prepare("DELETE FROM sessions WHERE token_hash = ?").run(hashToken(token));
}

export function destroyUserSessions(db, userId) {
  db.prepare("DELETE FROM sessions WHERE user_id = ?").run(userId);
}

export function requireCsrf(session, submitted) {
  if (!session?.csrf || !submitted) return false;
  const a = Buffer.from(String(session.csrf));
  const b = Buffer.from(String(submitted));
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
