import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { CURSO_ROOT, REPO_ROOT } from "./config.mjs";

const TITULOS = {
  "01": "Fundamentos de IA e LLMs para programadores",
  "02": "Integração de APIs de LLMs",
  "03": "MCP na prática",
  "04": "Agentes autónomos",
  "05": "IA para UI/UX",
  "06": "AIOps e engenharia agêntica",
  "07": "Gestão de projectos com IA",
  "08": "Arquitectura de sistemas com IA",
  "09": "Dados e fine-tuning",
};

const HORAS = {
  "01": 36,
  "02": 24,
  "03": 24,
  "04": 36,
  "05": 20,
  "06": 28,
  "07": 20,
  "08": 20,
  "09": 28,
};

/** Pré-requisitos da trilha oficial (trilha-aprendizado.md). */
export const DEPS = {
  "01": [],
  "02": ["01"],
  "03": ["02"],
  "04": ["03"],
  "05": ["01"],
  "06": ["04"],
  "07": ["01"],
  "08": ["04"],
  "09": ["01"],
  py: [],
};

const ANCORA = {
  "01": ["C01.4"],
  "02": ["C02.2"],
  "03": ["C03.1", "C03.2"],
  "04": ["C04.3"],
  "05": ["C05.2"],
  "06": ["C06.4"],
  "07": ["C07.4"],
  "08": ["C08.1", "C08.4"],
  "09": ["C09.1", "C09.3", "C09.4"],
};

function read(rel) {
  const abs = path.join(CURSO_ROOT, rel);
  if (!existsSync(abs)) return "";
  return readFileSync(abs, "utf8");
}

