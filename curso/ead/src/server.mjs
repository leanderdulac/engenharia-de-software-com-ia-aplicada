import express from "express";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createHash, randomBytes } from "node:crypto";
import {
  clearCookie,
  cookieHeader,
  createSession,
  destroySession,
  destroyUserSessions,
  hashPassword,
  loadSession,
  loginAllowed,
  newToken,
  parseCookies,
  recordLoginFail,
  requireCsrf,
  validEmail,
  validPassword,
  verifyPassword,
} from "./auth.mjs";
import { indexContent, lessonById, loadCatalog, moduleById, neighbors } from "./catalog.mjs";
import {
  CURSO_ROOT,
  PUBLIC_DIR,
  REPO_ROOT,
  TEXT_MAX,
  URL_MAX,
  NAME_MAX,
  dbFile,
  listenHost,
  listenPort,
  secureCookies,
  SESSION_TTL_MS,
} from "./config.mjs";
import { openDb } from "./db.mjs";
import { csrfInput, emptyState, errorPage, field, layout } from "./html.mjs";
import {
  certificateCriteria,
  completedLessons,
  enrollmentOf,
  lastLesson,
  moduleComplete,
  moduleStats,
  pendingSubmissions,
  riskFlag,
  unlockedModules,
} from "./progress.mjs";
import { securityHeaders, postRateLimit, requestLog } from "./httpguard.mjs";
import { audit, consumeReset, enrollmentWindow, integrityOk, isoDay, issueReset, putSetting, setting } from "./ops.mjs";
import { assertBootConfig, signupOpen, trustProxy } from "./runtime.mjs";
import { schemaVersion } from "./migrate.mjs";
import { escapeHtml, safeHttpUrl, sanitizeHtml } from "./sanitize.mjs";
import { createAdmin, seedDemo } from "./seed.mjs";
import {
  arquivosRelFromRequest,
  renderMarkdownPage,
  resolveMarkdownPath,
} from "../../preview/lib/markdown.mjs";
import { isInsideRoot } from "../../preview/lib/paths.mjs";
import { avaliar as avaliarColab, formatarRelatorio as formatarColab } from "../../avaliacao-colaboracao/verificar.mjs";

function bodyOf(req) {
  return req.body || {};
}

function sendHtml(res, html, status = 200) {
  res.status(status).type("html").send(html);
}

function redirect(res, to) {
  res.redirect(303, to);
}

function attachSession(req, res, db) {
  const cookies = parseCookies(req.headers.cookie);
  req.eadCookies = cookies;
  req.session = loadSession(db, cookies.ead_sid);
  if (!req.session && !cookies.ead_csrf) {
    const t = newToken();
    res.append(
      "Set-Cookie",
      cookieHeader("ead_csrf", t, { maxAge: SESSION_TTL_MS, secure: secureCookies() })
    );
    req.eadCookies.ead_csrf = t;
  }
  req.csrf = req.session?.csrf || req.eadCookies.ead_csrf;
}

function setSessionCookie(res, token) {
  res.append("Set-Cookie", cookieHeader("ead_sid", token, { maxAge: SESSION_TTL_MS, secure: secureCookies() }));
}

function staff(user) {
  return user && (user.role === "instrutor" || user.role === "admin");
}

function needAuth(req, res) {
  if (!req.session?.user) {
    redirect(res, "/entrar?next=" + encodeURIComponent(req.path));
    return false;
  }
  return true;
}

function needStaff(req, res) {
  if (!needAuth(req, res)) return false;
  if (!staff(req.session.user)) {
    sendHtml(
      res,
      layout({
        title: "Sem permissão",
        user: req.session.user,
        csrf: req.session.csrf,
        body: errorPage("Esta área é só para instrutor ou administração."),
      }),
      403
    );
    return false;
  }
  return true;
}

function needCsrf(req, res) {
  const expected = req.session ? req.session : { csrf: req.eadCookies?.ead_csrf };
  if (!requireCsrf(expected, bodyOf(req).csrf)) {
    sendHtml(
      res,
      layout({
        title: "Pedido rejeitado",
        user: req.session?.user,
        csrf: req.session?.csrf,
        body: errorPage("Token CSRF inválido ou sessão expirada. Recarregue a página."),
      }),
      403
    );
    return false;
  }
  return true;
}

function lessonMarkdown(lesson) {
  if (lesson.md) {
    const { abs, rel } = resolveMarkdownPath(lesson.md);
    const markdown = readFileSync(abs, "utf8");
    const page = renderMarkdownPage(markdown, rel);
    return { ...page, html: sanitizeHtml(page.html) };
  }
  if (lesson.repoMd) {
    const abs = path.resolve(REPO_ROOT, lesson.repoMd);
    const pyRoot = path.join(REPO_ROOT, "referencia", "llm-course");
    if (!isInsideRoot(abs, pyRoot)) {
      throw Object.assign(new Error("Ficheiro fora da ilha Apache."), { status: 403 });
    }
    if (!isInsideRoot(abs, REPO_ROOT) || !existsSync(abs)) {
      throw Object.assign(new Error("Ficheiro Python opcional ausente."), { status: 404 });
    }
    const markdown = readFileSync(abs, "utf8");
    const page = renderMarkdownPage(markdown, lesson.repoMd);
    return { ...page, html: sanitizeHtml(page.html) };
  }
  throw Object.assign(new Error("Aula sem fonte."), { status: 404 });
}

function page(req, title, body, status) {
  return layout({
    title,
    user: req.session?.user,
    csrf: req.csrf,
    flash: req.flash,
    body,
  });
}

