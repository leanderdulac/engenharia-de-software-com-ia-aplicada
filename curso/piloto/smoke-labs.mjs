#!/usr/bin/env node
/**
 * Smoke granular por lab. Não chama APIs pagas. Mock ≠ integração.
 *
 *   node curso/piloto/smoke-labs.mjs
 */
import { spawn } from "node:child_process";
import { existsSync, readdirSync, statSync, writeFileSync } from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "../..");
const NODE24 =
  process.env.NODE24 ||
  path.join(os.homedir(), ".nvm/versions/node/v24.22.1/bin/node");
const NODE22 = process.execPath;

function run(cmd, cwd, timeout_ms, extraEnv = {}) {
  return new Promise((resolve) => {
    const child = spawn(cmd[0], cmd.slice(1), {
      cwd,
      env: { ...process.env, NO_COLOR: "1", ...extraEnv },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => child.kill("SIGKILL"), timeout_ms);
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

async function probeHttp(url) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(2000) });
    return { ok: res.ok || res.status < 500, status: res.status };
  } catch (err) {
    return { ok: false, error: err.cause?.code || err.message };
  }
}

async function dockerOk() {
  const r = await run(["docker", "info"], REPO, 8000);
  if (r.code === 0) return { ok: true, via: "docker" };
  const sudo = await run(["sudo", "-n", "docker", "info"], REPO, 8000);
  if (sudo.code === 0) {
    return {
      ok: true,
      via: "sudo docker",
      error: "docker.sock sem permissão para o utilizador; sudo -n docker info OK",
    };
  }
  return {
    ok: false,
    error: (r.stderr || sudo.stderr).trim().split("\n").slice(-3).join(" "),
  };
}

function probeTcp(host, port) {
  return new Promise((resolve) => {
    const socket = net.connect({ host, port }, () => {
      socket.end();
      resolve({ ok: true });
    });
    socket.setTimeout(2000);
    socket.on("timeout", () => {
      socket.destroy();
      resolve({ ok: false, error: "timeout" });
    });
    socket.on("error", (err) => resolve({ ok: false, error: err.message }));
  });
}

