import { escapeHtml } from "./sanitize.mjs";

function mark() {
  return `<span class="mark" aria-hidden="true"><i></i><i></i><i></i></span>`;
}

export function layout({ title, user, csrf, flash, body, signup = false, variant }) {
  const role = user?.role;
  const mode = variant || (user ? "app" : "gate");
  const home = user ? "/dashboard" : "/";
  const demo = user?.demo
    ? `<p class="banner-demo" role="status">Conta <strong>DEMONSTRAÇÃO/TESTE</strong> — dados sintéticos, não é aluno real.</p>`
    : "";
  const flashHtml = flash
    ? `<p class="flash flash-${escapeHtml(flash.type || "info")}" role="status">${escapeHtml(flash.text)}</p>`
    : "";
  const brand = `<a class="brand-link" href="${home}">
      ${mark()}
      <span class="brand-text">
        <span class="brand-name">Oficina</span>
        <span class="brand-course">Engenharia de Software com IA Aplicada</span>
      </span>
    </a>`;
  const who = user
    ? `<span class="who">${escapeHtml(user.name)}<span class="who-role">${escapeHtml(user.role)}</span></span>
       <form method="post" action="/sair" class="inline">
         <input type="hidden" name="csrf" value="${escapeHtml(csrf || "")}">
         <button type="submit" class="btn btn-ghost">Sair</button>
       </form>`
    : `<a class="btn" href="/entrar">Entrar</a>`;
  const nav = user
    ? `<p class="nav-label">Estudar</p>
      <a href="/dashboard">Painel</a>
      <a href="/catalogo">Curso</a>
      <a href="/trilha">Trilha</a>
      <p class="nav-label">Na aula</p>
      <a href="/caderno">Caderno</a>
      <a href="/busca">Busca</a>
      <a href="/glossario">Glossário</a>
      <p class="nav-label">Turma</p>
      <a href="/duvidas">Dúvidas</a>
      <a href="/certificado">Comprovante</a>
      <p class="nav-label">Conta</p>
      <a href="/conta">Conta</a>
      <a href="/ajuda">Ajuda</a>
      <a href="/privacidade">Privacidade</a>
      ${
        role === "instrutor" || role === "admin"
          ? `<p class="nav-label">Equipa</p>
             <a href="/admin">Turma</a>
             <a href="/admin/fila">Fila de correção</a>
             <a href="/admin/avisos">Avisos</a>
             <a href="/admin/auditoria">Auditoria</a>`
          : ""
      }`
    : `<a href="/entrar">Entrar</a>
      ${signup ? `<a href="/registar">Criar conta local</a>` : ""}
      <a href="/redefinir">Redefinir senha</a>
      <a href="/verificar">Verificar comprovante</a>
      <a href="/ajuda">Ajuda</a>
      <a href="/privacidade">Privacidade</a>`;

  const sidebar =
    mode === "landing"
      ? ""
      : `<nav class="nav" id="nav-principal" aria-label="Principal">${nav}</nav>`;

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)} — Engenharia de Software com IA Aplicada</title>
  <meta name="description" content="Oficina: sala de aula local da pós Engenharia de Software com IA Aplicada. Sem pagamento. Sem envio de e-mail.">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/ead.css">
</head>
<body class="theme-oficina is-${escapeHtml(mode)}">
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  ${demo}
  <header class="top">
    ${brand}
    ${mode === "landing" ? "" : `<button type="button" class="menu-btn" id="menu-btn" aria-controls="nav-principal" aria-expanded="false">Menu</button>`}
    <div class="session">${who}</div>
  </header>
  <div class="shell">
    ${sidebar}
    <main id="conteudo">
      ${flashHtml}
      ${body}
    </main>
  </div>
  <footer class="foot">
    <p>Oficina é a sala local desta pós. Material do curso: CC BY-NC-ND 4.0. Comprovante interno não é reconhecimento MEC.</p>
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
