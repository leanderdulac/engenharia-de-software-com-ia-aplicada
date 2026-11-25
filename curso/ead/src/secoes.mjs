/** Parte aula.md nos títulos que o texto já tem. Não inventa aula vazia. */

export function secoesDaAula(markdown) {
  const lines = String(markdown || "").split("\n");
  const heads = [];
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    if (ln.startsWith("### ")) heads.push({ i, level: 3, title: ln.slice(4).trim() });
    else if (ln.startsWith("## ")) heads.push({ i, level: 2, title: ln.slice(3).trim() });
  }
  const raw = [];
  for (let n = 0; n < heads.length; n++) {
    const h = heads[n];
    if (h.level === 2 && /conceito/i.test(h.title)) {
      let k = n + 1;
      while (k < heads.length && heads[k].level === 3) {
        const end = k + 1 < heads.length ? heads[k + 1].i : lines.length;
        raw.push({ titulo: heads[k].title, start: heads[k].i, end, kind: "secao" });
        k++;
      }
      n = k - 1;
      continue;
    }
    if (h.level === 3) continue;
    let end = lines.length;
    for (let k = n + 1; k < heads.length; k++) {
      if (heads[k].level === 2) {
        end = heads[k].i;
        break;
      }
    }
    let kind = "secao";
    let titulo = h.title;
    if (/^abertura\b/i.test(h.title)) {
      kind = "intro";
      titulo = "Introdução";
    } else if (/exerc[ií]cio/i.test(h.title)) {
      kind = "atividade";
      titulo = "Atividade";
    } else if (/passo a passo/i.test(h.title)) {
      kind = "pratica";
      titulo = "Na prática";
    } else if (/armadilha/i.test(h.title)) titulo = "Armadilhas";
    else if (/s[ií]ntese/i.test(h.title)) titulo = "Síntese";
    raw.push({ titulo, start: h.i, end, kind });
  }
  return raw;
}

export function slugTitulo(title) {
  return (
    String(title || "")
      .normalize("NFD")
      .replace(/\p{M}/gu, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 42) || "secao"
  );
}

export function idDaSecao(modulo, sec, used) {
  let base = `m${modulo}-${slugTitulo(sec.titulo)}`;
  if (sec.kind === "intro") base = `m${modulo}-intro`;
  else if (sec.kind === "atividade") base = `m${modulo}-atividade`;
  else if (sec.kind === "pratica") base = `m${modulo}-pratica`;
  let id = base;
  let n = 2;
  while (used.has(id)) id = `${base}-${n++}`;
  used.add(id);
  return id;
}
