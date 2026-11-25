import { mkdtempSync } from "node:fs";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import path from "node:path";
import { boot } from "../src/server.mjs";

export const DEMO = {
  instructor: "Instrutor-Demo-teste-10",
  alunoA: "AlunoA-Demo-teste-10",
  alunoB: "AlunoB-Demo-teste-10",
  admin: "Admin-Demo-teste-10",
};

export class Jar {
  constructor() {
    this.map = new Map();
  }
  header() {
    return [...this.map.entries()].map(([k, v]) => `${k}=${v}`).join("; ");
  }
  capture(res) {
    const list = typeof res.headers.getSetCookie === "function" ? res.headers.getSetCookie() : [];
    for (const c of list) {
      const nv = c.split(";")[0];
      const i = nv.indexOf("=");
      if (i > 0) this.map.set(nv.slice(0, i).trim(), nv.slice(i + 1).trim());
    }
  }
}

export function csrfFrom(html) {
  const m = String(html).match(/name="csrf"\s+value="([^"]+)"/);
  return m ? m[1] : "";
}

export async function listenApp(app) {
  const port = await new Promise((resolve, reject) => {
    const s = createServer();
    s.listen(0, "127.0.0.1", () => {
      const { port: p } = s.address();
      s.close((err) => (err ? reject(err) : resolve(p)));
    });
  });
  const server = await new Promise((resolve) => {
    const httpd = app.listen(port, "127.0.0.1", () => resolve(httpd));
  });
  return { server, origin: `http://127.0.0.1:${port}` };
}

export async function startHarness(t) {
  const dir = mkdtempSync(path.join(tmpdir(), "ead-test-"));
  const { app, db } = boot({
    dbPath: path.join(dir, "ead.sqlite"),
    seedDemoPasswords: {
      instructor: DEMO.instructor,
      alunoA: DEMO.alunoA,
      alunoB: DEMO.alunoB,
    },
    createAdminOpts: {
      email: "admin.demo@local.test",
      password: DEMO.admin,
      name: "DEMONSTRAÇÃO/TESTE — Admin",
    },
  });
  const { server, origin } = await listenApp(app);
  t.after(() => {
    server.close();
    try {
      db.close();
    } catch {
      /* já fechado */
    }
  });
  return { origin, db };
}

export async function grab(origin, jar, url, opts = {}) {
  const res = await fetch(origin + url, {
    ...opts,
    redirect: "manual",
    headers: {
      ...(opts.headers || {}),
      cookie: jar.header(),
    },
  });
  jar.capture(res);
  const text = await res.text();
  return { res, text, location: res.headers.get("location") };
}

export async function login(origin, jar, email, password) {
  const page = await grab(origin, jar, "/entrar");
  const csrf = csrfFrom(page.text);
  return grab(origin, jar, "/entrar", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ email, password, csrf, next: "/dashboard" }),
  });
}

export async function follow(origin, jar, url) {
  let current = url;
  for (let i = 0; i < 6; i++) {
    const r = await grab(origin, jar, current);
    if (r.res.status >= 300 && r.res.status < 400 && r.location) {
      current = r.location.startsWith("http") ? new URL(r.location).pathname + new URL(r.location).search : r.location;
      continue;
    }
    return r;
  }
  throw new Error("redirect loop");
}
