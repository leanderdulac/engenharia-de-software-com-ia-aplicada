import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { createApp } from "./server.js";

let server;
let base;

before(async () => {
  const app = createApp();
  await new Promise((resolve) => {
    server = app.listen(0, "127.0.0.1", resolve);
  });
  const addr = server.address();
  base = `http://127.0.0.1:${addr.port}`;
});

after(async () => {
  await new Promise((resolve, reject) => {
    server.close((err) => (err ? reject(err) : resolve()));
  });
});

async function get(path, headers = {}) {
  return fetch(`${base}${path}`, { headers });
}

describe("preview HTTP", () => {
  it("serve a shell com CSS e JS relativos", async () => {
    const res = await get("/");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /text\/html/);
    const html = await res.text();
    assert.match(html, /href="\.\/styles\.css"/);
    assert.match(html, /src="\.\/app\.js"/);
    assert.doesNotMatch(html, /href="\/styles\.css"/);
  });

  it("CSS tem text/css", async () => {
    const res = await get("/styles.css");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /text\/css/);
  });

  it("API de página devolve JSON com HTML, não markdown cru", async () => {
    const res = await get("/api/page?path=README.md");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /application\/json/);
    const data = await res.json();
    assert.equal(data.path, "README.md");
    assert.ok(data.html.includes("<"));
    assert.ok(!data.html.startsWith("# "));
  });

  it("aula em rota profunda via API (não depende de CSS relativo do hash)", async () => {
    const res = await get("/api/page?path=conteudo/modulo-01/aula.md");
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.match(data.title, /Módulo 01/);
    assert.match(data.html, /\/media\/imagens\/modulo-01-capa\.png/);
  });

  it("pedido de .md sem raw=1 não é text/html com markdown cru", async () => {
    const res = await get("/modulos/01.md", { Accept: "application/json" });
    assert.equal(res.status, 400);
    assert.match(res.headers.get("content-type") || "", /application\/json/);
    const data = await res.json();
    assert.equal(data.error, true);
    assert.match(data.message, /raw=1/);
  });

  it("pedido de .md com Accept HTML redireciona para hash", async () => {
    const res = await fetch(`${base}/modulos/01.md`, {
      headers: { Accept: "text/html" },
      redirect: "manual",
    });
    assert.ok([302, 301].includes(res.status), `status=${res.status}`);
    assert.equal(new URL(res.headers.get("location"), base).hash, "#/modulos/01.md");
  });

  it("?raw=1 devolve text/markdown", async () => {
    const res = await get("/modulos/01.md?raw=1");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /text\/markdown/);
    const text = await res.text();
    assert.match(text, /^# /m);
  });

  it("PDF do lab M07 é application/pdf e não JSON 404", async () => {
    const rel =
      "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo/Atividade%20-%20Módulo%201.pdf";
    const res = await get(`/arquivos/${rel}`);
    assert.equal(res.status, 200, await res.text());
    assert.match(res.headers.get("content-type") || "", /application\/pdf/);
  });

  it("página do módulo 07 reescreve o PDF para /arquivos/", async () => {
    const res = await get("/api/page?path=modulos/07.md");
    const data = await res.json();
    assert.match(data.html, /\/arquivos\/modulo07-ferramentas-de-ia-para-gestao-de-projetos\//);
  });

  it("capa hero existe em /media/", async () => {
    const res = await get("/media/imagens/curso-capa-hero.png");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /image\//);
  });

  it("VTT de narração tem MIME text/vtt", async () => {
    const res = await get("/media/audios/tts/modulo-01-narracao.vtt");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /text\/vtt/);
  });

  it("APIs de mídia respondem", async () => {
    const grok = await (await get("/api/grok-videos")).json();
    const tts = await (await get("/api/tts-audios")).json();
    assert.ok(Array.isArray(grok.videos) && grok.videos.length >= 9);
    assert.ok(Array.isArray(tts.audios) && tts.audios.length >= 9);
    assert.ok(tts.audios[0].vtt_src.includes("media/audios/tts/"));
  });
});
