import { randomBytes } from "node:crypto";

const WINDOW_MS = 60_000;
const MAX_POSTS = 180;
const buckets = new Map();

export function hostnameOf(hostHeader) {
  const raw = String(hostHeader || "").trim().toLowerCase();
  if (!raw || raw.includes("/") || raw.includes("\\") || raw.includes("@")) return "";
  if (raw.startsWith("[")) {
    const end = raw.indexOf("]");
    return end > 0 ? raw.slice(0, end + 1) : "";
  }
  const colon = raw.lastIndexOf(":");
  if (colon > -1 && /^\d+$/.test(raw.slice(colon + 1))) return raw.slice(0, colon);
  return raw;
}

export function allowedHosts(env = process.env) {
  const raw = env.EAD_ALLOWED_HOSTS || "127.0.0.1,localhost,[::1]";
  return new Set(
    raw
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean)
  );
}

export function hostGuard(req, res, next) {
  const name = hostnameOf(req.headers.host);
  if (!allowedHosts().has(name)) {
    res.status(421).type("text/plain; charset=utf-8").send("Host recusado.");
    return;
  }
  if (req.method === "GET" || req.method === "HEAD" || req.method === "OPTIONS") return next();
  const origin = req.headers.origin;
  if (!origin) return next();
  let url;
  try {
    url = new URL(origin);
  } catch {
    res.status(403).type("text/plain; charset=utf-8").send("Origin recusada.");
    return;
  }
  const bare = name.replace(/^\[|\]$/g, "");
  if (url.hostname.toLowerCase() !== bare) {
    res.status(403).type("text/plain; charset=utf-8").send("Origin recusada.");
    return;
  }
  next();
}

export function securityHeaders(_req, res, next) {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "same-origin");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
  );
  res.setHeader("Cross-Origin-Resource-Policy", "same-origin");
  res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
  res.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  next();
}

export function requestLog(req, res, next) {
  const id = randomBytes(8).toString("hex");
  const start = Date.now();
  res.setHeader("X-Request-Id", id);
  res.on("finish", () => {
    if (process.env.NODE_TEST_CONTEXT) return;
    if (req.path === "/healthz" || req.path === "/readyz") return;
    console.log(
      JSON.stringify({
        t: new Date().toISOString(),
        id,
        method: req.method,
        path: String(req.path || "").replace(/[\r\n]/g, "").slice(0, 200),
        status: res.statusCode,
        ms: Date.now() - start,
      })
    );
  });
  next();
}

export function postRateLimit(req, res, next) {
  if (req.method !== "POST") return next();
  const now = Date.now();
  const key = req.ip || "0";
  let bucket = buckets.get(key);
  if (!bucket || now - bucket.start > WINDOW_MS) {
    bucket = { start: now, n: 0 };
    buckets.set(key, bucket);
  }
  bucket.n += 1;
  if (buckets.size > 5000) buckets.clear();
  if (bucket.n > MAX_POSTS) {
    res.status(429).type("text/plain").send("Demasiados pedidos. Espere um minuto.");
    return;
  }
  next();
}

export function hitLimit(key, max, windowMs = WINDOW_MS) {
  const now = Date.now();
  let bucket = buckets.get(key);
  if (!bucket || now - bucket.start > windowMs) {
    bucket = { start: now, n: 0 };
    buckets.set(key, bucket);
  }
  bucket.n += 1;
  if (buckets.size > 5000) buckets.clear();
  return bucket.n > max;
}

export function resetRateBuckets() {
  buckets.clear();
}
