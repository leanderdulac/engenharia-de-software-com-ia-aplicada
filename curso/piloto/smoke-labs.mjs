#!/usr/bin/env node
/**
 * Inventário + smoke offline/CPU. Não chama APIs pagas, não baixa modelos grandes.
 *
 *   node curso/piloto/smoke-labs.mjs
 */
import { spawn } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "../..");

const CATALOGO = [
  {
    id: "m07-monte-carlo",
    modulo: "07",
    status_esperado: "runnable_offline",
    cwd: "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-04-estimativas-e-previsoes",
    cmd: ["node", "monte-carlo-routewise.js"],
    timeout_ms: 20000,
  },
  {
    id: "m09-decision-framework",
    modulo: "09",
    status_esperado: "runnable_offline",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework",
    cmd: ["node", "decision-framework-tool.js"],
    timeout_ms: 20000,
  },
  {
    id: "c-colab-verificar",
    modulo: "08-09",
    status_esperado: "runnable_offline",
    cwd: ".",
    cmd: ["node", "--test", "curso/avaliacao-colaboracao/verificar.test.mjs"],
    timeout_ms: 20000,
  },
  {
    id: "m02-langchain-intro",
    modulo: "02",
    status_esperado: "runnable_offline",
    cwd: "modulo02-integracao-apis-llms/02-langchain-intro",
    cmd: ["npm", "test"],
    timeout_ms: 30000,
  },
  {
    id: "m09-grpo-math",
    modulo: "09",
    status_esperado: "runnable_offline",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework",
    cmd: ["node", "grpo-verifiable-reward-demo.js"],
    timeout_ms: 20000,
  },
  {
    id: "c052-a11y-static",
    modulo: "05",
    status_esperado: "runnable_offline",
    cwd: ".",
    cmd: ["node", "curso/piloto/check-a11y-c052.mjs"],
    timeout_ms: 10000,
  },
  {
    id: "m01-exemplo-11-header",
    modulo: "01",
    status_esperado: "inspect_only",
    cwd: "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter",
    inspect: "request.sh contém Content-Type application/json",
  },
  {
    id: "m06-nexus",
    modulo: "06",
    status_esperado: "blocked_secrets",
    cwd: "modulo06-aiops-engenharia-agentica",
    motivo: "GROQ_API_KEY + CrewAI; Prometheus/Jaeger simulados. Sem chamada paga neste smoke.",
  },
  {
    id: "m08-react-ollama",
    modulo: "08",
    status_esperado: "blocked_runtime",
    cwd: "modulo08-arquitetura-de-sistemas-com-ia/modulo-02-single-agent",
    motivo: "Tag gemma4:e2b existe no catálogo oficial (4,6–7,5 GB) mas Ollama não está nesta VM; não puxar o modelo. Fallback pago = segredo.",
  },
  {
    id: "m09-lora-mlx",
    modulo: "09",
    status_esperado: "blocked_gpu",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft",
    motivo: "adapters.safetensors fora do Git; MLX/Colab/GPU. Não baixar modelos enormes.",
  },
  {
    id: "m09-vertex",
    modulo: "09",
    status_esperado: "blocked_secrets",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-03-fine-tuning-via-api",
    motivo: "GCP/Vertex. Caminho Colab documentado no guia; não é integração real aqui.",
  },
  {
    id: "companion-rag-cpu",
    modulo: "ref",
    status_esperado: "blocked_model_download",
    cwd: "referencia/llm-course/modulo-13-rag",
    motivo: "lab_cpu.py importa torch e embeddings e5-small — não descarregar nesta máquina.",
  },
  {
    id: "m04-opspilot",
    modulo: "04",
    status_esperado: "blocked_secrets",
    cwd: "modulo04-criacao-de-agentes-autonomos-novo",
    motivo: "OPENROUTER_API_KEY nas unidades. .env.example em U2–U5 acrescentado para setup; smoke não chama a API.",
  },
  {
    id: "m02-openrouter-labs",
    modulo: "02",
    status_esperado: "blocked_secrets",
    cwd: "modulo02-integracao-apis-llms/01-smart-model-router-gateway",
    motivo: "Labs 01/03/05/06/07 chamam OpenRouter (e 04/06 Docker). Sem chave nesta VM. Lab 02 keyword já corre em m02-langchain-intro.",
  },
  {
    id: "m03-mcp",
    modulo: "03",
    status_esperado: "blocked_docker",
    cwd: "modulo03-mcp-na-pratica",
    motivo: "Mongo/Inspector/Verdaccio. Sem Docker de produção neste smoke.",
  },
  {
    id: "m05-bragbot",
    modulo: "05",
    status_esperado: "blocked_secrets",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot",
    motivo: "Genkit + chave Gemini. .env.example acrescentado; não é integração real.",
  },
];

