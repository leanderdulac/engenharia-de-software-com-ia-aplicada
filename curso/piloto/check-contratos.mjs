#!/usr/bin/env node
/**
 * Validação de contrato/configuração. TESTE LOCAL ≠ integração real.
 * Não chama OpenRouter, Groq, Gemini nem Vertex.
 *
 *   node curso/piloto/check-contratos.mjs
 */
import { existsSync, readFileSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const FAIL = [];
const OK = [];

function read(rel) {
  const abs = path.join(REPO, rel);
  if (!existsSync(abs)) {
    FAIL.push(`ausente: ${rel}`);
    return "";
  }
  return readFileSync(abs, "utf8");
}

const ex11 = read("modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/.env.example");
if (!/OPENROUTER_API_KEY=/.test(ex11)) FAIL.push("M01 ex.11 .env.example sem OPENROUTER_API_KEY=");
else OK.push("M01 ex.11 .env.example declara OPENROUTER_API_KEY");

const req = read("modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/request.sh");
if (!/Content-Type: application\/json/.test(req)) FAIL.push("request.sh sem Content-Type JSON");
if (!/Authorization: Bearer \$OPENROUTER_API_KEY/.test(req)) FAIL.push("request.sh sem Bearer");
if (!/openrouter\.ai\/api\/v1\/chat\/completions/.test(req)) FAIL.push("request.sh URL OpenRouter inesperada");
else OK.push("M01 request.sh: MIME + Bearer + URL OpenRouter (não chamado)");

const m04 = read("modulo04-criacao-de-agentes-autonomos-novo/02-padroes-de-raciocinio-e-execucao/.env.example");
if (!/OPENROUTER_API_KEY=/.test(m04)) FAIL.push("M04 U2 .env.example sem OPENROUTER_API_KEY");
else OK.push("M04 U2 .env.example");

const groq = read("modulo06-aiops-engenharia-agentica/.env.example");
if (!/GROQ_API_KEY=/.test(groq)) FAIL.push("M06 .env.example sem GROQ_API_KEY");
else OK.push("M06 .env.example GROQ_API_KEY (vazio)");

const brag = read("modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot/.env.example");
if (!/GEMINI_API_KEY=/.test(brag)) FAIL.push("BragBot .env.example sem GEMINI_API_KEY");
else OK.push("BragBot .env.example");

const vertexRel = "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-03-fine-tuning-via-api/finetuning-automation-tool.js";
const vertexSrc = read(vertexRel);
if (!/GCP_PROJECT_ID/.test(vertexSrc) || !/throw new Error/.test(vertexSrc)) {
  FAIL.push("Vertex tool não recusa GCP_PROJECT_ID ausente");
}

function spawnNoEnv(file) {
  const abs = path.join(REPO, file);
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [abs], {
      cwd: path.dirname(abs),
      env: { PATH: process.env.PATH, NO_COLOR: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    child.stdout.on("data", (d) => {
      out += d;
    });
    child.stderr.on("data", (d) => {
      out += d;
    });
    child.on("close", (code) => resolve({ code, out }));
    child.on("error", (err) => resolve({ code: 127, out: String(err) }));
  });
}

const vertex = await spawnNoEnv(vertexRel);
if (vertex.code !== 0 && /GCP_PROJECT_ID/.test(vertex.out)) {
  OK.push("Vertex recusa arranque sem GCP_PROJECT_ID (não chamou GCP)");
} else {
  FAIL.push(`Vertex sem env: exit=${vertex.code} out=${vertex.out.slice(0, 200)}`);
}

console.log("TESTE LOCAL ≠ integração real. Nenhuma API paga foi chamada.");
for (const line of OK) console.log(`OK    ${line}`);
if (FAIL.length) {
  for (const f of FAIL) console.error(`FAIL  ${f}`);
  process.exit(1);
}
console.log("contratos: pass");
