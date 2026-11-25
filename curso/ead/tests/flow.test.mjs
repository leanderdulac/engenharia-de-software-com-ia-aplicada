import { test } from "node:test";
import assert from "node:assert/strict";
import { DEMO, csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

async function enroll(origin, jar) {
  const cat = await grab(origin, jar, "/catalogo");
  await grab(origin, jar, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(cat.text) }),
  });
}

async function postForm(origin, jar, action, fields, pageUrl) {
  const page = await grab(origin, jar, pageUrl || action);
  const csrf = csrfFrom(page.text);
  assert.ok(csrf, `csrf em ${pageUrl || action}`);
  return grab(origin, jar, action, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf, ...fields }),
  });
}

test("aluno matricula, aula, nota, actividade, instrutor corrige, feedback e comprovante real", async (t) => {
  const { origin, db } = await startHarness(t);
  const aluno = new Jar();
  const inst = new Jar();

  await login(origin, aluno, "aluno-a.demo@local.test", DEMO.alunoA);
  await follow(origin, aluno, "/dashboard");
  await enroll(origin, aluno);

  const aula = await follow(origin, aluno, "/aula/m01-aula");
  assert.equal(aula.res.status, 200);
  assert.match(aula.text, /Módulo 01/);
  await postForm(origin, aluno, "/aula/m01-aula/nota", { body: "nota privada DEMONSTRAÇÃO/TESTE" }, "/aula/m01-aula");
  await postForm(origin, aluno, "/aula/m01-aula/concluir", {}, "/aula/m01-aula");

  const caderno = await grab(origin, aluno, "/caderno");
  assert.match(caderno.text, /nota privada DEMONSTRAÇÃO\/TESTE/);

  await follow(origin, aluno, "/atividade/C01.1");
  await postForm(origin, aluno, "/atividade/C01.1", {
    body_text: "DEMONSTRAÇÃO/TESTE: exemplo-00 no clone local",
    body_url: "https://example.com/evidencia-teste",
  });

  await login(origin, inst, "instrutor.demo@local.test", DEMO.instructor);
  await follow(origin, inst, "/admin");
  const fila = await grab(origin, inst, "/admin/fila");
  assert.match(fila.text, /C01.1/);
  const href = fila.text.match(/\/admin\/correcao\/(\d+)/);
  assert.ok(href);
  await follow(origin, inst, href[0]);
  await postForm(origin, inst, href[0], { score: "8", feedback: "DEMONSTRAÇÃO/TESTE: evidência aceite." });

  const after = await grab(origin, aluno, "/atividade/C01.1");
  assert.match(after.text, /Nota 8/);
  assert.match(after.text, /evidência aceite/);

  const mods = ["01", "02", "03", "04", "05", "06", "07"];
  for (const m of mods) {
    for (const kind of ["aula", "guia", "roteiro"]) {
      await postForm(origin, aluno, `/aula/m${m}-${kind}/concluir`, {}, `/aula/m${m}-${kind}`);
    }
  }
  for (const id of ["C02.1", "C03.1", "C04.3", "C05.1", "C06.1", "C07.1"]) {
    await postForm(origin, aluno, `/atividade/${id}`, { body_text: "DEMONSTRAÇÃO/TESTE checkpoint", body_url: "" });
  }
  const fila2 = await grab(origin, inst, "/admin/fila");
  const ids = [...fila2.text.matchAll(/\/admin\/correcao\/(\d+)/g)].map((x) => x[0]);
  for (const path of ids) {
    await follow(origin, inst, path);
    await postForm(origin, inst, path, { score: "8", feedback: "ok teste" });
  }

  const certPage = await grab(origin, aluno, "/certificado");
  assert.match(certPage.text, /Emitir comprovante interno/);
  await postForm(origin, aluno, "/certificado", {});
  const cert = await grab(origin, aluno, "/certificado");
  const code = cert.text.match(/<code>([a-f0-9]{16})<\/code>/);
  assert.ok(code, "código de verificação");
  const pub = await grab(origin, new Jar(), `/verificar/${code[1]}`);
  assert.match(pub.text, /Comprovante válido/);
  assert.match(pub.text, /Não<\/strong> constitui reconhecimento MEC/i);

  const n = db.prepare("SELECT completed FROM lesson_progress WHERE user_id = (SELECT id FROM users WHERE email = ?) AND lesson_id = 'm01-aula'").get("aluno-a.demo@local.test");
  assert.equal(n.completed, 1);
});