function run(cmd, cwd, timeout_ms) {
  return new Promise((resolve) => {
    const child = spawn(cmd[0], cmd.slice(1), {
      cwd,
      env: { ...process.env, NO_COLOR: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
    }, timeout_ms);
    child.stdout.on("data", (d) => {
      stdout += d.toString();
    });
    child.stderr.on("data", (d) => {
      stderr += d.toString();
    });
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      resolve({
        code,
        signal,
        stdout: stdout.slice(-4000),
        stderr: stderr.slice(-4000),
      });
    });
    child.on("error", (err) => {
      clearTimeout(timer);
      resolve({ code: 127, stdout, stderr: String(err) });
    });
  });
}

function listLabs(moduloDir) {
  if (!existsSync(moduloDir)) return [];
  return readdirSync(moduloDir)
    .filter((name) => !name.startsWith("."))
    .map((name) => {
      const abs = path.join(moduloDir, name);
      let kind = "dir";
      try {
        kind = statSync(abs).isDirectory() ? "dir" : "file";
      } catch {
        kind = "missing";
      }
      return { name, kind };
    });
}

async function main() {
  const inventario = {
    gerado_em: new Date().toISOString(),
    node: process.version,
    aviso: "Smoke offline. Mock ≠ integração real. Sem dados de alunos.",
    modulos: {},
    smokes: [],
  };

  const roots = [
    ["01", "modulo01-fundamentos-de-ia-e-llms-para-programadores"],
    ["02", "modulo02-integracao-apis-llms"],
    ["03", "modulo03-mcp-na-pratica"],
    ["04", "modulo04-criacao-de-agentes-autonomos-novo"],
    ["05", "modulo05-ferramentas-de-IA-para-UI-UX"],
    ["06", "modulo06-aiops-engenharia-agentica"],
    ["07", "modulo07-ferramentas-de-ia-para-gestao-de-projetos"],
    ["08", "modulo08-arquitetura-de-sistemas-com-ia"],
    ["09", "modulo09-processamento-de-dados-e-fine-tuning-de-modelos"],
  ];
  for (const [id, rel] of roots) {
    inventario.modulos[id] = {
      pasta: rel,
      entradas: listLabs(path.join(REPO, rel)).length,
    };
  }

  for (const item of CATALOGO) {
    const cwd = path.join(REPO, item.cwd);
    const record = {
      id: item.id,
      modulo: item.modulo,
      status: item.status_esperado,
      cwd: item.cwd,
    };
    if (!existsSync(cwd)) {
      record.status = "missing";
      record.resultado = "pasta ausente";
      inventario.smokes.push(record);
      console.log(`FAIL  ${item.id}: pasta ausente`);
      continue;
    }
    if (item.cmd) {
      const result = await run(item.cmd, cwd, item.timeout_ms);
      record.exit = result.code;
      record.sinal = result.signal;
      const pass = result.code === 0;
      record.status = pass ? "pass" : "fail";
      record.tail = (result.stdout + "\n" + result.stderr).trim().split("\n").slice(-8);
      inventario.smokes.push(record);
      console.log(`${pass ? "PASS" : "FAIL"}  ${item.id} exit=${result.code}`);
      if (!pass) console.log(record.tail.join("\n"));
    } else {
      record.motivo = item.motivo || item.inspect;
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} [${item.status_esperado}] ${record.motivo}`);
    }
  }

  const outJson = path.join(AQUI, "evidencias-smoke.json");
  writeFileSync(outJson, JSON.stringify(inventario, null, 2));
  console.log(`escreveu ${path.relative(REPO, outJson)}`);
  const failed = inventario.smokes.filter((s) => s.status === "fail" || s.status === "missing");
  if (failed.length) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
