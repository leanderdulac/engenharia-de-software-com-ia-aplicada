import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { signupOpen } from "../src/runtime.mjs";
import { DEMO } from "./helpers.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const probe = path.join(root, "tests", "signup-http-probe.mjs");

test("só EAD_OPEN_SIGNUP=1 abre; 0, ausente e inválido fecham em qualquer NODE_ENV", () => {
  assert.equal(signupOpen({}), false);
  assert.equal(signupOpen({ NODE_ENV: "development" }), false);
  assert.equal(signupOpen({ NODE_ENV: "production" }), false);
  for (const nodeEnv of [undefined, "development", "production"]) {
    const base = nodeEnv ? { NODE_ENV: nodeEnv } : {};
    assert.equal(signupOpen({ ...base, EAD_OPEN_SIGNUP: "0" }), false);
    for (const bad of ["", "false", "no", "off", "yes", "true", "2", " 1", "1 "]) {
      assert.equal(signupOpen({ ...base, EAD_OPEN_SIGNUP: bad }), false);
    }
    assert.equal(signupOpen({ ...base, EAD_OPEN_SIGNUP: "1" }), true);
  }
});

function runNode(script, args, env) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [script, ...args], {
      cwd: root,
      env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => {
      out += d;
    });
    child.stderr.on("data", (d) => {
      err += d;
    });
    child.on("close", (code) => resolve({ code, out, err }));
    child.on("error", reject);
  });
}

function cleanEnv(extra) {
  const env = { ...process.env };
  for (const key of [
    "EAD_DATA_DIR",
    "EAD_ADMIN_EMAIL",
    "EAD_ADMIN_PASSWORD",
    "EAD_USER_EMAIL",
    "EAD_USER_PASSWORD",
    "EAD_USER_NAME",
    "EAD_USER_ROLE",
    "EAD_SEED_DEMO",
    "EAD_DEMO_INSTRUCTOR_PASSWORD",
    "EAD_DEMO_ALUNO_A_PASSWORD",
    "EAD_DEMO_ALUNO_B_PASSWORD",
  ]) {
    delete env[key];
  }
  return { ...env, ...extra };
}

async function probeWith(extra) {
  const env = cleanEnv(extra);
  if (!Object.hasOwn(extra, "EAD_OPEN_SIGNUP")) delete env.EAD_OPEN_SIGNUP;
  if (!Object.hasOwn(extra, "NODE_ENV")) delete env.NODE_ENV;
  const { code, out, err } = await runNode(probe, [], env);
  const line = out.trim().split("\n").filter((l) => l.startsWith("{")).pop();
  assert.equal(code, 0, err);
  return JSON.parse(line);
}

function assertClosed(report) {
  assert.equal(report.csrfLen, 64);
  assert.equal(report.getStatus, 403);
  assert.equal(report.getForm, false);
  assert.equal(report.getPassword, false);
  assert.equal(report.getEmail, false);
  assert.equal(report.getName, false);
  assert.equal(report.postStatus, 403);
  assert.equal(report.apiStatus, 404);
  assert.notEqual(report.jsonStatus, 303);
  assert.equal(report.loginStatus, 303);
  assert.equal(report.dashOk, true);
  assert.equal(report.after.users, report.before.users);
  assert.equal(report.after.attempts, report.before.attempts);
  assert.deepEqual(report.after.rows, report.before.rows);
  assert.equal(report.after.rows.some((r) => r.email === "intruso.signup@local.test"), false);
}

test("GET e POST fechados com signup 0 em development, sem NODE_ENV e em produção", async () => {
  assertClosed(await probeWith({ EAD_OPEN_SIGNUP: "0", NODE_ENV: "development" }));
  assertClosed(await probeWith({ EAD_OPEN_SIGNUP: "0" }));
  assertClosed(await probeWith({ EAD_OPEN_SIGNUP: "false", NODE_ENV: "development" }));
  assertClosed(await probeWith({ EAD_OPEN_SIGNUP: "0", NODE_ENV: "production" }));
  assertClosed(await probeWith({ NODE_ENV: "production" }));
  assertClosed(await probeWith({ NODE_ENV: "development" }));
});

test("EAD_OPEN_SIGNUP=1 abre de propósito e cria só aluno", async () => {
  for (const nodeEnv of ["development", "production"]) {
    const report = await probeWith({ EAD_OPEN_SIGNUP: "1", NODE_ENV: nodeEnv });
    assert.equal(report.getStatus, 200);
    assert.equal(report.getForm, true);
    assert.equal(report.postStatus, 303);
    assert.equal(report.after.users, report.before.users + 1);
    const created = report.after.rows.find((r) => r.email === "intruso.signup@local.test");
    assert.equal(created.role, "aluno");
    assert.equal(report.apiStatus, 404);
  }
});

test("CLI create-admin, create-user e seed ignoram o fecho do formulário", async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "ead-cli-signup-"));
  const env = cleanEnv({
    EAD_DATA_DIR: dir,
    EAD_OPEN_SIGNUP: "0",
    NODE_ENV: "development",
    EAD_ADMIN_EMAIL: "cli.admin@local.test",
    EAD_ADMIN_PASSWORD: "Cli-Admin-teste-10",
    EAD_USER_EMAIL: "cli.aluno@local.test",
    EAD_USER_NAME: "Aluno CLI",
    EAD_USER_PASSWORD: "Cli-Aluno-teste-10",
    EAD_USER_ROLE: "aluno",
  });
  const migrate = await runNode(path.join(root, "src", "cli.mjs"), ["migrate"], env);
  assert.equal(migrate.code, 0, migrate.err);
  const admin = await runNode(path.join(root, "src", "cli.mjs"), ["create-admin"], env);
  assert.equal(admin.code, 0, admin.err);
  const user = await runNode(path.join(root, "src", "cli.mjs"), ["create-user"], env);
  assert.equal(user.code, 0, user.err);
  const seed = await runNode(path.join(root, "src", "cli.mjs"), ["seed"], {
    ...env,
    EAD_SEED_DEMO: "1",
    EAD_DEMO_INSTRUCTOR_PASSWORD: DEMO.instructor,
    EAD_DEMO_ALUNO_A_PASSWORD: DEMO.alunoA,
    EAD_DEMO_ALUNO_B_PASSWORD: DEMO.alunoB,
  });
  assert.equal(seed.code, 0, seed.err);
  const db = new DatabaseSync(path.join(dir, "ead.sqlite"));
  const rows = db.prepare("SELECT email, role FROM users ORDER BY email").all().map((r) => ({ email: r.email, role: r.role }));
  db.close();
  assert.deepEqual(rows, [
    { email: "aluno-a.demo@local.test", role: "aluno" },
    { email: "aluno-b.demo@local.test", role: "aluno" },
    { email: "cli.admin@local.test", role: "admin" },
    { email: "cli.aluno@local.test", role: "aluno" },
    { email: "instrutor.demo@local.test", role: "instrutor" },
  ]);
});
