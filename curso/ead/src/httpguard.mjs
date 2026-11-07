import { randomBytes } from "node:crypto";

const WINDOW_MS = 60_000;
const MAX_POSTS = 180;
const buckets = new Map();

export function securityHeaders(_req, res, next) {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "same-origin");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
  );
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
        path: req.path,
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
  if (bucket.n > MAX_POSTS) {
    res.status(429).type("text/plain").send("Demasiados pedidos. Espere um minuto.");
    return;
  }
  next();
}

export function resetRateBuckets() {
  buckets.clear();
}
