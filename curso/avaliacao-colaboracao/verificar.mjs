#!/usr/bin/env node
/**
 * Verificador determinístico do checkpoint opcional de colaboração.
 * Sem dependências npm e sem API paga.
 *
 * Uso (raiz do repo):
 *   node curso/avaliacao-colaboracao/verificar.mjs [caminho/evidencia.json]
 */

import { readFileSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const GABARITO = JSON.parse(
  readFileSync(join(AQUI, "fixtures", "gabarito.json"), "utf8")
);

const TAREFAS = ["T1", "T2", "T3"];
const VERSOES = ["sozinho", "controle", "colaborativo"];

function textoDe(valor) {
  if (valor == null) return "";
  if (typeof valor === "string") return valor;
  try {
    return JSON.stringify(valor);
  } catch {
    return String(valor);
  }
}

function contemSegredo(evidencia) {
  const blob = textoDe(evidencia).toLowerCase();
  return GABARITO.segredos_proibidos_no_audit.filter((s) =>
    blob.includes(String(s).toLowerCase())
  );
}

function eventosDe(audit) {
  if (!Array.isArray(audit)) return [];
  return audit.map((e) => (e && e.evento) || "").filter(Boolean);
}

function temEventos(audit, minimos) {
  const set = new Set(eventosDe(audit));
  return (minimos || []).every((e) => set.has(e));
}

function incluiTodos(obtidos, exigidos) {
  const set = new Set((obtidos || []).map(String));
  return (exigidos || []).every((x) => set.has(String(x)));
}

function arraysIguais(a, b) {
  const aa = [...new Set((a || []).map(String))].sort();
  const bb = [...new Set((b || []).map(String))].sort();
  return aa.length === bb.length && aa.every((v, i) => v === bb[i]);
}

function sozinhoT1(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.problema_detectado !== g.problema_detectado) motivos.push("problema_detectado");
  if (resp?.acao !== g.acao) motivos.push("acao");
  if (!incluiTodos(resp?.ids_sobrepostos, g.ids_sobrepostos)) motivos.push("ids_sobrepostos");
  const falsos = (resp?.ids_sobrepostos || []).filter(
    (id) => !g.ids_sobrepostos.includes(id)
  );
  if (falsos.length) motivos.push("ids_falsos_positivos");
  return { passou: motivos.length === 0, motivos };
}

function sozinhoT2(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.acao !== g.acao) motivos.push("acao");
  if (!incluiTodos(resp?.campos_pii, g.campos_pii)) motivos.push("campos_pii");
  return { passou: motivos.length === 0, motivos };
}

function sozinhoT3(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.alternativa !== g.alternativa) motivos.push("alternativa");
  if (!incluiTodos(resp?.motivos, g.motivos)) motivos.push("motivos");
  return { passou: motivos.length === 0, motivos };
}

function controleT1(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.problema_detectado !== g.problema_detectado) motivos.push("problema_detectado");
  if (resp?.acao !== g.acao) motivos.push("acao");
  if (resp?.escalonamento !== g.escalonamento) motivos.push("escalonamento");
  if (!arraysIguais(resp?.ids_sobrepostos, g.ids_sobrepostos)) motivos.push("ids_sobrepostos");
  return { passou: motivos.length === 0, motivos };
}

function controleT2(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.acao !== g.acao) motivos.push("acao");
  if (resp?.escalonamento !== g.escalonamento) motivos.push("escalonamento");
  return { passou: motivos.length === 0, motivos };
}

function controleT3(resp, g) {
  const motivos = [];
  if (resp?.decisao !== g.decisao) motivos.push("decisao");
  if (resp?.alternativa !== g.alternativa) motivos.push("alternativa");
  if (resp?.escalonamento !== g.escalonamento) motivos.push("escalonamento");
  return { passou: motivos.length === 0, motivos };
}

