import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { listenHost } from "../src/config.mjs";
import { DEMO, Jar, grab, login, startHarness } from "./helpers.mjs";

describe("mídia e PDFs exigem sessão", () => {
  it("sem HOST o processo fica em 127.0.0.1", () => {
    const prev = process.env.HOST;
    delete process.env.HOST;
    try {
      assert.equal(listenHost(), "127.0.0.1");
    } finally {
      if (prev === undefined) delete process.env.HOST;
      else process.env.HOST = prev;
    }
  });

  it("anónimo recebe 401; aluno autenticado lê a capa", async (t) => {
    const { origin } = await startHarness(t);
    const anon = new Jar();
    const media = await grab(origin, anon, "/media/imagens/curso-capa-hero.png");
    assert.equal(media.res.status, 401);
    assert.match(media.text, /Autenticação necessária/);
    const pdf = await grab(origin, anon, "/arquivos/conteudo/modulo-07/Atividade.pdf");
    assert.equal(pdf.res.status, 401);

    const jar = new Jar();
    const logged = await login(origin, jar, "aluno-a.demo@local.test", DEMO.alunoA);
    assert.equal(logged.res.status, 303);
    const ok = await grab(origin, jar, "/media/imagens/curso-capa-hero.png");
    assert.equal(ok.res.status, 200);
    assert.match(ok.res.headers.get("content-type") || "", /image\//);
  });
});
