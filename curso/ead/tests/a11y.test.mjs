import { test } from "node:test";
import assert from "node:assert/strict";
import { DEMO, grab, Jar, login, startHarness } from "./helpers.mjs";

test("páginas autenticadas têm lang, skip-link e labels (não é certificação WCAG)", async (t) => {
  const { origin } = await startHarness(t);
  const home = await grab(origin, new Jar(), "/");
  assert.match(home.text, /lang="pt-BR"/);
  assert.match(home.text, /Pular para o conteúdo/);
  assert.match(home.text, /id="conteudo"/);

  const entrar = await grab(origin, new Jar(), "/entrar");
  assert.match(entrar.text, /<label for="f-email">/);
  assert.match(entrar.text, /<label for="f-password">/);

  const jar = new Jar();
  await login(origin, jar, "aluno-a.demo@local.test", DEMO.alunoA);
  const dash = await grab(origin, jar, "/ajuda");
  assert.match(dash.text, /não certifica WCAG/i);
});