const CATALOGO = [
  {
    id: "preview-unit",
    modulo: "curso",
    cwd: "curso/preview",
    cmd: ["npm", "test"],
    timeout_ms: 30000,
  },
  {
    id: "c-colab-verificar",
    modulo: "08-09",
    cwd: ".",
    cmd: [NODE22, "--test", "curso/avaliacao-colaboracao/verificar.test.mjs"],
    timeout_ms: 20000,
  },
  {
    id: "m07-monte-carlo",
    modulo: "07",
    cwd: "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-04-estimativas-e-previsoes",
    cmd: [NODE22, "monte-carlo-routewise.js"],
    timeout_ms: 20000,
  },
  {
    id: "m07-routewise-danger",
    modulo: "07",
    cwd: "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-08-governanca-e-compliance/routewise-danger-demo",
    cmd: ["npm", "test"],
    timeout_ms: 40000,
  },
  {
    id: "m09-decision-framework",
    modulo: "09",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework",
    cmd: [NODE22, "decision-framework-tool.js"],
    timeout_ms: 20000,
  },
  {
    id: "m09-grpo-math",
    modulo: "09",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework",
    cmd: [NODE22, "grpo-verifiable-reward-demo.js"],
    timeout_ms: 20000,
  },
  {
    id: "m02-langchain-intro",
    modulo: "02",
    cwd: "modulo02-integracao-apis-llms/02-langchain-intro",
    cmd: ["npm", "test"],
    timeout_ms: 30000,
  },
  {
    id: "c052-a11y-static",
    modulo: "05",
    cwd: ".",
    cmd: [NODE22, "curso/piloto/check-a11y-c052.mjs"],
    timeout_ms: 10000,
  },
  {
    id: "contratos-config",
    modulo: "pago",
    cwd: ".",
    cmd: [NODE22, "curso/piloto/check-contratos.mjs"],
    timeout_ms: 15000,
    nota: "TESTE LOCAL ≠ integração real",
  },
  {
    id: "m03-ciphersuite-mcp",
    modulo: "03",
    cwd: "modulo03-mcp-na-pratica/05-mcps-do-zero-z",
    cmd: ["npm", "test"],
    timeout_ms: 30000,
    node: "24",
  },
  {
    id: "m03-inspector-cli",
    modulo: "03",
    cwd: "modulo03-mcp-na-pratica/05-mcps-do-zero-z",
    cmd: [
      "npx",
      "--yes",
      "@modelcontextprotocol/inspector@2.14.0",
      "--cli",
      "node",
      "--experimental-strip-types",
      "src/index.ts",
      "--method",
      "tools/list",
    ],
    timeout_ms: 60000,
    node: "24",
  },
  {
    id: "m03-customers-mcp",
    modulo: "03",
    cwd: "modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/customers-mcp-z",
    cmd: ["npm", "test"],
    timeout_ms: 30000,
    node: "24",
    needs: "customers-api",
  },
  {
    id: "m03-crud-mongo",
    modulo: "03",
    cwd: "modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/nodejs-fastify-mongodb-crud",
    cmd: ["npm", "test"],
    timeout_ms: 40000,
    needs: "mongo",
  },
  {
    id: "m05-pix-build",
    modulo: "05",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app",
    cmd: ["npm", "run", "build"],
    timeout_ms: 120000,
  },
  {
    id: "m05-pix-unit",
    modulo: "05",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app",
    cmd: ["npm", "test", "--", "--watch=false"],
    timeout_ms: 120000,
    extraEnv: { CI: "true" },
  },
  {
    id: "m05-cfp-frontend",
    modulo: "05",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform",
    cmd: ["npm", "exec", "--", "nx", "build", "frontend"],
    timeout_ms: 180000,
  },
  {
    id: "m05-cfp-api",
    modulo: "05",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform",
    cmd: ["npm", "exec", "--", "nx", "build", "api"],
    timeout_ms: 180000,
  },
  {
    id: "m08-embed-nomic",
    modulo: "08",
    cwd: ".",
    cmd: [
      NODE22,
      "-e",
      `fetch('http://127.0.0.1:11434/api/embed',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:'nomic-embed-text',input:'idade minima ANVISA'})}).then(async r=>{if(!r.ok) throw new Error(r.status);const j=await r.json();const n=(j.embeddings?.[0]||j.embedding||[]).length;if(n<10) throw new Error('embedding curto '+n);console.log('nomic_dims',n);})`,
    ],
    timeout_ms: 30000,
    needs: "ollama-nomic",
  },
  {
    id: "m09-tinyllama-generate",
    modulo: "09",
    cwd: ".",
    cmd: [
      NODE22,
      "-e",
      `fetch('http://127.0.0.1:11434/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:'tinyllama',prompt:'hi',stream:false,options:{num_predict:8}})}).then(async r=>{if(!r.ok) throw new Error(r.status);const j=await r.json();if(!j.response) throw new Error('empty');console.log('tinyllama_handshake_ok')})`,
    ],
    timeout_ms: 60000,
    needs: "ollama-tinyllama",
    nota: "handshake CPU; NÃO é gemma4:e2b nem paridade pedagógica",
  },
  {
    id: "m01-exemplo-11-header",
    modulo: "01",
    cwd: "modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter",
    inspect: "request.sh Content-Type — integração OpenRouter não chamada",
  },
  {
    id: "m06-nexus",
    modulo: "06",
    cwd: "modulo06-aiops-engenharia-agentica",
    status_esperado: "blocked_secrets",
    motivo:
      "GROQ_API_KEY indispensável para labs 4/6/12. Contrato em check-contratos.mjs. Sem chamada Groq.",
    minimo_externo: "GROQ_API_KEY no .env da raiz M06; depois pytest/npm do lab 4",
  },
  {
    id: "m04-opspilot",
    modulo: "04",
    cwd: "modulo04-criacao-de-agentes-autonomos-novo",
    status_esperado: "blocked_secrets",
    motivo: "OPENROUTER_API_KEY nas unidades. Contrato validado; API não chamada.",
    minimo_externo: "OPENROUTER_API_KEY + modelo :free em U2; npm test da unidade",
  },
  {
    id: "m02-openrouter-labs",
    modulo: "02",
    cwd: "modulo02-integracao-apis-llms/01-smart-model-router-gateway",
    status_esperado: "blocked_secrets",
    motivo: "Labs 01/03/05/06/07 chamam OpenRouter. Lab 02 keyword já corre.",
    minimo_externo: "OPENROUTER_API_KEY no lab alvo; npm test do próprio lab",
  },
  {
    id: "m05-bragbot",
    modulo: "05",
    cwd: "modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot",
    status_esperado: "blocked_secrets",
    motivo: "GEMINI_API_KEY / GOOGLE_GENAI_API_KEY. Contrato validado.",
    minimo_externo: "uma chave Gemini no BragBot .env; npm test ou curl POST /api/brag",
  },
  {
    id: "m09-vertex",
    modulo: "09",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-03-fine-tuning-via-api",
    status_esperado: "blocked_secrets",
    motivo: "GCP_PROJECT_ID recusado sem env (check-contratos). Sem job Vertex.",
    minimo_externo: "GCP_PROJECT_ID + TUNING_JOB_NAME; node finetuning-automation-tool.js",
  },
  {
    id: "m09-lora-mlx",
    modulo: "09",
    cwd: "modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft",
    status_esperado: "blocked_gpu",
    motivo: "adapters.safetensors fora do Git; GPU/MLX/Colab. GPU não se simula.",
  },
  {
    id: "m08-react-gemma4",
    modulo: "08",
    cwd: "modulo08-arquitetura-de-sistemas-com-ia/modulo-02-single-agent",
    status_esperado: "blocked_model_size",
    motivo: "Lab pede gemma4:e2b (~4,6–7,5 GB). Não puxado (limite ~2 GB). tinyllama só handshake GRPO.",
  },
];

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
  const docker = await dockerOk();
  const mongo = await probeTcp("127.0.0.1", 27017);
  const ollamaTags = await probeHttp("http://127.0.0.1:11434/api/tags");
  let ollamaModels = [];
  if (ollamaTags.ok) {
    try {
      const data = await fetch("http://127.0.0.1:11434/api/tags").then((r) => r.json());
      ollamaModels = (data.models || []).map((m) => m.name);
    } catch {
      ollamaModels = [];
    }
  }
  const verdaccio = await probeHttp("http://127.0.0.1:4873/");
  const node24ok = existsSync(NODE24);

  const inventario = {
    gerado_em: new Date().toISOString(),
    node: process.version,
    node24: node24ok ? NODE24 : null,
    docker,
    mongo,
    ollama: { ...ollamaTags, models: ollamaModels },
    verdaccio,
    aviso: "Smoke. TESTE LOCAL ≠ integração paga. GPU não simulada.",
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
      cwd: item.cwd,
      comando: item.cmd ? item.cmd.join(" ") : null,
      node: item.node || "22",
    };
    if (!existsSync(cwd)) {
      record.status = "missing";
      record.resultado = "pasta ausente";
      inventario.smokes.push(record);
      console.log(`FAIL  ${item.id}: pasta ausente`);
      continue;
    }
    if (item.needs === "customers-api") {
      const health = await probeHttp("http://127.0.0.1:9999/v1/health");
      if (!health.ok) {
        record.status = "skip";
        record.motivo = `API customers :9999 indisponível (${health.error || health.status}). Suba HOST=127.0.0.1 DB_NAME=customers npm start no CRUD.`;
        inventario.smokes.push(record);
        console.log(`SKIP  ${item.id} ${record.motivo}`);
        continue;
      }
    }
    if (item.needs === "mongo") {
      const ping = await run(
        [
          NODE22,
          "-e",
          "import('mongodb').then(async ({MongoClient})=>{const c=new MongoClient('mongodb://root:example@127.0.0.1:27017');await c.connect();await c.db('admin').command({ping:1});await c.close();console.log('pong')})",
        ],
        cwd,
        8000
      );
      if (ping.code !== 0) {
        record.status = "skip";
        record.motivo = `Mongo 127.0.0.1:27017 indisponível: ${(ping.stderr || ping.stdout).slice(-180)}`;
        inventario.smokes.push(record);
        console.log(`SKIP  ${item.id} ${record.motivo}`);
        continue;
      }
    }
    if (item.needs === "ollama-nomic" && !ollamaModels.some((n) => n.startsWith("nomic-embed-text"))) {
      record.status = "skip";
      record.motivo = `Ollama sem nomic-embed-text (tags=${ollamaModels.join(",") || "offline"})`;
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} ${record.motivo}`);
      continue;
    }
    if (item.needs === "ollama-tinyllama" && !ollamaModels.some((n) => n.startsWith("tinyllama"))) {
      record.status = "skip";
      record.motivo = `Ollama sem tinyllama (tags=${ollamaModels.join(",") || "offline"})`;
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} ${record.motivo}`);
      continue;
    }
    const needsNpm = item.cmd && (item.cmd[0] === "npm" || item.cmd[0] === "npx");
    if (needsNpm && !existsSync(path.join(cwd, "node_modules"))) {
      record.status = "skip";
      record.motivo = "node_modules ausente (rode npm ci neste lab)";
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} ${record.motivo}`);
      continue;
    }
    if (item.node === "24" && !node24ok) {
      record.status = "skip";
      record.motivo = `NODE24 ausente (${NODE24})`;
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} ${record.motivo}`);
      continue;
    }
    if (item.cmd) {
      const extraEnv = { ...(item.extraEnv || {}) };
      if (item.node === "24") {
        extraEnv.PATH = `${path.dirname(NODE24)}${path.delimiter}${process.env.PATH}`;
      }
      const result = await run(item.cmd, cwd, item.timeout_ms, extraEnv);
      record.exit = result.code;
      record.sinal = result.signal;
      const pass = result.code === 0;
      record.status = pass ? "pass" : "fail";
      if (item.nota) record.nota = item.nota;
      record.tail = (result.stdout + "\n" + result.stderr).trim().split("\n").slice(-8);
      inventario.smokes.push(record);
      console.log(`${pass ? "PASS" : "FAIL"}  ${item.id} exit=${result.code}${item.nota ? " [" + item.nota + "]" : ""}`);
      if (!pass) console.log(record.tail.join("\n"));
    } else {
      record.status = item.status_esperado || "inspect_only";
      record.motivo = item.motivo || item.inspect;
      if (item.minimo_externo) record.minimo_externo = item.minimo_externo;
      inventario.smokes.push(record);
      console.log(`SKIP  ${item.id} [${record.status}] ${record.motivo}`);
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
