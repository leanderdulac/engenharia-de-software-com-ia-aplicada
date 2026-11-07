import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import http from "node:http";
import { mkdtempSync, mkdirSync, statSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it } from "node:test";
import { openDb } from "../src/db.mjs";
import { safeInside } from "../src/filesafe.mjs";
import { DEMO, Jar, csrfFrom, grab, login, startHarness } from "./helpers.mjs";

function raw(origin, method, urlPath, headers = {}, body = "") {
  const u = new URL(origin);
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: u.hostname,
        port: u.port,
        path: urlPath,
        method,
        headers,
      },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () =>
          resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString("utf8") })
        );
      }
    );
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

describe("ameaças do browser contra o loopback", () => {
  it("Host alheio e Origin cruzada não passam", async (t) => {
    const { origin } = await startHarness(t);
    const evil = await raw(origin, "GET", "/healthz", { host: "evil.example" });
    assert.equal(evil.status, 421);
    const page = await grab(origin, new Jar(), "/entrar");
    const csrf = csrfFrom(page.text);
    const post = await raw(origin, "POST", "/entrar", {
      host: new URL(origin).host,
      origin: "http://evil.example",
      "content-type": "application/x-www-form-urlencoded",
      cookie: page.res.headers.get("set-cookie") ? "" : "",
    }, new URLSearchParams({ email: "a@b.c", password: "0123456789", csrf }).toString());
    assert.equal(post.status, 403);
    assert.equal(post.headers["access-control-allow-origin"], undefined);
  });

  it("login não segue next externo e o flash não executa HTML", async (t) => {
    const { origin } = await startHarness(t);
    const jar = new Jar();
    const page = await grab(origin, jar, "/entrar");
    const posted = await grab(origin, jar, "/entrar", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        email: "aluno-a.demo@local.test",
        password: DEMO.alunoA,
        csrf: csrfFrom(page.text),
        next: "//evil.example/phish",
      }),
    });
    assert.equal(posted.res.status, 303);
    assert.equal(posted.location, "/dashboard");
    const xss = await grab(origin, new Jar(), "/?ok=" + encodeURIComponent("<script>alert(1)</script>"));
    assert.equal(xss.text.includes("<script>alert"), false);
    assert.match(xss.text, /&lt;script&gt;alert/);
    assert.equal(xss.res.headers.get("access-control-allow-origin"), null);
  });

  it("mídia codificada e PDF fora da árvore não saem", async (t) => {
    const { origin } = await startHarness(t);
    const jar = new Jar();
    await login(origin, jar, "aluno-a.demo@local.test", DEMO.alunoA);
    const trick = await grab(origin, jar, "/media/%252e%252e/package.json");
    assert.ok(trick.res.status === 400 || trick.res.status === 404);
    assert.equal(trick.text.includes('"name"'), false);
    const encoded = await grab(origin, jar, "/media/imagens/%252e%252e.png");
    assert.notEqual(encoded.res.status, 200);
    const ok = await grab(origin, jar, "/media/imagens/curso-capa-hero.png");
    assert.equal(ok.res.status, 200);
    const pdf = await grab(origin, jar, "/arquivos/%252e%252e/package.json");
    assert.notEqual(pdf.res.status, 200);
  });

  it("instrutor não emite token de staff; admin emite de instrutor", async (t) => {
    const { origin, db } = await startHarness(t);
    const inst = new Jar();
    await login(origin, inst, "instrutor.demo@local.test", DEMO.instructor);
    const adminId = db.prepare("SELECT id FROM users WHERE role = 'admin'").get().id;
    const instId = db.prepare("SELECT id FROM users WHERE email = ?").get("instrutor.demo@local.test").id;
    const page = await grab(origin, inst, "/admin");
    const csrf = csrfFrom(page.text);
    const onAdmin = await grab(origin, inst, `/admin/conta/${adminId}/reset`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ csrf }),
    });
    assert.equal(onAdmin.res.status, 403);
    assert.equal(/<code>[a-f0-9]{64}<\/code>/.test(onAdmin.text), false);
    const onSelf = await grab(origin, inst, `/admin/conta/${instId}/reset`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ csrf }),
    });
    assert.equal(onSelf.res.status, 403);

    const admin = new Jar();
    await login(origin, admin, "admin.demo@local.test", DEMO.admin);
    const adminPage = await grab(origin, admin, "/admin");
    const issued = await grab(origin, admin, `/admin/conta/${instId}/reset`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ csrf: csrfFrom(adminPage.text) }),
    });
    assert.equal(issued.res.status, 200);
    assert.match(issued.text, /<code>[a-f0-9]{64}<\/code>/);
  });

  it("CSV não começa fórmula e o comprovante público não mostra o nome", async (t) => {
    const { origin, db } = await startHarness(t);
    db.prepare("UPDATE users SET name = ? WHERE email = ?").run("=cmd|calc", "aluno-a.demo@local.test");
    const id = db.prepare("SELECT id FROM users WHERE email = ?").get("aluno-a.demo@local.test").id;
    db.prepare("INSERT INTO certificates (user_id, code, issued_at, criteria_json) VALUES (?, ?, ?, ?)").run(
      id,
      "abc123demo",
      "2026-11-07T00:00:00.000Z",
      "{}"
    );
    const admin = new Jar();
    await login(origin, admin, "admin.demo@local.test", DEMO.admin);
    const csv = await grab(origin, admin, "/admin/export.csv");
    assert.equal(csv.res.status, 200);
    assert.match(csv.text, /'=cmd\|calc/);
    assert.equal(csv.text.includes("\n=cmd"), false);
    const pub = await grab(origin, new Jar(), "/verificar/abc123demo");
    assert.equal(pub.res.status, 200);
    assert.equal(pub.text.includes("Aluno A"), false);
    assert.equal(pub.text.includes("aluno-a.demo@local.test"), false);
    const ready = await grab(origin, new Jar(), "/readyz");
    const body = JSON.parse(ready.text);
    assert.deepEqual(Object.keys(body).sort(), ["ok", "service"]);
  });

  it("symlink para fora e dupla codificação são recusados", () => {
    const root = mkdtempSync(path.join(tmpdir(), "ead-root-"));
    const outside = mkdtempSync(path.join(tmpdir(), "ead-out-"));
    mkdirSync(path.join(root, "media"));
    writeFileSync(path.join(outside, "segredo.txt"), "nao-servir");
    writeFileSync(path.join(root, "media", "ok.txt"), "ok");
    symlinkSync(path.join(outside, "segredo.txt"), path.join(root, "media", "link.txt"));
    assert.throws(() => safeInside(root, "media/link.txt"), (err) => err.status === 403);
    assert.throws(() => safeInside(root, "%2e%2e/segredo.txt"), (err) => err.status === 400);
    assert.equal(safeInside(root, "media/ok.txt").endsWith("ok.txt"), true);
  });

  it("base e backup ficam 0600 e a pasta 0700", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "ead-mode-"));
    const file = path.join(dir, "nested", "ead.sqlite");
    const db = openDb(file);
    db.close();
    assert.equal(statSync(file).mode & 0o777, 0o600);
    assert.equal(statSync(path.dirname(file)).mode & 0o777, 0o700);
    const cli = path.resolve(import.meta.dirname, "../src/cli.mjs");
    const dest = path.join(dir, "backup.sqlite");
    const run = spawnSync(process.execPath, [cli, "backup", dest], {
      encoding: "utf8",
      env: { ...process.env, EAD_DATA_DIR: path.dirname(file) },
    });
    assert.equal(run.status, 0, run.stderr);
    assert.equal(statSync(dest).mode & 0o777, 0o600);
  });

  it("força bruta de login esgota no nono erro", async (t) => {
    const { origin } = await startHarness(t);
    const jar = new Jar();
    const page = await grab(origin, jar, "/entrar");
    const csrf = csrfFrom(page.text);
    let last = 0;
    for (let i = 0; i < 9; i++) {
      const res = await grab(origin, jar, "/entrar", {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ email: "ninguem@local.test", password: "senha-errada-10", csrf }),
      });
      last = res.res.status;
    }
    assert.equal(last, 429);
  });
});
