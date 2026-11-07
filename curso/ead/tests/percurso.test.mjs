import assert from "node:assert/strict";
import { rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { apoioPorId, caminhoApoio, contentDisposition } from "../src/apoio.mjs";
import { loadCatalog } from "../src/catalog.mjs";
import { moduleComplete } from "../src/progress.mjs";
import { DEMO, csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

test("o percurso parte o texto que já existe e guarda os ids antigos", () => {
  const catalog = loadCatalog();
  const aulas = catalog.lessons.filter((l) => l.modulo === "01" && l.percurso);
  assert.ok(aulas.length >= 8);
  assert.equal(aulas[0].id, "m01-intro");
  assert.equal(aulas[0].kind, "intro");
  assert.equal(aulas.at(-1).id, "m01-atividade");
  assert.equal(aulas.at(-1).kind, "atividade");
  assert.ok(aulas.some((l) => /tensor/i.test(l.titulo)));
  assert.ok(catalog.lessons.some((l) => l.id === "m01-aula" && l.legado));
  assert.ok(catalog.lessons.some((l) => l.id === "m01-guia" && l.legado));
  assert.ok(catalog.lessons.some((l) => l.id === "m01-roteiro" && l.legado));
  const intro = aulas[0];
  assert.equal(intro.start > 0, true);
  const done = new Set(["m01-aula", "m01-guia", "m01-roteiro"]);
  assert.equal(moduleComplete(catalog, done, "01"), true);
  assert.equal(moduleComplete(catalog, new Set(["m01-aula"]), "01"), false);
  assert.equal(moduleComplete(catalog, new Set(aulas.map((l) => l.id)), "01"), true);
});

test("apostila ausente não baixa e um PDF real exige sessão", async (t) => {
  assert.equal(apoioPorId("apostila-01").disponivel, false);
  assert.equal(caminhoApoio(apoioPorId("apostila-01")), null);
  assert.match(contentDisposition("modulo-01-apostila.pdf"), /filename="modulo-01-apostila.pdf"/);

  const { origin } = await startHarness(t);
  const anon = await grab(origin, new Jar(), "/apoio/apostila-01");
  assert.equal(anon.res.status, 401);
  const fora = await grab(origin, new Jar(), "/apoio/..%2F..%2Fpackage.json");
  assert.equal(fora.res.status, 401);

  const aluno = new Jar();
  await login(origin, aluno, "aluno-a.demo@local.test", DEMO.alunoA);
  const semMatricula = await grab(origin, aluno, "/apoio/apostila-01");
  assert.equal(semMatricula.res.status, 403);
  const cat = await grab(origin, aluno, "/catalogo");
  await grab(origin, aluno, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(cat.text) }),
  });
  const ausente = await grab(origin, aluno, "/apoio/apostila-01");
  assert.equal(ausente.res.status, 404);
  assert.equal(ausente.res.headers.get("content-disposition"), null);
  const modulo = await follow(origin, aluno, "/modulo/01");
  assert.match(modulo.text, /ainda não foi publicada/);
  assert.equal(modulo.text.includes('href="/apoio/apostila-01"'), false);
  assert.match(modulo.text, /Aula 1 de|01/);
  assert.match(modulo.text, /Introdução/);

  const apoioDir = path.join(path.dirname(new URL("../src/apoio.mjs", import.meta.url).pathname), "..", "apoio");
  const destino = path.join(apoioDir, "modulo-01-apostila.pdf");
  try {
    writeFileSync(destino, "nao e pdf");
    const falso = await grab(origin, aluno, "/apoio/apostila-01");
    assert.equal(falso.res.status, 404);
    writeFileSync(destino, "%PDF-1.4\n% teste local\n");
    const baixado = await grab(origin, aluno, "/apoio/apostila-01");
    assert.equal(baixado.res.status, 200);
    assert.equal(baixado.res.headers.get("content-type"), "application/pdf");
    assert.match(baixado.res.headers.get("content-disposition") || "", /filename="modulo-01-apostila.pdf"/);
    assert.match(baixado.text, /^%PDF-/);
    const pagina = await grab(origin, aluno, "/modulo/01");
    assert.match(pagina.text, /href="\/apoio\/apostila-01"/);
  } finally {
    rmSync(destino, { force: true });
  }
});
