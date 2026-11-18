import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import {
  extractTitle,
  stripHomeHeroDuplicate,
  resolveMarkdownPath,
  rewriteHtml,
  arquivosRelFromRequest,
} from "./lib/markdown.mjs";
import { CURSO_ROOT, REPO_ROOT } from "./lib/paths.mjs";

describe("helpers de markdown (regressão histórica)", () => {
  it("extractTitle lê o primeiro h1 e remove ênfase", () => {
    assert.equal(extractTitle("# **Título**\n\ncorpo", "x"), "Título");
    assert.equal(extractTitle("sem heading", "fallback"), "fallback");
  });

  it("stripHomeHeroDuplicate só atua no README", () => {
    const html = '<p><img src="/media/imagens/curso-capa-hero.png" alt="x"></p>';
    assert.equal(stripHomeHeroDuplicate(html, "modulos/01.md"), html);
    assert.equal(stripHomeHeroDuplicate(html, "README.md").includes("img"), false);
  });

  it("resolveMarkdownPath recusa path traversal e não-md", () => {
    assert.equal(resolveMarkdownPath("README.md").rel, "README.md");
    assert.throws(() => resolveMarkdownPath("../LICENSE.md"), /fora do pacote/);
    assert.throws(() => resolveMarkdownPath("/etc/passwd"), /fora do pacote/);
    assert.throws(() => resolveMarkdownPath("media/imagens/x.png"), /Markdown/);
  });

  it("rewriteHtml aponta mídia para /media/ e md interno para hash", () => {
    const html = rewriteHtml(
      '<p><img src="../../media/imagens/modulo-01-capa.png" alt="c"><a href="./aula.md">a</a></p>',
      "conteudo/modulo-01/aula.md"
    );
    assert.match(html, /src="\/media\/imagens\/modulo-01-capa.png"/);
    assert.match(html, /href="#\/conteudo\/modulo-01\/aula.md"/);
  });

  it("PDFs fora de curso/ mas no repo viram /arquivos/ e não ficam relativos", () => {
    const href =
      "../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo/Atividade%20-%20Módulo%201.pdf";
    const html = rewriteHtml(`<p><a href="${href}">PDF</a></p>`, "modulos/07.md");
    assert.match(html, /href="\/arquivos\/modulo07-ferramentas-de-ia-para-gestao-de-projetos\//);
    assert.match(html, /target="_blank"/);
    assert.doesNotMatch(html, /href="\.\.\//);
  });
});

describe("servir PDF allowlist", () => {
  it("aceita PDF existente no repo", () => {
    const rel =
      "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo/Atividade - Módulo 1.pdf";
    const resolved = arquivosRelFromRequest(encodeURI(rel));
    assert.equal(path.extname(resolved.abs).toLowerCase(), ".pdf");
    assert.ok(existsSync(resolved.abs), resolved.abs);
    assert.ok(resolved.abs.startsWith(REPO_ROOT));
  });

  it("recusa extensão que não é PDF", () => {
    assert.throws(() => arquivosRelFromRequest("LICENSE.md"), /PDF/);
  });

  it("recusa escape do repositório", () => {
    assert.throws(() => arquivosRelFromRequest("../outside.pdf"), /fora/);
  });
});

describe("pacote curso/", () => {
  it("README e guia do módulo 01 existem", () => {
    assert.ok(existsSync(path.join(CURSO_ROOT, "README.md")));
    assert.ok(existsSync(path.join(CURSO_ROOT, "modulos", "01.md")));
    assert.ok(existsSync(path.join(CURSO_ROOT, "conteudo", "modulo-01", "aula.md")));
  });
});
