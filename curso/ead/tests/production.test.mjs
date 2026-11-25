import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { backup } from "node:sqlite";
import { openDb } from "../src/db.mjs";
import { schemaVersion } from "../src/migrate.mjs";
import { integrityOk } from "../src/ops.mjs";
import { assertBootConfig, signupOpen } from "../src/runtime.mjs";
import { DEMO, csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

test("produção recusa config insegura e seed de demonstração", () => {
  assert.throws(
    () => assertBootConfig({ NODE_ENV: "production" }),
    (err) => err.code === "EAD_CONFIG" && /EAD_DATA_DIR/.test(err.message) && /SEED/.test(err.message) === false
  );
  assert.throws(
    () =>
      assertBootConfig({
        NODE_ENV: "production",
        EAD_SECURE_COOKIES: "1",
        EAD_DATA_DIR: "/var/ead",
        EAD_SEED_DEMO: "1",
      }),
    (err) => err.code === "EAD_CONFIG"
  );
  assert.deepEqual(
    assertBootConfig({
      NODE_ENV: "production",
      EAD_SECURE_COOKIES: "1",
      EAD_DATA_DIR: "/var/ead",
    }),
    ["secure-cookies", "data-dir", "sem-seed-demo"]
  );
  assert.equal(signupOpen({ NODE_ENV: "production" }), false);
  assert.equal(signupOpen({ NODE_ENV: "production", EAD_OPEN_SIGNUP: "0" }), false);
  assert.equal(signupOpen({ NODE_ENV: "production", EAD_OPEN_SIGNUP: "1" }), true);
  assert.equal(signupOpen({ NODE_ENV: "development" }), false);
  assert.equal(signupOpen({ NODE_ENV: "development", EAD_OPEN_SIGNUP: "0" }), false);
  assert.equal(signupOpen({ NODE_ENV: "development", EAD_OPEN_SIGNUP: "1" }), true);
});

test("backup SQLite reabre com o mesmo esquema e a mesma conta", async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "ead-bak-"));
  const src = path.join(dir, "ead.sqlite");
  const dest = path.join(dir, "copia.sqlite");
  const db = openDb(src);
  db.prepare(
    "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, disabled, created_at) VALUES ('ops@local.test', 'x', 'Ops', 'aluno', 0, 0, 0, '2026-01-01')"
  ).run();
  db.exec("PRAGMA wal_checkpoint(PASSIVE);");
  await backup(db, dest, { rate: 50 });
  db.close();
  const copy = openDb(dest);
  assert.equal(integrityOk(copy), true);
  assert.ok(schemaVersion(copy) >= 2);
  assert.equal(copy.prepare("SELECT email FROM users WHERE email = ?").get("ops@local.test").email, "ops@local.test");
  copy.close();
});

test("cabeçalhos, readyz, janela, desactivar, token e troca de senha", async (t) => {
  const { origin, db } = await startHarness(t);
  const home = await grab(origin, new Jar(), "/");
  assert.equal(home.res.headers.get("x-frame-options"), "DENY");
  assert.match(home.res.headers.get("content-security-policy") || "", /default-src 'self'/);
  assert.ok(home.res.headers.get("x-request-id"));

  const ready = await grab(origin, new Jar(), "/readyz");
  assert.equal(ready.res.status, 200);
  assert.match(ready.text, /"ok":true/);

  const aluno = new Jar();
  const outro = new Jar();
  await login(origin, aluno, "aluno-a.demo@local.test", DEMO.alunoA);
  await follow(origin, aluno, "/dashboard");
  await login(origin, outro, "aluno-a.demo@local.test", DEMO.alunoA);
  await follow(origin, outro, "/dashboard");

  const conta = await grab(origin, aluno, "/conta");
  const changed = await grab(origin, aluno, "/conta/senha", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrf: csrfFrom(conta.text),
      current: DEMO.alunoA,
      next: "AlunoA-Nova-senha-10",
    }),
  });
  assert.equal(changed.res.status, 303);
  const kicked = await grab(origin, outro, "/dashboard");
  assert.equal(kicked.res.status, 303);
  assert.match(kicked.location || "", /entrar/);

  const inst = new Jar();
  await login(origin, inst, "instrutor.demo@local.test", DEMO.instructor);
  await follow(origin, inst, "/admin");
  const turma = await grab(origin, inst, "/admin");
  const future = "2099-01-01";
  await grab(origin, inst, "/admin/turma", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrf: csrfFrom(turma.text),
      cohort_name: "Turma privada",
      cohort_starts: future,
      cohort_ends: "2099-12-31",
    }),
  });
  const b = new Jar();
  await login(origin, b, "aluno-b.demo@local.test", DEMO.alunoB);
  const cat = await grab(origin, b, "/catalogo");
  const blocked = await grab(origin, b, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(cat.text) }),
  });
  assert.equal(blocked.res.status, 403);
  assert.match(blocked.text, /2099-01-01/);

  const idB = db.prepare("SELECT id FROM users WHERE email = ?").get("aluno-b.demo@local.test").id;
  const adminPage = await grab(origin, inst, "/admin");
  const off = await grab(origin, inst, `/admin/conta/${idB}/estado`, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(adminPage.text) }),
  });
  assert.equal(off.res.status, 303);
  const denied = await login(origin, new Jar(), "aluno-b.demo@local.test", DEMO.alunoB);
  assert.equal(denied.res.status, 403);

  const again = await grab(origin, inst, "/admin");
  const issued = await grab(origin, inst, `/admin/conta/${idB}/reset`, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(again.text) }),
  });
  assert.equal(issued.res.status, 200);
  const token = issued.text.match(/<code>([a-f0-9]{64})<\/code>/);
  assert.ok(token);
  const anon = new Jar();
  const form = await grab(origin, anon, "/redefinir");
  const done = await grab(origin, anon, "/redefinir", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrf: csrfFrom(form.text),
      token: token[1],
      password: "AlunoB-Nova-senha-10",
    }),
  });
  assert.equal(done.res.status, 303);
  const replayJar = new Jar();
  const replayForm = await grab(origin, replayJar, "/redefinir");
  const replay = await grab(origin, replayJar, "/redefinir", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      csrf: csrfFrom(replayForm.text),
      token: token[1],
      password: "AlunoB-Outra-senha-10",
    }),
  });
  assert.equal(replay.res.status, 400);

  db.prepare("UPDATE users SET disabled = 0 WHERE id = ?").run(idB);
  const back = await login(origin, new Jar(), "aluno-b.demo@local.test", "AlunoB-Nova-senha-10");
  assert.equal(back.res.status, 303);

  const audit = await grab(origin, inst, "/admin/auditoria");
  assert.match(audit.text, /token_senha/);
  assert.equal(audit.text.includes(token[1]), false);
});