function parseCheckpoints() {
  const md = read("avaliacao.md");
  const out = [];
  let modulo = null;
  for (const line of md.split("\n")) {
    const head = line.match(/^### M0?(\d+)/);
    if (head) modulo = head[1].padStart(2, "0");
    if (/^### C-COLAB/.test(line)) modulo = "colab";
    const row = line.match(/^\|\s*(C\d+\.\d+|C-COLAB)\s*\|\s*(.+?)\s*\|/);
    if (row && modulo) {
      out.push({
        id: row[1],
        modulo: modulo === "colab" ? "colab" : modulo,
        evidencia: row[2].replace(/\*\*/g, "").trim(),
        kind: row[1] === "C-COLAB" ? "colab" : "checkpoint",
      });
    }
  }
  return out;
}

function parseDiagnostic() {
  const md = read("piloto/pre-pos-teste.md");
  const items = [];
  for (const line of md.split("\n")) {
    const row = line.match(/^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|/);
    if (row && row[1] !== "#") {
      items.push({
        id: Number(row[1]),
        prompt: row[2].trim(),
        liga: row[3].trim(),
      });
    }
  }
  return items;
}

function parseGlossario() {
  const md = read("glossario.md");
  const items = [];
  for (const line of md.split("\n")) {
    const row = line.match(/^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|/);
    if (row) {
      items.push({
        termo: row[1].trim(),
        significado: row[2].trim(),
        onde: row[3].trim(),
      });
    }
  }
  return items;
}

function pdfsDoModulo(modulo) {
  const roots = {
    "07": "modulo07-ferramentas-de-ia-para-gestao-de-projetos",
    "08": "modulo08-arquitetura-de-sistemas-com-ia",
    "09": "modulo09-processamento-de-dados-e-fine-tuning-de-modelos",
  };
  const root = roots[modulo];
  if (!root) return [];
  const absRoot = path.join(REPO_ROOT, root);
  if (!existsSync(absRoot)) return [];
  const found = [];
  const walk = (dir, depth) => {
    if (depth > 3) return;
    let names;
    try {
      names = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const ent of names) {
      if (ent.name.startsWith(".")) continue;
      const abs = path.join(dir, ent.name);
      if (ent.isDirectory()) walk(abs, depth + 1);
      else if (/^Atividade/i.test(ent.name) && ent.name.toLowerCase().endsWith(".pdf")) {
        found.push(path.relative(REPO_ROOT, abs).split(path.sep).join("/"));
      }
    }
  };
  walk(absRoot, 0);
  return found.slice(0, 12);
}

function loadMeta(modulo) {
  const rel = `conteudo/modulo-${modulo}/meta.json`;
  const abs = path.join(CURSO_ROOT, rel);
  if (!existsSync(abs)) return {};
  try {
    return JSON.parse(readFileSync(abs, "utf8"));
  } catch {
    return {};
  }
}

export function loadCatalog() {
  const checkpoints = parseCheckpoints();
  const diagnostic = parseDiagnostic();
  const glossario = parseGlossario();
  const modules = [];
  const lessons = [];

  for (const id of Object.keys(TITULOS)) {
    const meta = loadMeta(id);
    const modulo = {
      id,
      titulo: meta.titulo || TITULOS[id],
      horas: HORAS[id],
      caso: meta.caso_ancora || "",
      capa: `/media/imagens/modulo-${id}-capa.png`,
      video: `/media/videos/grok/modulo-${id}-intro.mp4`,
      audio: `/media/audios/tts/modulo-${id}-narracao.mp3`,
      vtt: `/media/audios/tts/modulo-${id}-narracao.vtt`,
      deps: DEPS[id],
      optional: false,
      pdfs: pdfsDoModulo(id),
    };
    modules.push(modulo);

    const aulaId = `m${id}-aula`;
    const guiaId = `m${id}-guia`;
    lessons.push({
      id: aulaId,
      modulo: id,
      ordem: 1,
      titulo: `Aula ${id} — ${modulo.titulo}`,
      md: `conteudo/modulo-${id}/aula.md`,
      kind: "aula",
    });
    lessons.push({
      id: guiaId,
      modulo: id,
      ordem: 2,
      titulo: `Guia operacional ${id}`,
      md: `modulos/${id}.md`,
      kind: "guia",
    });
    lessons.push({
      id: `m${id}-roteiro`,
      modulo: id,
      ordem: 3,
      titulo: `Roteiro de narração ${id}`,
      md: `conteudo/modulo-${id}/roteiro-narracao.md`,
      kind: "roteiro",
    });
  }

  modules.push({
    id: "py",
    titulo: "Aprofundamento Python (opcional, Apache-2.0)",
    horas: 0,
    caso: "llm-course vendored — não substitui M08/M09",
    capa: "/media/imagens/curso-capa-hero.png",
    video: null,
    audio: null,
    vtt: null,
    deps: [],
    optional: true,
    pdfs: [],
  });
  const pyLessons = [
    {
      id: "py-readme",
      md: null,
      repoMd: "referencia/llm-course/README.md",
      titulo: "Ilha Apache — o que veio e o que não veio",
    },
    {
      id: "py-lora",
      md: null,
      repoMd: "referencia/llm-course/modulo-06-lora/README.md",
      titulo: "LoRA CPU (lab B, opcional)",
    },
    {
      id: "py-rag",
      md: null,
      repoMd: "referencia/llm-course/modulo-13-rag/README.md",
      titulo: "RAG Python (lab B, opcional)",
    },
    {
      id: "py-prod",
      md: null,
      repoMd: "referencia/llm-course/modulo-19-producao/README.md",
      titulo: "Produção (lab B, opcional)",
    },
  ];
  pyLessons.forEach((l, i) => {
    lessons.push({
      ...l,
      modulo: "py",
      ordem: i + 1,
      kind: "python",
    });
  });

  return {
    titulo: "Engenharia de Software com IA Aplicada",
    modules,
    lessons,
    checkpoints,
    diagnostic,
    glossario,
    ancora: ANCORA,
    pesos: [
      { nome: "Checkpoints de lab (M01–M03, trechos do M06)", peso: 30 },
      { nome: "Projectos âncora de módulo", peso: 50 },
      { nome: "Curadoria", peso: 10 },
      { nome: "Integração opcional ou C-COLAB", peso: 10 },
    ],
    aprovacao: {
      media: 7,
      minModulos: 7,
      obrigatorio: "04",
      umDe: ["06", "08", "09"],
    },
  };
}

export function lessonById(catalog, id) {
  return catalog.lessons.find((l) => l.id === id) || null;
}

export function moduleById(catalog, id) {
  return catalog.modules.find((m) => m.id === id) || null;
}

export function neighbors(catalog, lessonId) {
  const lesson = lessonById(catalog, lessonId);
  if (!lesson) return { prev: null, next: null };
  const same = catalog.lessons
    .filter((l) => l.modulo === lesson.modulo)
    .sort((a, b) => a.ordem - b.ordem);
  const i = same.findIndex((l) => l.id === lessonId);
  return { prev: same[i - 1] || null, next: same[i + 1] || null };
}

export function indexContent(db, catalog) {
  db.exec("DELETE FROM content_fts;");
  const ins = db.prepare("INSERT INTO content_fts (lesson_id, title, body) VALUES (?, ?, ?)");
  for (const lesson of catalog.lessons) {
    let body = "";
    if (lesson.md) {
      const abs = path.join(CURSO_ROOT, lesson.md);
      if (existsSync(abs)) body = readFileSync(abs, "utf8");
    } else if (lesson.repoMd) {
      const abs = path.join(REPO_ROOT, lesson.repoMd);
      if (existsSync(abs)) body = readFileSync(abs, "utf8");
    }
    ins.run(lesson.id, lesson.titulo, body.slice(0, 200000));
  }
}

export { TITULOS, HORAS };