export function createApp({ db, catalog }) {
  const app = express();
  app.disable("x-powered-by");
  if (trustProxy()) app.set("trust proxy", 1);
  app.use(securityHeaders);
  app.use(requestLog);
  app.use(postRateLimit);
  app.use(express.urlencoded({ extended: false, limit: "200kb" }));
  app.use((req, res, next) => {
    attachSession(req, res, db);
    const q = req.query || {};
    if (q.ok) req.flash = { type: "ok", text: String(q.ok) };
    if (q.erro) req.flash = { type: "erro", text: String(q.erro) };
    next();
  });
  app.use("/ead.css", express.static(path.join(PUBLIC_DIR, "ead.css")));
  app.use("/ead.js", express.static(path.join(PUBLIC_DIR, "ead.js")));
  app.get("/healthz", (_req, res) => res.json({ ok: true, service: "curso-ead" }));
  app.get("/readyz", (_req, res) => {
    try {
      const ping = db.prepare("SELECT 1 AS ok").get();
      const version = schemaVersion(db);
      if (!ping?.ok || !integrityOk(db) || version < 2) {
        res.status(503).json({ ok: false, service: "curso-ead" });
        return;
      }
      res.json({ ok: true, service: "curso-ead", schema: version });
    } catch {
      res.status(503).json({ ok: false, service: "curso-ead" });
    }
  });

  app.get("/media/*", (req, res) => {
    if (!req.session?.user) {
      res.status(401).type("text/plain; charset=utf-8").send("Autenticação necessária.");
      return;
    }
    const rel = decodeURIComponent(req.path.replace(/^\/media\//, ""));
    const abs = path.resolve(path.join(CURSO_ROOT, "media"), rel);
    if (!isInsideRoot(abs, path.join(CURSO_ROOT, "media"))) {
      res.status(403).send("Fora da pasta de mídia.");
      return;
    }
    if (!existsSync(abs)) {
      res.status(404).send("Mídia não encontrada.");
      return;
    }
    res.sendFile(abs);
  });

  app.get("/arquivos/*", (req, res) => {
    if (!req.session?.user) {
      res.status(401).type("text/plain; charset=utf-8").send("Autenticação necessária.");
      return;
    }
    try {
      const raw = req.path.replace(/^\/arquivos\//, "");
      const { abs } = arquivosRelFromRequest(raw);
      res.sendFile(abs);
    } catch (err) {
      res.status(err.status || 400).send(err.message);
    }
  });

  app.get("/preview-pacote", (req, res) => {
    if (!needAuth(req, res)) return;
    sendHtml(
      res,
      page(
        req,
        "Preview estático",
        `<h1>Preview markdown</h1>
        <p>A sala não substitui o leitor de markdown. No mesmo host, com o cookie desta sessão:</p>
        <pre>PREVIEW_REQUIRE_AUTH=1 EAD_DATA_DIR=… npm --prefix curso/preview start</pre>
        <p>Sem <code>PREVIEW_REQUIRE_AUTH=1</code> o leitor fica aberto — isso só é aceitável na máquina de desenvolvimento. <code>NODE_ENV=production</code> recusa arrancar o preview sem o portão. GitHub Pages continua desligado.</p>`
      )
    );
  });

  app.get("/", (req, res) => {
    if (req.session?.user) return redirect(res, "/dashboard");
    sendHtml(
      res,
      page(
        req,
        "Sala de aula local",
        `<article class="hero-card">
          <p class="kicker">Engenharia de Software com IA Aplicada</p>
          <h1>Sala de aula local desta pós</h1>
          <p>Nove módulos do repositório, narrações TTS, intros Grok, PDFs de missão e o checkpoint C-COLAB. Sem checkout. Sem e-mail. Contas só neste servidor.</p>
          <p><a class="btn" href="/registar">Criar conta de aluno</a> <a class="btn btn-ghost" href="/entrar">Entrar</a></p>
          <p class="muted">O preview markdown em <code>curso/preview</code> continua a ser a leitura estática. Esta sala guarda progresso e notas no SQLite.</p>
        </article>`
      )
    );
  });

  app.get("/entrar", (req, res) => {
    sendHtml(
      res,
      page(
        req,
        "Entrar",
        `<h1>Entrar</h1>
        <form method="post" action="/entrar" class="card">
          <input type="hidden" name="next" value="${escapeHtml(req.query.next || "/dashboard")}">
          ${field("E-mail", "email", { type: "email", required: true, autocomplete: "username" })}
          ${field("Senha", "password", { type: "password", required: true, autocomplete: "current-password" })}
          ${csrfInput(req.csrf)}
          <button type="submit">Entrar</button>
        </form>
        <p>Ainda não tem conta? <a href="/registar">Registo local</a>. Sem SMTP: o instrutor emite um <a href="/redefinir">token de redefinição</a> (uso único, 30 min).</p>`
      )
    );
  });

  app.post("/entrar", (req, res) => {
    if (!needCsrf(req, res)) return;
    const email = String(bodyOf(req).email || "").trim().toLowerCase();
    const password = String(bodyOf(req).password || "");
    const ip = req.ip || "0";
    const key = `${email}|${ip}`;
    if (!loginAllowed(db, key)) {
      return sendHtml(res, page(req, "Entrar", errorPage("Demasiadas tentativas. Espere alguns minutos.")), 429);
    }
    const user = db.prepare("SELECT * FROM users WHERE email = ?").get(email);
    if (!user || !verifyPassword(password, user.password_hash)) {
      recordLoginFail(db, key);
      return sendHtml(res, page(req, "Entrar", errorPage("E-mail ou senha incorrectos.")), 401);
    }
    if (user.disabled) {
      return sendHtml(res, page(req, "Entrar", errorPage("Conta desactivada. Fale com o instrutor.")), 403);
    }
    const sess = createSession(db, user.id);
    audit(db, { actorId: user.id, action: "login", target: user.role });
    setSessionCookie(res, sess.token);
    const next = String(bodyOf(req).next || "/dashboard");
    redirect(res, next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard");
  });

  app.get("/registar", (req, res) => {
    sendHtml(
      res,
      page(
        req,
        "Criar conta",
        `<h1>Criar conta local de aluno</h1>
        <form method="post" action="/registar" class="card">
          ${field("Nome a apresentar", "name", { required: true, autocomplete: "name" })}
          ${field("E-mail", "email", { type: "email", required: true, autocomplete: "username" })}
          ${field("Senha (mín. 10 caracteres)", "password", { type: "password", required: true, autocomplete: "new-password" })}
          ${csrfInput(req.csrf)}
          <button type="submit">Criar conta</button>
        </form>
        <p>O papel é sempre <strong>aluno</strong>. Instrutor/admin só via CLI no servidor. Não há verificação de e-mail. Em produção o auto-registo fica fechado salvo <code>EAD_OPEN_SIGNUP=1</code>.</p>`
      )
    );
  });

  app.post("/registar", (req, res) => {
    if (!needCsrf(req, res)) return;
    if (!signupOpen()) {
      return sendHtml(
        res,
        page(req, "Criar conta", errorPage("Auto-registo fechado nesta instalação. Peça a conta ao instrutor.")),
        403
      );
    }
    const name = String(bodyOf(req).name || "").trim().slice(0, NAME_MAX);
    const email = String(bodyOf(req).email || "").trim().toLowerCase();
    const password = String(bodyOf(req).password || "");
    if (!name || !validEmail(email) || !validPassword(password)) {
      return sendHtml(res, page(req, "Criar conta", errorPage("Nome, e-mail válido e senha com 10–128 caracteres.")), 400);
    }
    try {
      const info = db
        .prepare(
          "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, created_at) VALUES (?, ?, ?, 'aluno', 0, 0, ?)"
        )
        .run(email, hashPassword(password), name, new Date().toISOString());
      const sess = createSession(db, Number(info.lastInsertRowid));
      setSessionCookie(res, sess.token);
      redirect(res, "/onboarding");
    } catch (err) {
      if (String(err.message).includes("UNIQUE")) {
        return sendHtml(res, page(req, "Criar conta", errorPage("Já existe conta com este e-mail.")), 409);
      }
      throw err;
    }
  });

  app.post("/sair", (req, res) => {
    if (req.session && !needCsrf(req, res)) return;
    destroySession(db, req.eadCookies?.ead_sid);
    res.append("Set-Cookie", clearCookie("ead_sid", secureCookies()));
    redirect(res, "/");
  });

  app.get("/onboarding", (req, res) => {
    if (!needAuth(req, res)) return;
    const items = catalog.diagnostic;
    sendHtml(
      res,
      page(
        req,
        "Diagnóstico inicial",
        `<h1>Diagnóstico (pré-teste do piloto)</h1>
        <p>Itens oficiais de <code>curso/piloto/pre-pos-teste.md</code>. Autoavaliação 0–2. <strong>Não entra na média do curso</strong> — só orienta a trilha.</p>
        <form method="post" action="/onboarding" class="card">
          ${csrfInput(req.session.csrf)}
          ${items
            .map(
              (it) => `<fieldset class="diag">
              <legend>${escapeHtml(it.id + ". " + it.prompt)}</legend>
              <p class="muted">Liga a ${escapeHtml(it.liga)}</p>
              <label><input type="radio" name="i${it.id}" value="0" required> 0 — não demonstra</label>
              <label><input type="radio" name="i${it.id}" value="1"> 1 — parcial</label>
              <label><input type="radio" name="i${it.id}" value="2"> 2 — demonstra com evidência</label>
            </fieldset>`
            )
            .join("")}
          <button type="submit">Guardar orientação</button>
        </form>`
      )
    );
  });

  app.post("/onboarding", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const uid = req.session.user.id;
    const ins = db.prepare(
      "INSERT INTO diagnostic_answers (user_id, item_id, score) VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO UPDATE SET score = excluded.score"
    );
    for (const it of catalog.diagnostic) {
      const v = Number(bodyOf(req)["i" + it.id]);
      if (![0, 1, 2].includes(v)) {
        return sendHtml(res, page(req, "Diagnóstico", errorPage("Responda a todos os itens com 0, 1 ou 2.")), 400);
      }
      ins.run(uid, it.id, v);
    }
    db.prepare("UPDATE users SET diagnostic_done = 1 WHERE id = ?").run(uid);
    redirect(res, "/catalogo?ok=" + encodeURIComponent("Diagnóstico guardado. A orientação está no catálogo."));
  });

  app.get("/catalogo", (req, res) => {
    if (!needAuth(req, res)) return;
    const uid = req.session.user.id;
    const enr = enrollmentOf(db, uid);
    const done = new Set(completedLessons(db, uid));
    const unlocked = unlockedModules(catalog, done, Boolean(enr));
    const answers = db.prepare("SELECT item_id, score FROM diagnostic_answers WHERE user_id = ?").all(uid);
    const low = answers.filter((a) => a.score === 0).map((a) => a.item_id);
    const orient =
      answers.length === 0
        ? `<p><a href="/onboarding">Fazer o diagnóstico inicial</a> (pré-teste). Sem isso o painel não inventa desempenho.</p>`
        : `<p>Itens em 0 no diagnóstico: ${low.length ? low.join(", ") : "nenhum"}. Siga a trilha oficial; o diagnóstico não substitui C01–C09.</p>`;
    const cards = catalog.modules
      .map((m) => {
        const lock = enr && !unlocked.has(m.id);
        const href = lock ? "#" : `/modulo/${m.id}`;
        return `<article class="mod-card ${lock ? "locked" : ""}">
          <img src="${escapeHtml(m.capa)}" alt="">
          <h2>${m.optional ? "Opcional · " : ""}M${escapeHtml(m.id)} — ${escapeHtml(m.titulo)}</h2>
          <p>${escapeHtml(m.caso || "")}</p>
          <p class="muted">${m.horas ? m.horas + " h · " : ""}deps: ${
            (m.deps || []).join(", ") || "—"
          }${lock ? " · bloqueado até concluir pré-requisito" : ""}</p>
          ${lock ? "<p>Bloqueado</p>" : `<p><a class="btn" href="${href}">Abrir</a></p>`}
        </article>`;
      })
      .join("");
    sendHtml(
      res,
      page(
        req,
        "Catálogo",
        `<h1>O curso neste repositório</h1>
        ${orient}
        ${
          enr
            ? `<p>Matrícula <strong>${escapeHtml(enr.status)}</strong> em ${escapeHtml(enr.enrolled_at.slice(0, 10))}.</p>`
            : `<form method="post" action="/matricular">${csrfInput(req.session.csrf)}<button type="submit">Matricular-me (sem pagamento)</button></form>`
        }
        <div class="grid">${cards}</div>`
      )
    );
  });

  app.post("/matricular", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    if (req.session.user.role !== "aluno" && !staff(req.session.user)) {
      return sendHtml(res, page(req, "Matrícula", errorPage("Só contas de aluno se matriculam.")), 403);
    }
    const window = enrollmentWindow(db);
    if (!window.open && req.session.user.role === "aluno") {
      return sendHtml(res, page(req, "Matrícula", errorPage(window.reason)), 403);
    }
    try {
      db.prepare("INSERT INTO enrollments (user_id, status, enrolled_at) VALUES (?, 'ativa', ?)").run(
        req.session.user.id,
        new Date().toISOString()
      );
    } catch (err) {
      if (!String(err.message).includes("UNIQUE")) throw err;
    }
    redirect(res, "/dashboard?ok=" + encodeURIComponent("Matrícula activa."));
  });

  app.get("/dashboard", (req, res) => {
    if (!needAuth(req, res)) return;
    const uid = req.session.user.id;
    const enr = enrollmentOf(db, uid);
    if (!enr) {
      return sendHtml(
        res,
        page(
          req,
          "Painel",
          emptyState(
            "Ainda não há progresso para mostrar",
            "Conclua o diagnóstico e a matrícula. Não inventamos gráficos de desempenho."
          ) + `<p><a class="btn" href="/onboarding">Diagnóstico</a> <a class="btn" href="/catalogo">Catálogo</a></p>`
        )
      );
    }
    const stats = moduleStats(catalog, db, uid);
    const last = lastLesson(db, uid);
    const pending = pendingSubmissions(db, uid).filter((s) => s.status === "enviada");
    const avisos = db.prepare("SELECT title, body, created_at FROM announcements ORDER BY id DESC LIMIT 5").all();
    const continueLink = last ? `/aula/${encodeURIComponent(last.lesson_id)}` : "/modulo/01";
    sendHtml(
      res,
      page(
        req,
        "Painel",
        `<h1>Continuar</h1>
        <p><a class="btn" href="${continueLink}">${last ? "Retomar a última aula" : "Começar o Módulo 01"}</a></p>
        <section><h2>Progresso real por módulo</h2>
          <ul class="progress-list">${stats
            .map(
              (s) =>
                `<li>M${escapeHtml(s.id)} — ${escapeHtml(s.titulo)}: ${s.done}/${s.total} aulas ${
                  s.complete ? "(completo)" : ""
                }</li>`
            )
            .join("")}</ul>
        </section>
        <section><h2>Pendências</h2>
          ${
            pending.length
              ? `<ul>${pending.map((p) => `<li>${escapeHtml(p.assignment_id)} à espera de correção</li>`).join("")}</ul>`
              : "<p>Nenhuma submissão à espera de nota.</p>"
          }
        </section>
        <section><h2>Avisos internos</h2>
          ${
            avisos.length
              ? avisos
                  .map(
                    (a) =>
                      `<article class="card"><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.body)}</p><p class="muted">${escapeHtml(
                        a.created_at
                      )}</p></article>`
                  )
                  .join("")
              : "<p>Sem avisos.</p>"
          }
        </section>`
      )
    );
  });

  app.get("/trilha", (req, res) => {
    if (!needAuth(req, res)) return;
    const uid = req.session.user.id;
    const enr = enrollmentOf(db, uid);
    const done = new Set(completedLessons(db, uid));
    const unlocked = unlockedModules(catalog, done, Boolean(enr));
    const plan = db.prepare("SELECT * FROM study_plans WHERE user_id = ?").get(uid);
    sendHtml(
      res,
      page(
        req,
        "Trilha",
        `<h1>Trilha dos 9 módulos + Python opcional</h1>
        <p>Pré-requisitos: ${escapeHtml(JSON.stringify(catalog.modules.filter((m) => !m.optional).map((m) => ({ m: m.id, deps: m.deps }))))}</p>
        <ol class="trilha">${catalog.modules
          .map((m) => {
            const ok = unlocked.has(m.id);
            return `<li class="${ok ? "" : "locked"}"><a href="${ok ? "/modulo/" + m.id : "#"}">M${escapeHtml(
              m.id
            )} ${escapeHtml(m.titulo)}</a> ${m.optional ? "(opcional)" : ""} ${ok ? "" : "— bloqueado"}</li>`;
          })
          .join("")}</ol>
        <h2>Plano de estudo local</h2>
        <p>Só neste servidor. Não envia convites nem cria eventos externos.</p>
        <form method="post" action="/trilha/plano" class="card">
          ${csrfInput(req.session.csrf)}
          ${field("Horas por semana", "hours", { type: "number", value: String(plan?.hours_per_week || 8), extra: 'min="1" max="40"' })}
          ${field("Dias (ex. 1,2,3,4,5 = seg–sex)", "days", { value: plan?.weekday_mask || "1,2,3,4,5" })}
          <button type="submit">Guardar plano</button>
        </form>`
      )
    );
  });

  app.post("/trilha/plano", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const hours = Number(bodyOf(req).hours);
    const days = String(bodyOf(req).days || "").replace(/[^0-9,]/g, "").slice(0, 20);
    if (!Number.isInteger(hours) || hours < 1 || hours > 40) {
      return sendHtml(res, page(req, "Plano", errorPage("Horas: inteiro 1–40.")), 400);
    }
    db.prepare(
      "INSERT INTO study_plans (user_id, hours_per_week, weekday_mask, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET hours_per_week = excluded.hours_per_week, weekday_mask = excluded.weekday_mask, updated_at = excluded.updated_at"
    ).run(req.session.user.id, hours, days, new Date().toISOString());
    redirect(res, "/trilha?ok=" + encodeURIComponent("Plano guardado neste servidor."));
  });

  app.get("/modulo/:id", (req, res) => {
    if (!needAuth(req, res)) return;
    const mod = moduleById(catalog, req.params.id);
    if (!mod) return sendHtml(res, page(req, "Módulo", errorPage("Módulo inexistente.")), 404);
    const enr = enrollmentOf(db, req.session.user.id);
    const done = new Set(completedLessons(db, req.session.user.id));
    if (!unlockedModules(catalog, done, Boolean(enr)).has(mod.id) && req.session.user.role === "aluno") {
      return sendHtml(res, page(req, "Módulo", errorPage("Este módulo ainda está bloqueado pelos pré-requisitos da trilha.")), 403);
    }
    const aulas = catalog.lessons.filter((l) => l.modulo === mod.id);
    const cps = catalog.checkpoints.filter((c) => c.modulo === mod.id || (mod.id === "08" && c.modulo === "colab"));
    sendHtml(
      res,
      page(
        req,
        `Módulo ${mod.id}`,
        `<h1>M${escapeHtml(mod.id)} — ${escapeHtml(mod.titulo)}</h1>
        ${mod.video ? `<video controls preload="metadata" src="${escapeHtml(mod.video)}"></video>` : ""}
        ${
          mod.audio
            ? `<audio controls preload="metadata" src="${escapeHtml(mod.audio)}">${
                mod.vtt ? `<track kind="subtitles" src="${escapeHtml(mod.vtt)}" srclang="pt" label="Português" default>` : ""
              }</audio>`
            : ""
        }
        <h2>Aulas</h2>
        <ol>${aulas.map((l) => `<li><a href="/aula/${encodeURIComponent(l.id)}">${escapeHtml(l.titulo)}</a>${done.has(l.id) ? " · concluída" : ""}</li>`).join("")}</ol>
        <h2>Checkpoints (avaliação.md)</h2>
        <ul>${cps.map((c) => `<li><a href="/atividade/${encodeURIComponent(c.id)}">${escapeHtml(c.id)}</a> — ${escapeHtml(c.evidencia)}</li>`).join("")}</ul>
        ${
          mod.pdfs?.length
            ? `<h2>PDFs de missão no repositório</h2><ul>${mod.pdfs
                .map((p) => `<li><a href="/arquivos/${p.split("/").map(encodeURIComponent).join("/")}">${escapeHtml(path.basename(p))}</a></li>`)
                .join("")}</ul>`
            : ""
        }`
      )
    );
  });

  app.get("/aula/:id", (req, res) => {
    if (!needAuth(req, res)) return;
    const lesson = lessonById(catalog, req.params.id);
    if (!lesson) return sendHtml(res, page(req, "Aula", errorPage("Aula inexistente.")), 404);
    const enr = enrollmentOf(db, req.session.user.id);
    const done = new Set(completedLessons(db, req.session.user.id));
    if (req.session.user.role === "aluno" && !unlockedModules(catalog, done, Boolean(enr)).has(lesson.modulo)) {
      return sendHtml(res, page(req, "Aula", errorPage("Módulo bloqueado.")), 403);
    }
    let rendered;
    try {
      rendered = lessonMarkdown(lesson);
    } catch (err) {
      return sendHtml(res, page(req, "Aula", errorPage(err.message)), err.status || 500);
    }
    db.prepare(
      "INSERT INTO lesson_progress (user_id, lesson_id, completed, last_seen_at) VALUES (?, ?, 0, ?) ON CONFLICT(user_id, lesson_id) DO UPDATE SET last_seen_at = excluded.last_seen_at"
    ).run(req.session.user.id, lesson.id, new Date().toISOString());
    const { prev, next } = neighbors(catalog, lesson.id);
    const note = db.prepare("SELECT body FROM notes WHERE user_id = ? AND lesson_id = ?").get(req.session.user.id, lesson.id);
    const book = db.prepare("SELECT 1 FROM bookmarks WHERE user_id = ? AND lesson_id = ?").get(req.session.user.id, lesson.id);
    const mod = moduleById(catalog, lesson.modulo);
    sendHtml(
      res,
      page(
        req,
        rendered.title,
        `<nav class="crumbs" aria-label="Percurso"><a href="/modulo/${lesson.modulo}">M${escapeHtml(lesson.modulo)}</a></nav>
        <h1>${escapeHtml(rendered.title)}</h1>
        ${mod?.capa ? `<figure class="hero"><img src="${escapeHtml(mod.capa)}" alt=""></figure>` : ""}
        ${mod?.video && lesson.kind === "aula" ? `<video controls preload="metadata" src="${escapeHtml(mod.video)}"></video>` : ""}
        ${
          mod?.audio && lesson.kind === "aula"
            ? `<audio controls preload="metadata" src="${escapeHtml(mod.audio)}">${
                mod.vtt ? `<track default kind="subtitles" srclang="pt" label="Português" src="${escapeHtml(mod.vtt)}">` : ""
              }</audio>`
            : ""
        }
        <article class="md">${rendered.html}</article>
        <form method="post" action="/aula/${encodeURIComponent(lesson.id)}/concluir" class="inline">
          ${csrfInput(req.session.csrf)}
          <button type="submit">${done.has(lesson.id) ? "Já concluída (registar de novo)" : "Marcar conclusão"}</button>
        </form>
        <form method="post" action="/aula/${encodeURIComponent(lesson.id)}/marcador" class="inline">
          ${csrfInput(req.session.csrf)}
          <button type="submit">${book ? "Remover marcador" : "Marcar para voltar"}</button>
        </form>
        <form method="post" action="/aula/${encodeURIComponent(lesson.id)}/nota" class="card">
          ${csrfInput(req.session.csrf)}
          <label for="nota">Nota privada (só você)</label>
          <textarea id="nota" name="body" maxlength="${TEXT_MAX}">${escapeHtml(note?.body || "")}</textarea>
          <button type="submit">Guardar nota</button>
        </form>
        <p>${prev ? `<a href="/aula/${prev.id}">Anterior</a>` : ""} ${next ? `<a href="/aula/${next.id}">Seguinte</a>` : ""}</p>`
      )
    );
  });

  app.post("/aula/:id/concluir", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const lesson = lessonById(catalog, req.params.id);
    if (!lesson) return sendHtml(res, page(req, "Aula", errorPage("Aula inexistente.")), 404);
    const t = new Date().toISOString();
    db.prepare(
      "INSERT INTO lesson_progress (user_id, lesson_id, completed, completed_at, last_seen_at) VALUES (?, ?, 1, ?, ?) ON CONFLICT(user_id, lesson_id) DO UPDATE SET completed = 1, completed_at = excluded.completed_at, last_seen_at = excluded.last_seen_at"
    ).run(req.session.user.id, lesson.id, t, t);
    redirect(res, `/aula/${encodeURIComponent(lesson.id)}?ok=` + encodeURIComponent("Conclusão guardada."));
  });

  app.post("/aula/:id/marcador", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const lesson = lessonById(catalog, req.params.id);
    if (!lesson) return sendHtml(res, page(req, "Aula", errorPage("Aula inexistente.")), 404);
    const exists = db.prepare("SELECT 1 FROM bookmarks WHERE user_id = ? AND lesson_id = ?").get(req.session.user.id, lesson.id);
    if (exists) db.prepare("DELETE FROM bookmarks WHERE user_id = ? AND lesson_id = ?").run(req.session.user.id, lesson.id);
    else
      db.prepare("INSERT INTO bookmarks (user_id, lesson_id, created_at) VALUES (?, ?, ?)").run(
        req.session.user.id,
        lesson.id,
        new Date().toISOString()
      );
    redirect(res, `/aula/${encodeURIComponent(lesson.id)}`);
  });

  app.post("/aula/:id/nota", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const lesson = lessonById(catalog, req.params.id);
    if (!lesson) return sendHtml(res, page(req, "Aula", errorPage("Aula inexistente.")), 404);
    const body = String(bodyOf(req).body || "").slice(0, TEXT_MAX);
    const existing = db.prepare("SELECT id FROM notes WHERE user_id = ? AND lesson_id = ?").get(req.session.user.id, lesson.id);
    if (existing) {
      db.prepare("UPDATE notes SET body = ?, updated_at = ? WHERE id = ? AND user_id = ?").run(
        body,
        new Date().toISOString(),
        existing.id,
        req.session.user.id
      );
    } else {
      db.prepare("INSERT INTO notes (user_id, lesson_id, body, updated_at) VALUES (?, ?, ?, ?)").run(
        req.session.user.id,
        lesson.id,
        body,
        new Date().toISOString()
      );
    }
    redirect(res, `/aula/${encodeURIComponent(lesson.id)}?ok=` + encodeURIComponent("Nota privada guardada."));
  });

  app.get("/atividade/:id", (req, res) => {
    if (!needAuth(req, res)) return;
    const cp = catalog.checkpoints.find((c) => c.id === req.params.id);
    if (!cp) return sendHtml(res, page(req, "Actividade", errorPage("Checkpoint inexistente.")), 404);
    const subs = db
      .prepare("SELECT * FROM submissions WHERE user_id = ? AND assignment_id = ? ORDER BY attempt DESC")
      .all(req.session.user.id, cp.id);
    const last = subs[0];
    const colabHint =
      cp.kind === "colab"
        ? `<p>Cole o JSON das três tarefas. O verificador corre <strong>neste servidor</strong> e não executa código do JSON. O gabarito secreto não é enviado ao browser.</p>`
        : "";
    sendHtml(
      res,
      page(
        req,
        cp.id,
        `<h1>${escapeHtml(cp.id)}</h1>
        <p>${escapeHtml(cp.evidencia)}</p>
        ${colabHint}
        <p>Entrega: texto e/ou URL (sem upload de ficheiros nesta versão).</p>
        ${
          last?.status === "corrigida"
            ? `<section class="card"><h2>Feedback</h2><p>Nota ${escapeHtml(String(last.score))} / 10</p><p>${escapeHtml(
                last.feedback || ""
              )}</p></section>`
            : last
              ? "<p>Submissão enviada — à espera do instrutor.</p>"
              : ""
        }
        <form method="post" action="/atividade/${encodeURIComponent(cp.id)}" class="card">
          ${csrfInput(req.session.csrf)}
          <label for="body_text">Texto / evidência</label>
          <textarea id="body_text" name="body_text" maxlength="${TEXT_MAX}">${escapeHtml(last?.body_text || "")}</textarea>
          ${field("URL (https)", "body_url", { value: last?.body_url || "" })}
          ${
            cp.kind === "colab"
              ? `<label for="payload_json">JSON C-COLAB</label><textarea id="payload_json" name="payload_json" maxlength="20000"></textarea>`
              : ""
          }
          <button type="submit">Enviar tentativa</button>
        </form>
        <p class="muted">Tentativas: ${subs.length}. Rubrica genérica 0–10 em avaliacao.md. Gabaritos <code>*-z</code> não são servidos aqui.</p>`
      )
    );
  });

  app.post("/atividade/:id", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const cp = catalog.checkpoints.find((c) => c.id === req.params.id);
    if (!cp) return sendHtml(res, page(req, "Actividade", errorPage("Checkpoint inexistente.")), 404);
    const body_text = String(bodyOf(req).body_text || "").slice(0, TEXT_MAX);
    const body_url = safeHttpUrl(bodyOf(req).body_url).slice(0, URL_MAX);
    let payload = null;
    let autoScore = null;
    let autoFeedback = null;
    let status = "enviada";
    if (cp.kind === "colab") {
      const raw = String(bodyOf(req).payload_json || "").slice(0, 20000);
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch {
        return sendHtml(res, page(req, cp.id, errorPage("JSON C-COLAB inválido.")), 400);
      }
      if (parsed && typeof parsed === "object") {
        delete parsed.__proto__;
      }
      const resultado = avaliarColab(parsed);
      payload = JSON.stringify({ veredito: resultado.veredito, aprovado: resultado.aprovado, media: resultado.media_colaboracao });
      autoFeedback = formatarColab(resultado);
      autoScore = resultado.aprovado ? 8 : resultado.veredito === "reprovado_falha_critica" ? 0 : 4;
      status = "corrigida";
    } else if (!body_text && !body_url) {
      return sendHtml(res, page(req, cp.id, errorPage("Escreva um texto ou uma URL https.")), 400);
    }
    const n =
      db.prepare("SELECT COUNT(*) AS n FROM submissions WHERE user_id = ? AND assignment_id = ?").get(
        req.session.user.id,
        cp.id
      ).n + 1;
    db.prepare(
      `INSERT INTO submissions (user_id, assignment_id, attempt, body_text, body_url, payload_json, status, score, feedback, submitted_at, graded_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(
      req.session.user.id,
      cp.id,
      n,
      body_text,
      body_url,
      payload,
      status,
      autoScore,
      autoFeedback,
      new Date().toISOString(),
      status === "corrigida" ? new Date().toISOString() : null
    );
    redirect(res, `/atividade/${encodeURIComponent(cp.id)}?ok=` + encodeURIComponent("Tentativa registada."));
  });

  app.get("/caderno", (req, res) => {
    if (!needAuth(req, res)) return;
    const notes = db
      .prepare("SELECT lesson_id, body, updated_at FROM notes WHERE user_id = ? ORDER BY updated_at DESC")
      .all(req.session.user.id);
    const marks = db
      .prepare("SELECT lesson_id, created_at FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC")
      .all(req.session.user.id);
    sendHtml(
      res,
      page(
        req,
        "Caderno",
        `<h1>Caderno privado</h1>
        <h2>Marcadores</h2>
        ${
          marks.length
            ? `<ul>${marks.map((m) => `<li><a href="/aula/${encodeURIComponent(m.lesson_id)}">${escapeHtml(m.lesson_id)}</a></li>`).join("")}</ul>`
            : emptyState("Sem marcadores", "Marque uma aula para voltar depois.")
        }
        <h2>Notas</h2>
        ${
          notes.length
            ? notes
                .map(
                  (n) =>
                    `<article class="card"><h3><a href="/aula/${encodeURIComponent(n.lesson_id)}">${escapeHtml(
                      n.lesson_id
                    )}</a></h3><pre>${escapeHtml(n.body)}</pre></article>`
                )
                .join("")
            : emptyState("Sem notas", "As notas ficam só na sua conta neste SQLite.")
        }`
      )
    );
  });

  app.get("/busca", (req, res) => {
    if (!needAuth(req, res)) return;
    const q = String(req.query.q || "").trim().slice(0, 80);
    let hits = [];
    if (q.length >= 2) {
      try {
        const token = q.replace(/[^\p{L}\p{N}\s-]/gu, " ").trim();
        if (token.length >= 2) {
          hits = db
            .prepare(
              "SELECT lesson_id, title, snippet(content_fts, 2, '<mark>', '</mark>', '…', 20) AS snip FROM content_fts WHERE content_fts MATCH ? LIMIT 20"
            )
            .all(token);
        }
      } catch {
        hits = [];
      }
    }
    sendHtml(
      res,
      page(
        req,
        "Busca",
        `<h1>Busca no conteúdo do curso</h1>
        <form method="get" action="/busca" class="card" role="search">
          <label for="q">Termo</label>
          <input id="q" name="q" value="${escapeHtml(q)}" required minlength="2">
          <button type="submit">Buscar</button>
        </form>
        ${
          q && !hits.length
            ? emptyState("Nada encontrado", "Tente um termo que exista nos markdowns importados.")
            : `<ul>${hits
                .map(
                  (h) =>
                    `<li><a href="/aula/${encodeURIComponent(h.lesson_id)}">${escapeHtml(h.title)}</a><p>${h.snip}</p></li>`
                )
                .join("")}</ul>`
        }`
      )
    );
  });

  app.get("/glossario", (req, res) => {
    if (!needAuth(req, res)) return;
    sendHtml(
      res,
      page(
        req,
        "Glossário",
        `<h1>Glossário do repositório</h1>
        <dl>${catalog.glossario
          .map(
            (g) =>
              `<dt>${escapeHtml(g.termo)}</dt><dd>${escapeHtml(g.significado)} <span class="muted">${escapeHtml(
                g.onde
              )}</span></dd>`
          )
          .join("")}</dl>`
      )
    );
  });

  app.get("/duvidas", (req, res) => {
    if (!needAuth(req, res)) return;
    const uid = req.session.user.id;
    const isStaff = staff(req.session.user);
    if (!isStaff && req.query.aluno && Number(req.query.aluno) !== uid) {
      return sendHtml(res, page(req, "Dúvidas", errorPage("Não pode ver o fio de outro aluno.")), 403);
    }
    const studentId = isStaff ? Number(req.query.aluno || uid) : uid;
    const msgs = db
      .prepare(
        `SELECT m.body, m.created_at, u.name, u.role FROM messages m JOIN users u ON u.id = m.author_id
         WHERE m.student_id = ? ORDER BY m.id ASC`
      )
      .all(studentId);
    sendHtml(
      res,
      page(
        req,
        "Dúvidas",
        `<h1>Dúvidas aluno ↔ instrutor</h1>
        <p>Não é um fórum público. Mensagens ficam neste SQLite. Sem e-mail.</p>
        <ol class="thread">${msgs
          .map(
            (m) =>
              `<li><strong>${escapeHtml(m.name)}</strong> (${escapeHtml(m.role)})<p>${escapeHtml(m.body)}</p><p class="muted">${escapeHtml(
                m.created_at
              )}</p></li>`
          )
          .join("")}</ol>
        <form method="post" action="/duvidas" class="card">
          ${csrfInput(req.session.csrf)}
          ${isStaff ? `<input type="hidden" name="student_id" value="${studentId}">` : ""}
          <label for="body">Mensagem</label>
          <textarea id="body" name="body" required maxlength="${TEXT_MAX}"></textarea>
          <button type="submit">Enviar</button>
        </form>`
      )
    );
  });

  app.post("/duvidas", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const text = String(bodyOf(req).body || "").trim().slice(0, TEXT_MAX);
    if (!text) return sendHtml(res, page(req, "Dúvidas", errorPage("Mensagem vazia.")), 400);
    const isStaff = staff(req.session.user);
    const studentId = isStaff ? Number(bodyOf(req).student_id || req.session.user.id) : req.session.user.id;
    if (!isStaff && studentId !== req.session.user.id) {
      return sendHtml(res, page(req, "Dúvidas", errorPage("Isolamento: não escreve no fio alheio.")), 403);
    }
    db.prepare("INSERT INTO messages (student_id, author_id, body, created_at) VALUES (?, ?, ?, ?)").run(
      studentId,
      req.session.user.id,
      text,
      new Date().toISOString()
    );
    redirect(res, isStaff ? `/duvidas?aluno=${studentId}` : "/duvidas?ok=" + encodeURIComponent("Mensagem guardada."));
  });

  app.get("/admin", (req, res) => {
    if (!needStaff(req, res)) return;
    const alunos = db
      .prepare("SELECT id, email, name, demo, disabled FROM users WHERE role = 'aluno' ORDER BY id")
      .all();
    const rows = alunos
      .map((a) => {
        const stats = moduleStats(catalog, db, a.id);
        const doneN = stats.filter((s) => s.complete).length;
        const enr = enrollmentOf(db, a.id);
        const risk = riskFlag(stats, db.prepare("SELECT score FROM submissions WHERE user_id = ? AND score IS NOT NULL").all(a.id));
        return `<tr>
          <td>${a.demo ? "DEMONSTRAÇÃO/TESTE" : "conta"}</td>
          <td>${escapeHtml(a.name)}</td>
          <td>${escapeHtml(a.email)}</td>
          <td>${enr ? escapeHtml(enr.status) : "sem matrícula"}</td>
          <td>${doneN}/9</td>
          <td>${escapeHtml(risk || "—")}</td>
          <td>${a.disabled ? "desactivada" : "activa"} · <a href="/duvidas?aluno=${a.id}">dúvidas</a>
            <form method="post" action="/admin/conta/${a.id}/estado" class="inline">${csrfInput(req.session.csrf)}
              <button type="submit">${a.disabled ? "Reactivar" : "Desactivar"}</button></form>
            <form method="post" action="/admin/conta/${a.id}/reset" class="inline">${csrfInput(req.session.csrf)}
              <button type="submit">Token de senha</button></form>
          </td>
        </tr>`;
      })
      .join("");
    sendHtml(
      res,
      page(
        req,
        "Turma",
        `<h1>Turma</h1>
        <p><a href="/admin/export.csv">Exportar CSV</a> (sem hashes de senha). <a href="/admin/auditoria">Auditoria</a></p>
        <section class="card">
          <h2>Janela da turma</h2>
          <p>${escapeHtml(setting(db, "cohort_name") || "Sem nome")} · ${escapeHtml(setting(db, "cohort_starts") || "sem início")} → ${escapeHtml(setting(db, "cohort_ends") || "sem fim")}</p>
          <form method="post" action="/admin/turma">
            ${csrfInput(req.session.csrf)}
            ${field("Nome da turma", "cohort_name", { value: setting(db, "cohort_name") })}
            ${field("Início (AAAA-MM-DD, vazio = já aberta)", "cohort_starts", { value: setting(db, "cohort_starts") })}
            ${field("Fim (AAAA-MM-DD, vazio = sem prazo)", "cohort_ends", { value: setting(db, "cohort_ends") })}
            <button type="submit">Guardar janela</button>
          </form>
        </section>
        <table class="table"><thead><tr><th>Origem</th><th>Nome</th><th>E-mail</th><th>Matrícula</th><th>Módulos</th><th>Risco</th><th></th></tr></thead><tbody>${
          rows || `<tr><td colspan="7">Sem alunos.</td></tr>`
        }</tbody></table>`
      )
    );
  });

  app.get("/admin/export.csv", (req, res) => {
    if (!needStaff(req, res)) return;
    const alunos = db.prepare("SELECT id, email, name, demo, created_at FROM users WHERE role = 'aluno'").all();
    const lines = ["origem,nome,email,modulos_completos,media"];
    for (const a of alunos) {
      const stats = moduleStats(catalog, db, a.id);
      const crit = certificateCriteria(catalog, db, a.id);
      lines.push(
        [a.demo ? "DEMONSTRACAO/TESTE" : "conta", csv(a.name), csv(a.email), crit.n, crit.media ?? ""].join(",")
      );
    }
    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition", "attachment; filename=turma.csv");
    res.send(lines.join("\n"));
  });

  app.get("/admin/fila", (req, res) => {
    if (!needStaff(req, res)) return;
    const fila = db
      .prepare(
        `SELECT s.id, s.assignment_id, s.attempt, s.submitted_at, u.name, u.demo, u.id AS uid
         FROM submissions s JOIN users u ON u.id = s.user_id
         WHERE s.status = 'enviada' ORDER BY s.id ASC`
      )
      .all();
    sendHtml(
      res,
      page(
        req,
        "Fila",
        `<h1>Fila de correção</h1>
        ${
          fila.length
            ? `<ul>${fila
                .map(
                  (f) =>
                    `<li>${f.demo ? "[DEMONSTRAÇÃO/TESTE] " : ""}${escapeHtml(f.name)} · ${escapeHtml(
                      f.assignment_id
                    )} tentativa ${f.attempt} — <a href="/admin/correcao/${f.id}">corrigir</a></li>`
                )
                .join("")}</ul>`
            : emptyState("Fila vazia", "Não há submissões pendentes.")
        }`
      )
    );
  });

  app.get("/admin/correcao/:id", (req, res) => {
    if (!needStaff(req, res)) return;
    const sub = db
      .prepare(
        `SELECT s.*, u.name, u.demo FROM submissions s JOIN users u ON u.id = s.user_id WHERE s.id = ?`
      )
      .get(Number(req.params.id));
    if (!sub) return sendHtml(res, page(req, "Correção", errorPage("Submissão inexistente.")), 404);
    sendHtml(
      res,
      page(
        req,
        "Corrigir",
        `<h1>Corrigir ${escapeHtml(sub.assignment_id)}</h1>
        <p>${sub.demo ? "DEMONSTRAÇÃO/TESTE · " : ""}${escapeHtml(sub.name)}</p>
        <pre>${escapeHtml(sub.body_text)}</pre>
        <p>${sub.body_url ? `<a href="${escapeHtml(sub.body_url)}" rel="noopener">URL</a>` : ""}</p>
        <form method="post" action="/admin/correcao/${sub.id}" class="card">
          ${csrfInput(req.session.csrf)}
          ${field("Nota 0–10", "score", { type: "number", extra: 'min="0" max="10" step="0.5" required' })}
          <label for="feedback">Feedback</label>
          <textarea id="feedback" name="feedback" required maxlength="${TEXT_MAX}"></textarea>
          <button type="submit">Publicar nota</button>
        </form>`
      )
    );
  });

  app.post("/admin/correcao/:id", (req, res) => {
    if (!needStaff(req, res) || !needCsrf(req, res)) return;
    const id = Number(req.params.id);
    const sub = db.prepare("SELECT id FROM submissions WHERE id = ?").get(id);
    if (!sub) return sendHtml(res, page(req, "Correção", errorPage("Submissão inexistente.")), 404);
    const score = Number(bodyOf(req).score);
    const feedback = String(bodyOf(req).feedback || "").slice(0, TEXT_MAX);
    if (Number.isNaN(score) || score < 0 || score > 10) {
      return sendHtml(res, page(req, "Correção", errorPage("Nota 0–10.")), 400);
    }
    db.prepare(
      "UPDATE submissions SET status = 'corrigida', score = ?, feedback = ?, grader_id = ?, graded_at = ? WHERE id = ?"
    ).run(score, feedback, req.session.user.id, new Date().toISOString(), id);
    audit(db, { actorId: req.session.user.id, action: "nota", target: String(id) });
    redirect(res, "/admin/fila?ok=" + encodeURIComponent("Nota publicada. O aluno vê no checkpoint."));
  });

  app.get("/admin/avisos", (req, res) => {
    if (!needStaff(req, res)) return;
    const list = db.prepare("SELECT title, body, created_at FROM announcements ORDER BY id DESC").all();
    sendHtml(
      res,
      page(
        req,
        "Avisos",
        `<h1>Avisos internos</h1>
        <p>Não envia e-mail nem Slack. Só o painel do aluno.</p>
        <form method="post" action="/admin/avisos" class="card">
          ${csrfInput(req.session.csrf)}
          ${field("Título", "title", { required: true })}
          <label for="body">Texto</label>
          <textarea id="body" name="body" required maxlength="${TEXT_MAX}"></textarea>
          <button type="submit">Publicar no painel</button>
        </form>
        ${list.map((a) => `<article class="card"><h2>${escapeHtml(a.title)}</h2><p>${escapeHtml(a.body)}</p></article>`).join("")}`
      )
    );
  });

  app.post("/admin/avisos", (req, res) => {
    if (!needStaff(req, res) || !needCsrf(req, res)) return;
    const title = String(bodyOf(req).title || "").trim().slice(0, 120);
    const body = String(bodyOf(req).body || "").trim().slice(0, TEXT_MAX);
    if (!title || !body) return sendHtml(res, page(req, "Avisos", errorPage("Título e texto.")), 400);
    db.prepare("INSERT INTO announcements (author_id, title, body, created_at) VALUES (?, ?, ?, ?)").run(
      req.session.user.id,
      title,
      body,
      new Date().toISOString()
    );
    redirect(res, "/admin/avisos?ok=" + encodeURIComponent("Aviso no painel (sem e-mail)."));
  });

  app.get("/certificado", (req, res) => {
    if (!needAuth(req, res)) return;
    const crit = certificateCriteria(catalog, db, req.session.user.id);
    const existing = db.prepare("SELECT * FROM certificates WHERE user_id = ?").get(req.session.user.id);
    let extra = "";
    if (crit.ok && !existing) {
      extra = `<form method="post" action="/certificado">${csrfInput(req.session.csrf)}<button type="submit">Emitir comprovante interno</button></form>`;
    } else if (existing) {
      extra = `<p>Código <code>${escapeHtml(existing.code)}</code> · <a href="/verificar/${encodeURIComponent(
        existing.code
      )}">página pública de verificação</a></p>
      <p class="muted">Comprovante interno desta instalação. Não é diploma MEC nem acreditação.</p>`;
    } else {
      extra = `<ul>
        <li>Média (módulos com nota): ${crit.media == null ? "ainda sem notas" : crit.media.toFixed(1)} (mín. ${crit.mediaMinima})</li>
        <li>Módulos concluídos (aulas): ${crit.n} / ${crit.minModulos} (inclui M04? ${crit.temM04 ? "sim" : "não"}; um de M06/M08/M09? ${
        crit.temUmDe ? "sim" : "não"
      })</li>
      </ul><p>Os critérios vêm de <code>curso/avaliacao.md</code>. Não emitimos comprovante fictício.</p>`;
    }
    sendHtml(res, page(req, "Comprovante", `<h1>Comprovante interno</h1>${extra}`));
  });

  app.post("/certificado", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const crit = certificateCriteria(catalog, db, req.session.user.id);
    if (!crit.ok) return sendHtml(res, page(req, "Comprovante", errorPage("Critérios de avaliacao.md ainda não cumpridos.")), 403);
    const code = createHash("sha256").update(`ead:${req.session.user.id}:${randomBytes(8).toString("hex")}`).digest("hex").slice(0, 16);
    try {
      db.prepare("INSERT INTO certificates (user_id, code, issued_at, criteria_json) VALUES (?, ?, ?, ?)").run(
        req.session.user.id,
        code,
        new Date().toISOString(),
        JSON.stringify(crit)
      );
    } catch (err) {
      if (!String(err.message).includes("UNIQUE")) throw err;
    }
    redirect(res, "/certificado");
  });

  app.get("/verificar/:code?", (req, res) => {
    const code = String(req.params.code || req.query.code || "").trim();
    if (!code) {
      return sendHtml(
        res,
        page(
          req,
          "Verificar",
          `<h1>Verificar comprovante</h1>
          <form method="get" action="/verificar"><label for="code">Código</label><input id="code" name="code" required><button type="submit">Verificar</button></form>`
        )
      );
    }
    const row = db
      .prepare(
        `SELECT c.code, c.issued_at, u.name, u.demo FROM certificates c JOIN users u ON u.id = c.user_id WHERE c.code = ?`
      )
      .get(code);
    if (!row) return sendHtml(res, page(req, "Verificar", errorPage("Código desconhecido neste servidor.")), 404);
    sendHtml(
      res,
      page(
        req,
        "Verificar",
        `<h1>Comprovante válido nesta instalação</h1>
        <p>${row.demo ? "DEMONSTRAÇÃO/TESTE · " : ""}${escapeHtml(row.name)}</p>
        <p>Emitido ${escapeHtml(row.issued_at)}. Código ${escapeHtml(row.code)}.</p>
        <p><strong>Não</strong> constitui reconhecimento MEC, diploma ou acreditação externa.</p>`
      )
    );
  });

  app.get("/ajuda", (req, res) => {
    sendHtml(
      res,
      page(
        req,
        "Ajuda",
        `<h1>Ajuda técnica</h1>
        <ol>
          <li><code>cd curso/ead && npm ci && npm run migrate && npm start</code></li>
          <li>Admin: <code>EAD_ADMIN_EMAIL=… EAD_ADMIN_PASSWORD=… npm run create-admin</code></li>
          <li>Preview estático (sem login): pasta <code>curso/preview</code> na porta 3847.</li>
        </ol>
        <h2>Maturidade da autenticação</h2>
        <ul>
          <li>Senha local com scrypt; sessão HttpOnly; CSRF em POST; cabeçalhos de segurança; conta desactivável.</li>
          <li>Redefinição: token local de uso único (30 min), mostrado uma vez ao instrutor. SMTP continua desligado — nenhum e-mail é enviado.</li>
          <li>Papéis no servidor: aluno, instrutor, admin. Endpoints /admin exigem instrutor|admin.</li>
          <li>Produção (<code>NODE_ENV=production</code>) exige <code>EAD_SECURE_COOKIES=1</code>, <code>EAD_DATA_DIR</code> e recusa seed de demonstração. Uma instância, um SQLite.</li>
        </ul>
        <h2>Adaptadores desligados</h2>
        <p>SMTP, SSO, billing e streaming premium não têm botão de “sucesso”. Esta sala não cobra matrícula.</p>
        <h2>Acessibilidade</h2>
        <p>Há skip-link, <code>lang=pt-BR</code>, labels e navegação por teclado. A checagem automática <strong>não certifica WCAG</strong>.</p>`
      )
    );
  });

  app.get("/privacidade", (req, res) => {
    sendHtml(
      res,
      page(
        req,
        "Privacidade",
        `<h1>Limites de tratamento (esta instalação)</h1>
        <p>Não é consentimento jurídico genérico nem DPA. Descreve o que <strong>este</strong> processo grava.</p>
        <ul>
          <li>Conta: nome, e-mail, hash de senha, papel.</li>
          <li>Progresso, notas privadas, marcadores, submissões (texto/URL), mensagens aluno↔instrutor.</li>
          <li>Não pedimos CPF, saúde, biometria nem cartão.</li>
          <li>Sem analytics de terceiros. O log JSON tem método, caminho e estado — sem senha, cookie ou token.</li>
          <li>Auditoria interna: login, nota, aviso, desactivação, token de senha, janela da turma. Sem o conteúdo da senha.</li>
          <li>CSV da turma: nome, e-mail, módulos, média — só para instrutor autenticado.</li>
          <li>C-COLAB: o JSON é avaliado no servidor; o gabarito não vai para o cliente.</li>
        </ul>`
      )
    );
  });

  app.get("/conta", (req, res) => {
    if (!needAuth(req, res)) return;
    sendHtml(
      res,
      page(
        req,
        "Conta",
        `<h1>Conta</h1>
        <p>${escapeHtml(req.session.user.name)} · ${escapeHtml(req.session.user.email)}</p>
        <form method="post" action="/conta/senha" class="card">
          ${csrfInput(req.session.csrf)}
          ${field("Senha actual", "current", { type: "password", required: true, autocomplete: "current-password" })}
          ${field("Senha nova (mín. 10)", "next", { type: "password", required: true, autocomplete: "new-password" })}
          <button type="submit">Alterar senha</button>
        </form>
        <p class="muted">Alterar a senha encerra as outras sessões desta conta. Não envia e-mail.</p>`
      )
    );
  });

  app.post("/conta/senha", (req, res) => {
    if (!needAuth(req, res) || !needCsrf(req, res)) return;
    const current = String(bodyOf(req).current || "");
    const next = String(bodyOf(req).next || "");
    const user = db.prepare("SELECT * FROM users WHERE id = ?").get(req.session.user.id);
    if (!user || !verifyPassword(current, user.password_hash)) {
      return sendHtml(res, page(req, "Conta", errorPage("Senha actual incorrecta.")), 401);
    }
    if (!validPassword(next) || next === current) {
      return sendHtml(res, page(req, "Conta", errorPage("A senha nova precisa de 10–128 caracteres e ser diferente da actual.")), 400);
    }
    db.prepare("UPDATE users SET password_hash = ?, password_changed_at = ? WHERE id = ?").run(
      hashPassword(next),
      new Date().toISOString(),
      user.id
    );
    destroyUserSessions(db, user.id);
    audit(db, { actorId: user.id, action: "senha_alterada", target: String(user.id) });
    const sess = createSession(db, user.id);
    setSessionCookie(res, sess.token);
    redirect(res, "/conta?ok=" + encodeURIComponent("Senha alterada. As outras sessões foram encerradas."));
  });

  app.get("/redefinir", (req, res) => {
    sendHtml(
      res,
      page(
        req,
        "Redefinir senha",
        `<h1>Redefinir senha</h1>
        <p>Cole o token que o instrutor lhe mostrou. Não há e-mail. O token vale 30 minutos e só uma vez.</p>
        <form method="post" action="/redefinir" class="card">
          ${csrfInput(req.csrf)}
          ${field("Token", "token", { required: true, autocomplete: "one-time-code" })}
          ${field("Senha nova", "password", { type: "password", required: true, autocomplete: "new-password" })}
          <button type="submit">Definir senha</button>
        </form>`
      )
    );
  });

  app.post("/redefinir", (req, res) => {
    if (!needCsrf(req, res)) return;
    const token = String(bodyOf(req).token || "").trim();
    const password = String(bodyOf(req).password || "");
    if (!validPassword(password)) {
      return sendHtml(res, page(req, "Redefinir", errorPage("Senha: 10 a 128 caracteres.")), 400);
    }
    const userId = consumeReset(db, token);
    if (!userId) {
      return sendHtml(res, page(req, "Redefinir", errorPage("Token inválido, usado ou expirado.")), 400);
    }
    db.prepare("UPDATE users SET password_hash = ?, password_changed_at = ? WHERE id = ?").run(
      hashPassword(password),
      new Date().toISOString(),
      userId
    );
    destroyUserSessions(db, userId);
    audit(db, { actorId: userId, action: "senha_redefinida", target: String(userId) });
    redirect(res, "/entrar?ok=" + encodeURIComponent("Senha actualizada. Entre com a senha nova."));
  });

  app.post("/admin/turma", (req, res) => {
    if (!needStaff(req, res) || !needCsrf(req, res)) return;
    const name = String(bodyOf(req).cohort_name || "").trim().slice(0, 80);
    const starts = isoDay(bodyOf(req).cohort_starts);
    const ends = isoDay(bodyOf(req).cohort_ends);
    if (starts === null || ends === null) {
      return sendHtml(res, page(req, "Turma", errorPage("Datas no formato AAAA-MM-DD, ou vazias.")), 400);
    }
    if (starts && ends && ends < starts) {
      return sendHtml(res, page(req, "Turma", errorPage("A data de fim é anterior ao início.")), 400);
    }
    putSetting(db, "cohort_name", name);
    putSetting(db, "cohort_starts", starts);
    putSetting(db, "cohort_ends", ends);
    audit(db, { actorId: req.session.user.id, action: "janela_turma", target: `${starts || "aberta"}..${ends || "sem-fim"}` });
    redirect(res, "/admin?ok=" + encodeURIComponent("Janela da turma guardada."));
  });

  app.post("/admin/conta/:id/estado", (req, res) => {
    if (!needStaff(req, res) || !needCsrf(req, res)) return;
    const id = Number(req.params.id);
    const user = db.prepare("SELECT id, role, disabled FROM users WHERE id = ?").get(id);
    if (!user || user.role !== "aluno") {
      return sendHtml(res, page(req, "Turma", errorPage("Só contas de aluno se desactivam aqui.")), 404);
    }
    const next = user.disabled ? 0 : 1;
    db.prepare("UPDATE users SET disabled = ? WHERE id = ?").run(next, id);
    if (next) destroyUserSessions(db, id);
    audit(db, { actorId: req.session.user.id, action: next ? "conta_desactivada" : "conta_reactivada", target: String(id) });
    redirect(res, "/admin?ok=" + encodeURIComponent(next ? "Conta desactivada." : "Conta reactivada."));
  });

  app.post("/admin/conta/:id/reset", (req, res) => {
    if (!needStaff(req, res) || !needCsrf(req, res)) return;
    const id = Number(req.params.id);
    const user = db.prepare("SELECT id, role, email, demo FROM users WHERE id = ?").get(id);
    if (!user || user.role === "admin") {
      return sendHtml(res, page(req, "Token", errorPage("Não se emite token para administração por este formulário.")), 403);
    }
    const token = issueReset(db, id);
    audit(db, { actorId: req.session.user.id, action: "token_senha", target: String(id) });
    sendHtml(
      res,
      page(
        req,
        "Token de senha",
        `<h1>Token de uso único</h1>
        <p>${user.demo ? "DEMONSTRAÇÃO/TESTE · " : ""}${escapeHtml(user.email)}</p>
        <p>Mostre este token à pessoa. Não é enviado por e-mail. Expira em 30 minutos e não volta a aparecer.</p>
        <p><code>${escapeHtml(token)}</code></p>
        <p><a href="/admin">Voltar à turma</a></p>`
      )
    );
  });

  app.get("/admin/auditoria", (req, res) => {
    if (!needStaff(req, res)) return;
    const rows = db
      .prepare(
        `SELECT a.action, a.target, a.created_at, u.email AS actor
         FROM audit_log a LEFT JOIN users u ON u.id = a.actor_id
         ORDER BY a.id DESC LIMIT 100`
      )
      .all();
    sendHtml(
      res,
      page(
        req,
        "Auditoria",
        `<h1>Auditoria</h1>
        <p>Últimos 100 eventos desta instalação. Sem senhas nem tokens.</p>
        <table class="table"><thead><tr><th>Quando</th><th>Quem</th><th>Acção</th><th>Alvo</th></tr></thead><tbody>
        ${
          rows.length
            ? rows
                .map(
                  (r) =>
                    `<tr><td>${escapeHtml(r.created_at)}</td><td>${escapeHtml(r.actor || "—")}</td><td>${escapeHtml(
                      r.action
                    )}</td><td>${escapeHtml(r.target)}</td></tr>`
                )
                .join("")
            : `<tr><td colspan="4">Sem eventos.</td></tr>`
        }
        </tbody></table>`
      )
    );
  });

  app.use((err, req, res, _next) => {
    console.error("[ead]", err.message);
    sendHtml(
      res,
      layout({
        title: "Erro",
        user: req.session?.user,
        csrf: req.session?.csrf,
        body: errorPage("Falha interna. Nada foi enviado para fora deste processo."),
      }),
      500
    );
  });

  return app;
}

function csv(v) {
  const s = String(v ?? "");
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function boot({ dbPath, seedDemoPasswords, createAdminOpts } = {}) {
  const db = openDb(dbPath || dbFile());
  const catalog = loadCatalog();
  indexContent(db, catalog);
  if (createAdminOpts) createAdmin(db, createAdminOpts);
  if (seedDemoPasswords) seedDemo(db, seedDemoPasswords);
  return { app: createApp({ db, catalog }), db, catalog };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  assertBootConfig();
  const { app, db } = boot();
  const host = listenHost();
  const port = listenPort();
  const server = app.listen(port, host, () => {
    console.log(
      JSON.stringify({
        t: new Date().toISOString(),
        msg: "ead-listen",
        host,
        port,
        schema: schemaVersion(db),
        production: process.env.NODE_ENV === "production",
      })
    );
  });
  const stop = (signal) => {
    console.log(JSON.stringify({ t: new Date().toISOString(), msg: "ead-shutdown", signal }));
    server.close(() => {
      try {
        db.close();
      } catch {
        /* ignore */
      }
      process.exit(0);
    });
    setTimeout(() => process.exit(1), 10_000).unref();
  };
  process.on("SIGTERM", () => stop("SIGTERM"));
  process.on("SIGINT", () => stop("SIGINT"));
}
