import { escapeHtml } from "./sanitize.mjs";

export function layout({ title, user, csrf, flash, body, wide }) {
  const role = user?.role;
  const demo = user?.demo
    ? `<p class="banner-demo" role="status">Conta <strong>DEMONSTRAÇÃO/TESTE</strong> — dados sintéticos, não é aluno real.</p>`
    : "";
  const flashHtml = flash
    ? `<p class="flash flash-${escapeHtml(flash.type || "info")}" role="status">${escapeHtml(flash.text)}</p>`
    : "";
  const navAluno = user
    ? `
      <a href="/dashboard">Painel</a>
      <a href="/catalogo">Curso</a>
      <a href="/trilha">Trilha</a>
      <a href="/caderno">Caderno</a>
      <a href="/busca">Busca</a>
      <a href="/glossario">Glossário</a>
      <a href="/duvidas">Dúvidas</a>
      <a href="/certificado">Comprovante</a>
      <a href="/ajuda">Ajuda</a>
      <a href="/privacidade">Privacidade</a>`
    : `
      <a href="/">Início</a>
      <a href="/entrar">Entrar</a>
      <a href="/registar">Criar conta local</a>
      <a href="/ajuda">Ajuda</a>
      <a href="/privacidade">Privacidade</a>
      <a href="/verificar">Verificar comprovante</a>`;
  const navStaff =
    role === "instrutor" || role === "admin"
      ? `<a href="/admin">Turma</a><a href="/admin/fila">Fila de correção</a><a href="/admin/avisos">Avisos</a>`
      : "";
  const who = user
    ? `<span class="who">${escapeHtml(user.name)} · ${escapeHtml(user.role)}</span>
       <form method="post" action="/sair" class="inline">
         <input type="hidden" name="csrf" value="${escapeHtml(csrf || "")}">
         <button type="submit">Sair</button>
       </form>`
    : "";

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)} — Engenharia de Software com IA Aplicada</title>
  <meta name="description" content="Sala de aula local da pós Engenharia de Software com IA Aplicada. Sem pagamento. Sem envio de e-mail.">
  <link rel="stylesheet" href="/ead.css">
</head>
<body>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  ${demo}
  <header class="top">
    <div class="brand">
      <p class="kicker">Pós-graduação · sala local</p>
      <a href="${user ? "/dashboard" : "/"}" class="brand-link">Engenharia de Software com IA Aplicada</a>
    </div>
    <button type="button" class="menu-btn" id="menu-btn" aria-controls="nav-principal" aria-expanded="false">Menu</button>
    <div class="session">${who}</div>
  </header>
  <div class="shell ${wide ? "shell-wide" : ""}">
    <nav class="nav" id="nav-principal" aria-label="Principal">
      ${navAluno}
      ${navStaff}
      <a href="/preview-pacote">Preview markdown (estático)</a>
    </nav>
    <main id="conteudo">
      ${flashHtml}
      ${body}
    </main>
  </div>
  <footer class="foot">
    <p>Material do curso: CC BY-NC-ND 4.0. Código desta sala: ver <a href="/ajuda">ajuda</a>. GitHub Pages não hospeda este backend. Comprovante interno ≠ reconhecimento MEC.</p>
  </footer>
  <script src="/ead.js" defer></script>
</body>
</html>`;
}

export function field(label, name, { type = "text", value = "", required, autocomplete, extra } = {}) {
  const id = `f-${name}`;
  return `<div class="field">
    <label for="${id}">${escapeHtml(label)}</label>
    <input id="${id}" name="${escapeHtml(name)}" type="${escapeHtml(type)}" value="${escapeHtml(value)}" ${
      required ? "required" : ""
    } ${autocomplete ? `autocomplete="${escapeHtml(autocomplete)}"` : ""} ${extra || ""}>
  </div>`;
}

export function csrfInput(csrf) {
  return `<input type="hidden" name="csrf" value="${escapeHtml(csrf || "")}">`;
}

export function emptyState(title, text) {
  return `<section class="empty" role="status"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(text)}</p></section>`;
}

export function errorPage(message) {
  return `<section class="empty error"><h1>Não foi possível concluir</h1><p>${escapeHtml(message)}</p><p><a href="/dashboard">Voltar ao painel</a></p></section>`;
}
