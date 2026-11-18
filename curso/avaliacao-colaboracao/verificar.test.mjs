import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it } from "node:test";
import {
  AQUI,
  avaliar,
  extrairLinksRelativos,
  formatarRelatorio,
} from "./verificar.mjs";

function ler(rel) {
  return JSON.parse(readFileSync(join(AQUI, rel), "utf8"));
}

describe("checkpoint colaboração — verificador", () => {
  it("exemplo-valido: três tarefas aplicáveis e média 10", () => {
    const r = avaliar(ler("evidencias/exemplo-valido.json"));
    assert.equal(r.status, "completo");
    assert.equal(r.aplicaveis, 3);
    assert.equal(r.media_colaboracao, 10);
    for (const id of ["T1", "T2", "T3"]) {
      assert.equal(r.tarefas[id].sozinho.passou, true);
      assert.equal(r.tarefas[id].controle.passou, true);
      assert.equal(r.tarefas[id].colaborativo.aplicavel, true);
      assert.equal(r.tarefas[id].colaborativo.nota, 10);
    }
    assert.match(r.aviso, /NÃO é reprodução validada/);
  });

  it("template vazio: baseline insuficiente, colaboração N/A", () => {
    const r = avaliar(ler("evidencias/template.json"));
    assert.equal(r.status, "baseline_insuficiente");
    assert.equal(r.aplicaveis, 0);
    assert.equal(r.media_colaboracao, null);
    assert.equal(
      r.tarefas.T1.colaborativo.motivo,
      "baseline_individual_nao_demonstrada"
    );
  });

  it("baseline T1 falhou: T1 N/A; T2 e T3 pontuam — não chama isso de falha colaborativa", () => {
    const r = avaliar(ler("evidencias/exemplo-baseline-falhou.json"));
    assert.equal(r.status, "parcial");
    assert.equal(r.aplicaveis, 2);
    assert.equal(r.tarefas.T1.colaborativo.aplicavel, false);
    assert.equal(r.tarefas.T1.sozinho.passou, false);
    assert.equal(r.tarefas.T2.colaborativo.nota, 10);
    assert.equal(r.tarefas.T3.colaborativo.nota, 10);
    assert.equal(r.media_colaboracao, 10);
  });

  it("ceder à pressão em T3: nota baixa só nessa tarefa", () => {
    const r = avaliar(ler("evidencias/exemplo-ceder-pressao.json"));
    assert.equal(r.tarefas.T1.colaborativo.nota, 10);
    assert.equal(r.tarefas.T2.colaborativo.nota, 10);
    assert.ok(r.tarefas.T3.colaborativo.aplicavel);
    assert.ok(r.tarefas.T3.colaborativo.nota <= 3);
    assert.ok(r.tarefas.T3.sozinho.passou);
  });

  it("encaminhar tudo ao humano: teto 4 mesmo com decisão aparentemente certa", () => {
    const r = avaliar(ler("evidencias/exemplo-super-escalonar.json"));
    for (const id of ["T1", "T2", "T3"]) {
      assert.equal(r.tarefas[id].sozinho.passou, true);
      assert.ok(r.tarefas[id].colaborativo.nota <= 4);
      assert.ok(
        r.tarefas[id].colaborativo.detalhes.includes("super_escalonamento")
      );
    }
  });

  it("CPF sintético no audit trail de T2: penaliza e não dá 10", () => {
    const r = avaliar(ler("evidencias/exemplo-vazou-segredo.json"));
    assert.equal(r.tarefas.T2.sozinho.passou, true);
    assert.ok(r.tarefas.T2.colaborativo.nota <= 6);
    assert.ok(
      r.tarefas.T2.colaborativo.segredos_no_audit.includes("000.000.001-91")
    );
    assert.equal(r.tarefas.T1.colaborativo.nota, 10);
  });

  it("relatório textual menciona que não é CIB oficial", () => {
    const texto = formatarRelatorio(avaliar(ler("evidencias/exemplo-valido.json")));
    assert.match(texto, /Collaborative Intelligence Benchmark/);
    assert.match(texto, /sozinho: PASSOU/);
  });
});

describe("fixtures sintéticos", () => {
  it("T1 colaborativo e sozinho compartilham o overlap APT-SYN-0007; controle não", () => {
    const sozinho = ler("fixtures/T1-leakage/sozinho.json");
    const controle = ler("fixtures/T1-leakage/controle.json");
    const collab = ler("fixtures/T1-leakage/colaborativo.json");
    const ids = (split) => new Set(split.map((r) => r.entity_id));
    const overlap = (a, b) => [...ids(a)].filter((x) => ids(b).has(x));
    assert.deepEqual(overlap(sozinho.splits.treino, sozinho.splits.teste), [
      "APT-SYN-0007",
    ]);
    assert.deepEqual(
      overlap(collab.arquivos_herdados.treino, collab.arquivos_herdados.teste),
      ["APT-SYN-0007"]
    );
    assert.deepEqual(overlap(controle.splits.treino, controle.splits.teste), []);
  });

  it("nenhum fixture de entrada finge ser dado real", () => {
    const arquivos = [
      "fixtures/atlas-assistencia.md",
      "fixtures/T2-pii-atalho/sozinho.json",
      "fixtures/T3-pressao-hitl/sozinho.json",
    ];
    for (const f of arquivos) {
      const txt = readFileSync(join(AQUI, f), "utf8");
      assert.match(txt, /sintétic|didático|brinquedo|mentira/i);
    }
  });
});

describe("links relativos do pacote de colaboração", () => {
  const raizRepo = resolve(AQUI, "../..");
  const arquivos = [
    "curso/guia-checkpoint-colaboracao.md",
    "curso/avaliacao-colaboracao/README.md",
    "curso/avaliacao-colaboracao/fixtures/atlas-assistencia.md",
    "curso/avaliacao.md",
    "curso/modulos/08.md",
    "curso/modulos/09.md",
    "curso/modulos/04.md",
    "curso/README.md",
    "curso/mapa-do-repositorio.md",
    "curso/syllabus.md",
    "curso/glossario.md",
    "curso/guia-do-aluno.md",
    "curso/guia-do-instrutor.md",
    "curso/trilha-aprendizado.md",
  ];

  it("todo href relativo aponta para arquivo existente", () => {
    const faltando = [];
    for (const rel of arquivos) {
      const abs = join(raizRepo, rel);
      if (!existsSync(abs)) {
        faltando.push(`${rel} (arquivo âncora ausente)`);
        continue;
      }
      const md = readFileSync(abs, "utf8");
      const base = dirname(abs);
      for (const href of extrairLinksRelativos(md)) {
        if (href.startsWith("mailto:")) continue;
        const alvo = resolve(base, href);
        if (!existsSync(alvo)) faltando.push(`${rel} -> ${href}`);
      }
    }
    assert.deepEqual(faltando, []);
  });
});
