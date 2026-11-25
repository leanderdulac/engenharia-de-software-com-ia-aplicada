import { test } from "node:test";
import assert from "node:assert/strict";
import { hashPassword } from "../src/auth.mjs";
import { csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

const EMAIL = "cli.aluno@local.test";
const PASSWORD = "Cli-Aluno-teste-10";

test("conta CLI sem matrícula vê o próximo passo; M01 abre depois, dependentes não", async (t) => {
  const { origin, db } = await startHarness(t);
  db.prepare(
    "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, disabled, created_at) VALUES (?, ?, ?, 'aluno', 0, 0, 0, ?)"
  ).run(EMAIL, hashPassword(PASSWORD), "Aluno CLI", new Date().toISOString());

  const jar = new Jar();
  const entered = await login(origin, jar, EMAIL, PASSWORD);
  assert.equal(entered.res.status, 303);

  const trilha = await grab(origin, jar, "/trilha");
  assert.equal(trilha.res.status, 200);
  assert.equal(trilha.text.includes("[{"), false);
  assert.equal(/bloqueado/i.test(trilha.text), false);
  assert.match(trilha.text, /Próximo passo: matrícula/);
  assert.match(trilha.text, /action="\/matricular"/);
  assert.match(trilha.text, /Aguardando matrícula/);
  assert.match(trilha.text, /Fundamentos de IA e LLMs para programadores/);
  assert.match(trilha.text, /Depois da matrícula abre sem pré-requisito/);
  assert.match(trilha.text, /não substitui a trilha/);
  assert.equal(trilha.text.includes('href="/modulo/01"'), false);

  const painel = await grab(origin, jar, "/dashboard");
  assert.match(painel.text, /Próximo passo: matrícula/);
  assert.equal(/Conclua o diagnóstico e a matrícula/.test(painel.text), false);
  assert.equal(painel.text.includes("[{"), false);

  const curso = await grab(origin, jar, "/catalogo");
  assert.match(curso.text, /Próximo passo: matrícula/);
  assert.equal(curso.text.includes("[{"), false);
  assert.equal(/bloqueado/i.test(curso.text), false);

  const antes = await grab(origin, jar, "/modulo/01");
  assert.equal(antes.res.status, 403);
  assert.match(antes.text, /ainda não tem matrícula/);
  assert.equal(/pré-requisitos da trilha/i.test(antes.text), false);

  const diag = db.prepare("SELECT COUNT(*) AS n FROM diagnostic_answers WHERE user_id = (SELECT id FROM users WHERE email = ?)").get(EMAIL);
  assert.equal(diag.n, 0);
  const prog = db.prepare("SELECT COUNT(*) AS n FROM lesson_progress WHERE user_id = (SELECT id FROM users WHERE email = ?)").get(EMAIL);
  assert.equal(prog.n, 0);

  const posted = await grab(origin, jar, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(trilha.text) }),
  });
  assert.equal(posted.res.status, 303);

  const depois = await follow(origin, jar, "/trilha");
  assert.match(depois.text, /Disponível/);
  assert.match(depois.text, /href="\/modulo\/01"/);
  assert.match(depois.text, /Pré-requisito pendente: concluir as aulas de M01/);
  assert.match(depois.text, /Opcional/);
  assert.equal(depois.text.includes("[{"), false);
  assert.equal(/bloqueado/i.test(depois.text), false);
  assert.equal(depois.text.includes("Aguardando matrícula"), false);

  const m01 = await grab(origin, jar, "/modulo/01");
  assert.equal(m01.res.status, 200);
  assert.match(m01.text, /Módulo 01/);
  const done = db.prepare(
    "SELECT COUNT(*) AS n FROM lesson_progress WHERE completed = 1 AND user_id = (SELECT id FROM users WHERE email = ?)"
  ).get(EMAIL);
  assert.equal(done.n, 0);

  const m02 = await grab(origin, jar, "/modulo/02");
  assert.equal(m02.res.status, 403);
  assert.match(m02.text, /Pré-requisito pendente: concluir as aulas de M01/);

  const py = await grab(origin, jar, "/modulo/py");
  assert.equal(py.res.status, 200);
  assert.match(py.text, /opcional/i);

  const admin = await grab(origin, jar, "/admin");
  assert.equal(admin.res.status, 403);
  const reg = await grab(origin, new Jar(), "/registar");
  assert.equal(reg.res.status, 403);
  assert.equal(reg.text.includes("<form"), false);

  const ainda = db.prepare("SELECT COUNT(*) AS n FROM diagnostic_answers WHERE user_id = (SELECT id FROM users WHERE email = ?)").get(EMAIL);
  assert.equal(ainda.n, 0);
});