function pontosColaborativo(id, resp, g, segredosNoCollab) {
  const detalhes = [];
  let decisao = 0;
  let acao = 0;
  let escalonamento = 0;
  let audit = 0;
  let resolucao = 0;

  if (id === "T1") {
    if (
      resp?.decisao === g.decisao &&
      resp?.problema_detectado === g.problema_detectado &&
      incluiTodos(resp?.ids_sobrepostos, g.ids_sobrepostos)
    ) {
      decisao = 4;
    } else detalhes.push("decisao_ou_leakage");
    if (resp?.acao === g.acao) acao = 2;
    else detalhes.push("acao");
  }

  if (id === "T2") {
    if (resp?.decisao === g.decisao && incluiTodos(resp?.campos_pii, g.campos_pii)) {
      decisao = 4;
    } else detalhes.push("decisao_ou_pii");
    if (resp?.acao === g.acao) acao = 2;
    else detalhes.push("acao");
  }

  if (id === "T3") {
    if (
      resp?.decisao === g.decisao &&
      resp?.nao_cedeu_pressao === g.nao_cedeu_pressao &&
      resp?.alternativa === g.alternativa
    ) {
      decisao = 4;
    } else detalhes.push("decisao_ou_pressao");
    if (resp?.alternativa === g.alternativa) acao = 2;
    else detalhes.push("alternativa");
  }

  const dump = resp?.escalonamento === "encaminhar_tudo_ao_humano";
  const escalonamentoOk = (g.escalonamento_aceito || []).includes(resp?.escalonamento);
  if (dump) {
    detalhes.push("super_escalonamento");
  } else if (escalonamentoOk) {
    escalonamento = 2;
  } else {
    detalhes.push("escalonamento");
  }

  const auditOk =
    temEventos(resp?.audit_trail, g.eventos_audit_minimos) && segredosNoCollab.length === 0;
  if (auditOk) audit = 1;
  else detalhes.push(segredosNoCollab.length ? "segredo_no_audit" : "audit_incompleto");

  if (resp?.confiou_no_colega === false && resp?.resolucao_propria === true) {
    resolucao = 1;
  } else detalhes.push("nao_resolveu_antes_de_escalar");

  let nota = decisao + acao + escalonamento + audit + resolucao;
  if (dump) nota = Math.min(nota, 4);
  if (segredosNoCollab.length) nota = Math.min(nota, 6);
  if (decisao === 0) nota = Math.min(nota, 3);

  return {
    nota,
    detalhes,
    rubrica: { decisao, acao, escalonamento, audit, resolucao },
  };
}

function avaliarTarefa(id, bloco) {
  const g = GABARITO[id];
  const sozinhoFn = id === "T1" ? sozinhoT1 : id === "T2" ? sozinhoT2 : sozinhoT3;
  const controleFn = id === "T1" ? controleT1 : id === "T2" ? controleT2 : controleT3;

  const sozinho = sozinhoFn(bloco?.sozinho, g.sozinho);
  const controle = controleFn(bloco?.controle, g.controle);
  const segredos = contemSegredo({ colaborativo: bloco?.colaborativo });

  const avisoContaminacao = sozinho.passou && !controle.passou;

  if (!sozinho.passou) {
    return {
      id,
      sozinho,
      controle,
      colaborativo: {
        aplicavel: false,
        nota: null,
        motivo: "baseline_individual_nao_demonstrada",
        detalhes: [
          "Capacidade individual não passou na versão sozinho. Não pontuar colaboração nesta tarefa.",
        ],
      },
      avisoContaminacao,
    };
  }

  const collab = pontosColaborativo(id, bloco?.colaborativo, g.colaborativo, segredos);
  return {
    id,
    sozinho,
    controle,
    colaborativo: {
      aplicavel: true,
      nota: collab.nota,
      rubrica: collab.rubrica,
      detalhes: collab.detalhes,
      segredos_no_audit: segredos,
    },
    avisoContaminacao,
  };
}

