import assert from "node:assert/strict";
import { rmSync, symlinkSync, writeFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { rewriteHtml } from "../../preview/lib/markdown.mjs";
import { loadCatalog } from "../src/catalog.mjs";
import { inspectRecurso, parseRecursoPath } from "../src/recurso.mjs";
import { REPO_ROOT } from "../src/config.mjs";
import { DEMO, csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

const EXEMPLO = "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-01-ecommerce-recomendations-z";

test("a sala reescreve o exemplo e preserva mídia, PDF e âncora", () => {
  const html = rewriteHtml(
    [
      `<a href="../../../${EXEMPLO}/">loja</a>`,
      `<a href="../../../${EXEMPLO}/parte01-ecommerce-recomendations-with-tensorflow/#worker">parte</a>`,
      `<a href="../../modulos/01.md#labs">guia</a>`,
      `<a href="../../media/audios/tts/modulo-01-narracao.mp3">audio</a>`,
    ].join(" "),
    "conteudo/modulo-01/aula.md",
    { surface: "ead", from: "/aula/m01-intro" }
  );
  const pdf = rewriteHtml(
    `<a href="../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo/Atividade%20-%20Módulo%201.pdf">pdf</a>`,
    "modulos/07.md",
    { surface: "ead", from: "/aula/m07-guia" }
  );
  assert.match(html, new RegExp(`href="/recurso/${EXEMPLO}\\?from=%2Faula%2Fm01-intro"`));
  assert.match(html, /parte01-ecommerce-recomendations-with-tensorflow\?from=%2Faula%2Fm01-intro#worker/);
  assert.match(html, /href="\/aula\/m01-guia#labs"/);
  assert.match(html, /href="\/media\/audios\/tts\/modulo-01-narracao\.mp3"/);
  assert.match(pdf, /href="\/arquivos\/modulo07-ferramentas-de-ia-para-gestao-de-projetos\//);
  assert.doesNotMatch(pdf, /\/recurso\//);
  assert.doesNotMatch(html, /href="\.\.\//);
});

test("o leitor recusa segredo, travessia e a pasta da aplicação", () => {
  assert.equal(parseRecursoPath("..%2F.env").ok, false);
  assert.equal(parseRecursoPath("%2e%2e/%2e%2e/etc/passwd").ok, false);
  const env = inspectRecurso(REPO_ROOT, "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/.env");
  assert.equal(env.status, 403);
  const app = inspectRecurso(REPO_ROOT, "curso/ead/src/server.mjs");
  assert.equal(app.status, 403);
  const nodeModules = inspectRecurso(
    REPO_ROOT,
    "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-00-template/node_modules/express/index.js"
  );
  assert.equal(nodeModules.status, 403);
  const db = inspectRecurso(
    REPO_ROOT,
    "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-08-context7/nextjs-better-auth-demo/better-auth.sqlite"
  );
  assert.equal(db.status, 403);
});

test("o exemplo da loja abre autenticado, sem progresso, e o laboratório não finge execução", async (t) => {
  const { origin, db } = await startHarness(t);
  const anon = await grab(origin, new Jar(), `/${EXEMPLO}/`);
  assert.equal(anon.res.status, 302);
  assert.match(anon.location || "", new RegExp(`^/recurso/${EXEMPLO}$`));
  const anonSala = await grab(origin, new Jar(), `/recurso/${EXEMPLO}/`);
  assert.equal(anonSala.res.status, 401);
  const anonApoio = await grab(origin, new Jar(), "/apoio/apostila-01");
  assert.equal(anonApoio.res.status, 401);
  const anonPdf = await grab(origin, new Jar(), "/arquivos/LICENSE.md");
  assert.equal(anonPdf.res.status, 401);
  const reg = await grab(origin, new Jar(), "/registar", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ email: "novo.aluno@local.test", password: "Senha-teste-10", name: "Novo", csrf: "x" }),
  });
  assert.equal(reg.res.status, 403);

  const aluno = new Jar();
  await login(origin, aluno, "aluno-a.demo@local.test", DEMO.alunoA);
  const fechado = await grab(origin, aluno, `/recurso/${EXEMPLO}/`);
  assert.equal(fechado.res.status, 403);
  assert.match(fechado.text, /matrícula/i);

  const cat = await grab(origin, aluno, "/catalogo");
  await grab(origin, aluno, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(cat.text) }),
  });

  const antes = db.prepare("SELECT COUNT(*) AS n FROM lesson_progress").get().n;
  const pagina = await follow(origin, aluno, `/${EXEMPLO}/`);
  assert.equal(pagina.res.status, 200);
  assert.match(pagina.text, /não executa o laboratório/);
  assert.match(pagina.text, /parte01-ecommerce-recomendations-with-tensorflow/);
  assert.match(pagina.text, /Voltar à trilha/);
  assert.doesNotMatch(pagina.text, /Cannot GET/);

  const catalog = loadCatalog();
  const aula = catalog.lessons.find((l) => l.modulo === "01" && l.percurso && /tensor/i.test(l.titulo));
  assert.ok(aula);
  const licao = await grab(origin, aluno, `/aula/${aula.id}`);
  assert.equal(licao.res.status, 200);
  assert.match(licao.text, new RegExp(`/recurso/${EXEMPLO}\\?from=%2Faula%2F${aula.id}`));
  assert.doesNotMatch(licao.text, /href="\.\.\/\.\.\/\.\.\//);
  const comVolta = await grab(origin, aluno, `/recurso/${EXEMPLO}/?from=${encodeURIComponent(`/aula/${aula.id}`)}`);
  assert.match(comVolta.text, new RegExp(`href="/aula/${aula.id}"`));
  assert.match(comVolta.text, /Voltar à aula/);

  const guia = await grab(origin, aluno, "/aula/m01-guia");
  assert.match(guia.text, /\/recurso\/modulo01-fundamentos-de-ia-e-llms-para-programadores\/exemplo-01-ecommerce-recomendations-z\/parte01-/);

  const intro = await grab(origin, aluno, "/aula/m01-intro");
  assert.match(intro.text, /\/media\//);

  const fonte = await grab(
    origin,
    aluno,
    "/recurso/modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-00-template/index.js"
  );
  assert.equal(fonte.res.status, 200);
  assert.match(fonte.text, /tfjs-node/);
  assert.match(fonte.text, /não executa o laboratório/);
  assert.match(fonte.text, /<pre><code>import tf from &\#39;@tensorflow\/tfjs-node&\#39;;/);

  const modelo = await grab(
    origin,
    aluno,
    "/recurso/modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/.env.example"
  );
  assert.equal(modelo.res.status, 200);
  assert.match(modelo.text, /Não commite o \.env/);

  const ausente = await grab(
    origin,
    aluno,
    "/recurso/modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-que-nao-existe/"
  );
  assert.equal(ausente.res.status, 404);
  assert.match(ausente.text, /não está nesta instalação/);
  assert.match(ausente.text, /não executa o laboratório/);

  const m02 = await grab(origin, aluno, "/recurso/modulo02-integracao-apis-llms/README.md");
  assert.equal(m02.res.status, 403);
  assert.match(m02.text, /Pré-requisito pendente/);

  const instrutor = new Jar();
  await login(origin, instrutor, "instrutor.demo@local.test", DEMO.instructor);
  const equipe = await grab(origin, instrutor, "/recurso/modulo02-integracao-apis-llms/README.md");
  assert.equal(equipe.res.status, 200);

  const peso = await grab(
    origin,
    aluno,
    "/recurso/modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-02-vencendo-qualquer-jogo/DuckHunt-JS-parte01/machine-learning/yolov5n_web_model/group1-shard1of2.bin"
  );
  assert.equal(peso.res.status, 200);
  assert.match(peso.text, /binário ou é grande demais/);
  assert.doesNotMatch(peso.text, /PK/);

  const secreto = "sk-test-local-not-real";
  const envPath = path.join(REPO_ROOT, "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/.env");
  const linkFora = path.join(REPO_ROOT, EXEMPLO, "symlink-teste-recurso");
  const linkApp = path.join(REPO_ROOT, EXEMPLO, "symlink-teste-app");
  try {
    writeFileSync(envPath, `OPENROUTER_API_KEY=${secreto}\n`);
    symlinkSync("/etc/passwd", linkFora);
    symlinkSync(path.join(REPO_ROOT, "curso/ead/src/server.mjs"), linkApp);
    const env = await grab(
      origin,
      aluno,
      "/recurso/modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/.env"
    );
    assert.equal(env.res.status, 403);
    assert.doesNotMatch(env.text, new RegExp(secreto));
    const fora = await grab(origin, aluno, `/recurso/${EXEMPLO}/symlink-teste-recurso`);
    assert.equal(fora.res.status, 403);
    assert.doesNotMatch(fora.text, /root:/);
    const app = await grab(origin, aluno, `/recurso/${EXEMPLO}/symlink-teste-app`);
    assert.equal(app.res.status, 403);
    const travessia = await grab(origin, aluno, "/recurso/..%2F..%2Fetc/passwd");
    assert.ok(travessia.res.status === 400 || travessia.res.status === 403);
  } finally {
    rmSync(envPath, { force: true });
    rmSync(linkFora, { force: true });
    rmSync(linkApp, { force: true });
  }

  const meio = db.prepare("SELECT COUNT(*) AS n FROM lesson_progress").get().n;
  await grab(origin, aluno, `/recurso/${EXEMPLO}/parte01-ecommerce-recomendations-with-tensorflow/`);
  const progresso = db.prepare("SELECT COUNT(*) AS n FROM lesson_progress").get().n;
  const concluidas = db.prepare("SELECT COUNT(*) AS n FROM lesson_progress WHERE completed = 1").get().n;
  assert.ok(meio > antes);
  assert.equal(progresso, meio);
  assert.equal(concluidas, 0);
  const contas = db.prepare("SELECT COUNT(*) AS n FROM users").get().n;
  assert.equal(contas, 4);
});
