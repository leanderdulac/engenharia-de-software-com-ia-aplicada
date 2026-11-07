import { aulasDoModulo, DEPS } from "./catalog.mjs";

export function enrollmentOf(db, userId) {
  return db.prepare("SELECT * FROM enrollments WHERE user_id = ?").get(userId) || null;
}

export function completedLessons(db, userId) {
  return db
    .prepare("SELECT lesson_id FROM lesson_progress WHERE user_id = ? AND completed = 1")
    .all(userId)
    .map((r) => r.lesson_id);
}

export function lastLesson(db, userId) {
  return (
    db
      .prepare(
        "SELECT lesson_id, last_seen_at FROM lesson_progress WHERE user_id = ? ORDER BY last_seen_at DESC LIMIT 1"
      )
      .get(userId) || null
  );
}

export function conjuntoAntigoCompleto(doneSet, modulo) {
  return ["aula", "guia", "roteiro"].every((k) => doneSet.has(`m${modulo}-${k}`));
}

export function moduleLessonIds(catalog, modulo) {
  return aulasDoModulo(catalog, modulo).map((l) => l.id);
}

export function moduleComplete(catalog, doneSet, modulo) {
  const ids = moduleLessonIds(catalog, modulo);
  if (!ids.length) return false;
  if (ids.every((id) => doneSet.has(id))) return true;
  return conjuntoAntigoCompleto(doneSet, modulo);
}

/** Estado de um módulo para um aluno. Staff não usa isto. */
export function moduleGate(catalog, mod, { enrolled, doneSet }) {
  const deps = mod.optional ? [] : mod.deps || DEPS[mod.id] || [];
  const missing = deps.filter((d) => !moduleComplete(catalog, doneSet, d));
  if (!enrolled) {
    const after = mod.optional
      ? "É opcional, não substitui a trilha e não tem pré-requisito."
      : missing.length
        ? `Depois da matrícula, ainda pede as aulas de ${missing.map((d) => "M" + d).join(", ")}.`
        : "Depois da matrícula abre sem pré-requisito.";
    return { open: false, reason: "sem-matricula", missing, detail: `Aguardando matrícula. ${after}` };
  }
  if (mod.optional) {
    return {
      open: true,
      reason: "opcional",
      missing: [],
      detail: "Opcional. Não substitui os módulos da trilha e não tem pré-requisito.",
    };
  }
  if (missing.length) {
    return {
      open: false,
      reason: "pre-requisito",
      missing,
      detail: `Pré-requisito pendente: concluir as aulas de ${missing.map((d) => "M" + d).join(", ")}.`,
    };
  }
  return {
    open: true,
    reason: "disponivel",
    missing: [],
    detail: deps.length ? `Pré-requisito concluído: ${deps.map((d) => "M" + d).join(", ")}.` : "Disponível. Sem pré-requisito.",
  };
}

export function unlockedModules(catalog, doneSet, enrolled) {
  const out = new Set();
  for (const mod of catalog.modules) {
    if (moduleGate(catalog, mod, { enrolled, doneSet }).open) out.add(mod.id);
  }
  return out;
}

export function moduleStats(catalog, db, userId) {
  const done = new Set(completedLessons(db, userId));
  return catalog.modules
    .filter((m) => !m.optional)
    .map((m) => {
      const ids = moduleLessonIds(catalog, m.id);
      const antigo = conjuntoAntigoCompleto(done, m.id);
      const doneN = antigo ? ids.length : ids.filter((id) => done.has(id)).length;
      return {
        id: m.id,
        titulo: m.titulo,
        total: ids.length,
        done: doneN,
        complete: ids.length > 0 && doneN === ids.length,
        antigo,
      };
    });
}

export function pendingSubmissions(db, userId) {
  return db
    .prepare(
      `SELECT assignment_id, MAX(attempt) AS attempt, status, score, submitted_at
       FROM submissions WHERE user_id = ? GROUP BY assignment_id`
    )
    .all(userId);
}

export function gradesOf(db, userId) {
  const rows = db
    .prepare(
      `SELECT assignment_id, score FROM submissions
       WHERE user_id = ? AND status = 'corrigida' AND score IS NOT NULL`
    )
    .all(userId);
  return rows;
}

export function mediaPonderada(catalog, grades) {
  const byMod = {};
  for (const g of grades) {
    const cp = catalog.checkpoints.find((c) => c.id === g.assignment_id);
    if (!cp || cp.modulo === "colab") continue;
    byMod[cp.modulo] = byMod[cp.modulo] || [];
    byMod[cp.modulo].push(Number(g.score));
  }
  const mods = Object.keys(byMod);
  if (!mods.length) return null;
  const medias = mods.map((m) => byMod[m].reduce((a, b) => a + b, 0) / byMod[m].length);
  return medias.reduce((a, b) => a + b, 0) / medias.length;
}

export function certificateCriteria(catalog, db, userId) {
  const done = new Set(completedLessons(db, userId));
  const stats = moduleStats(catalog, db, userId);
  const completeIds = stats.filter((s) => s.complete).map((s) => s.id);
  const grades = gradesOf(db, userId);
  const media = mediaPonderada(catalog, grades);
  const { aprovacao } = catalog;
  const temM04 = completeIds.includes(aprovacao.obrigatorio);
  const temUmDe = aprovacao.umDe.some((id) => completeIds.includes(id));
  const n = completeIds.length;
  const mediaOk = media != null && media >= aprovacao.media;
  const ok = n >= aprovacao.minModulos && temM04 && temUmDe && mediaOk;
  return {
    ok,
    media,
    modulosCompletos: completeIds,
    n,
    minModulos: aprovacao.minModulos,
    temM04,
    temUmDe,
    mediaMinima: aprovacao.media,
  };
}

export function riskFlag(stats, grades) {
  const incomplete = stats.filter((s) => !s.complete && s.id !== "py");
  const ungradedWait = grades.length === 0 && stats.some((s) => s.done > 0);
  if (incomplete.filter((s) => s.done === 0).length >= 6 && stats.some((s) => s.done > 0)) {
    return "sem progresso na maior parte da trilha";
  }
  if (ungradedWait) return "entregas ainda sem nota";
  return null;
}