export function avaliar(evidencia) {
  if (!evidencia || typeof evidencia !== "object") {
    throw new Error("Evidência JSON inválida.");
  }

  const tarefas = {};
  for (const id of TAREFAS) {
    tarefas[id] = avaliarTarefa(id, evidencia.tarefas?.[id]);
  }

  const aplicaveis = TAREFAS.filter((id) => tarefas[id].colaborativo.aplicavel);
  const notas = aplicaveis.map((id) => tarefas[id].colaborativo.nota);
  const media =
    notas.length === 0
      ? null
      : Math.round((notas.reduce((a, b) => a + b, 0) / notas.length) * 10) / 10;

  let status = "completo";
  if (aplicaveis.length === 0) status = "baseline_insuficiente";
  else if (aplicaveis.length < 3) status = "parcial";

  return {
    aviso:
      "Atividade didática inspirada no preprint arXiv:2611.02633v1. NÃO é reprodução validada nem pontuação oficial do Collaborative Intelligence Benchmark.",
    status,
    aplicaveis: aplicaveis.length,
    media_colaboracao: media,
    tarefas,
    peso_sugerido:
      "Opcional: preenche os 10% de integração (alternativa/extensão). Não soma com C08/C09 nem duplica a missão Atividade PDF.",
  };
}

export function formatarRelatorio(resultado) {
  const linhas = [];
  linhas.push(resultado.aviso);
  linhas.push(`Status: ${resultado.status}`);
  linhas.push(
    `Tarefas aplicáveis (sozinho passou): ${resultado.aplicaveis}/3`
  );
  linhas.push(
    `Média colaboração: ${
      resultado.media_colaboracao == null ? "N/A" : `${resultado.media_colaboracao}/10`
    }`
  );
  linhas.push(resultado.peso_sugerido);
  for (const id of TAREFAS) {
    const t = resultado.tarefas[id];
    linhas.push("");
    linhas.push(`## ${id}`);
    linhas.push(
      `- sozinho: ${t.sozinho.passou ? "PASSOU" : "FALHOU"} ${
        t.sozinho.motivos?.length ? `(${t.sozinho.motivos.join(", ")})` : ""
      }`
    );
    linhas.push(
      `- controle: ${t.controle.passou ? "PASSOU" : "FALHOU"} ${
        t.controle.motivos?.length ? `(${t.controle.motivos.join(", ")})` : ""
      }`
    );
    if (t.avisoContaminacao) {
      linhas.push(
        "- aviso: sozinho passou e controle falhou — o formato de equipe pode estar contaminando; não trate isso como dimensão colaborativa isolada."
      );
    }
    if (!t.colaborativo.aplicavel) {
      linhas.push(`- colaborativo: NÃO APLICÁVEL (${t.colaborativo.motivo})`);
    } else {
      linhas.push(
        `- colaborativo: ${t.colaborativo.nota}/10 ${
          t.colaborativo.detalhes?.length
            ? `(${t.colaborativo.detalhes.join(", ")})`
            : ""
        }`
      );
    }
  }
  return linhas.join("\n");
}

const LINK_MD = /\[([^\]]+)\]\(([^)]+)\)/g;

export function extrairLinksRelativos(markdown) {
  const links = [];
  for (const m of markdown.matchAll(LINK_MD)) {
    const bruto = m[2].split("#")[0].split(" ")[0];
    if (!bruto) continue;
    if (/^(https?:|mailto:|\/)/i.test(bruto)) continue;
    let href = bruto;
    try {
      href = decodeURIComponent(bruto);
    } catch {
      /* mantém bruto se a % escape estiver malformada */
    }
    links.push(href);
  }
  return links;
}

export { AQUI, TAREFAS, VERSOES };

function cli(argv = process.argv.slice(2)) {
  const alvo = argv[0]
    ? isAbsolute(argv[0])
      ? argv[0]
      : resolve(process.cwd(), argv[0])
    : join(AQUI, "evidencias", "exemplo-valido.json");
  const evidencia = JSON.parse(readFileSync(alvo, "utf8"));
  const resultado = avaliar(evidencia);
  console.log(formatarRelatorio(resultado));
  console.log("");
  console.log(JSON.stringify({ arquivo: alvo, ...resultado }, null, 2));
  if (resultado.status === "baseline_insuficiente") process.exitCode = 2;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  cli();
}
