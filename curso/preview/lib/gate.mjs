/**
 * Portão reversível do preview.
 * Desligado (omissão, testes, leitura local): o preview continua aberto.
 * PREVIEW_REQUIRE_AUTH=1: páginas, API, markdown, mídia e PDFs exigem
 * o cookie ead_sid da mesma base SQLite da sala (EAD_DATA_DIR ou PREVIEW_AUTH_DB).
 * NODE_ENV=production recusa escutar sem esse portão e sem o caminho da base.
 */

let dbPromise = null;

function authRequired(env = process.env) {
  return env.PREVIEW_REQUIRE_AUTH === "1";
}

export function assertPreviewListen(env = process.env) {
  if (env.NODE_ENV !== "production") return;
  if (!authRequired(env) || (!env.PREVIEW_AUTH_DB && !env.EAD_DATA_DIR)) {
    throw new Error(
      "Preview em produção exige PREVIEW_REQUIRE_AUTH=1 e PREVIEW_AUTH_DB ou EAD_DATA_DIR (mesma base da sala)."
    );
  }
}

function protects(req) {
  const p = req.path || "/";
  if (p.startsWith("/api/") || p.startsWith("/media") || p.startsWith("/arquivos")) return true;
  if (p.toLowerCase().endsWith(".md")) return true;
  // CSS/JS do casco não trazem o material. Qualquer outra rota (/, HTML, fallback) sim.
  if (/\.(css|js|map|ico|webmanifest)$/i.test(p)) return false;
  return true;
}

async function sessionDb() {
  if (!dbPromise) {
    dbPromise = (async () => {
      const { openDb } = await import("../../ead/src/db.mjs");
      if (process.env.PREVIEW_AUTH_DB) return openDb(process.env.PREVIEW_AUTH_DB);
      const { dbFile } = await import("../../ead/src/config.mjs");
      return openDb(dbFile());
    })();
  }
  return dbPromise;
}

export function resetPreviewGate() {
  dbPromise = null;
}

export async function previewContentGate(req, res, next) {
  if (!authRequired() || !protects(req)) return next();
  try {
    const db = await sessionDb();
    const { loadSession, parseCookies } = await import("../../ead/src/auth.mjs");
    const session = loadSession(db, parseCookies(req.headers.cookie || "").ead_sid);
    if (!session?.user || session.user.disabled) {
      res.status(401).type("text/plain; charset=utf-8").send("Autenticação necessária.");
      return;
    }
    return next();
  } catch {
    res.status(401).type("text/plain; charset=utf-8").send("Autenticação necessária.");
  }
}
