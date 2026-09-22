const NAV = [
  { section: "Pacote" },
  { path: "README.md", label: "Início" },
  { path: "syllabus.md", label: "Syllabus" },
  { path: "trilha-aprendizado.md", label: "Trilha" },
  { path: "mapa-do-repositorio.md", label: "Mapa" },
  { path: "avaliacao.md", label: "Avaliação" },
  { path: "guia-do-aluno.md", label: "Guia do aluno" },
  { path: "guia-do-instrutor.md", label: "Guia do instrutor" },
  { path: "glossario.md", label: "Glossário" },
  { path: "lacunas-e-proximos-passos.md", label: "Lacunas" },
  { path: "media/README.md", label: "Mídia" },
  { path: "videos/grok", label: "Intros Grok", kind: "grok" },
  { path: "audios", label: "Narrações TTS", kind: "tts" },
  { section: "Módulos" },
  { path: "modulos/01.md", label: "Módulo 01" },
  { path: "modulos/02.md", label: "Módulo 02" },
  { path: "modulos/03.md", label: "Módulo 03" },
  { path: "modulos/04.md", label: "Módulo 04" },
  { path: "modulos/05.md", label: "Módulo 05" },
  { path: "modulos/06.md", label: "Módulo 06" },
  { path: "modulos/07.md", label: "Módulo 07" },
  { path: "modulos/08.md", label: "Módulo 08" },
  { path: "modulos/09.md", label: "Módulo 09" },
];

const navEl = document.getElementById("nav");
const articleEl = document.getElementById("article");
const crumbEl = document.getElementById("crumb");
const heroEl = document.getElementById("hero");
const sidebarEl = document.getElementById("sidebar");
const menuBtn = document.getElementById("menu-btn");
const backdropEl = document.getElementById("backdrop");

function currentPath() {
  const raw = decodeURIComponent(location.hash.replace(/^#\/?/, "")).trim();
  return raw || "README.md";
}

function labelFor(path) {
  const item = NAV.find((entry) => entry.path === path);
  return item ? item.label : path;
}

function renderNav() {
  const frag = document.createDocumentFragment();
  for (const entry of NAV) {
    if (entry.section) {
      const title = document.createElement("p");
      title.className = "nav-section";
      title.textContent = entry.section;
      frag.appendChild(title);
      continue;
    }
    const link = document.createElement("a");
    link.href = `#/${entry.path}`;
    link.dataset.path = entry.path;
    link.textContent = entry.label;
    frag.appendChild(link);
  }
  navEl.appendChild(frag);
}

function setActive(path) {
  for (const link of navEl.querySelectorAll("a")) {
    link.classList.toggle("active", link.dataset.path === path);
  }
}

function closeMenu() {
  sidebarEl.classList.remove("open");
  menuBtn.setAttribute("aria-expanded", "false");
  backdropEl.hidden = true;
}

function openMenu() {
  sidebarEl.classList.add("open");
  menuBtn.setAttribute("aria-expanded", "true");
  backdropEl.hidden = false;
}

function grokGalleryHtml(payload) {
  const videos = payload.videos || [];
  const cards = videos
    .map((video) => {
      const duration =
        video.duration != null ? `${video.duration} s` : "duração n/d";
      return `<article class="grok-card">
  <h3>Módulo ${video.modulo} — ${video.title}</h3>
  <p class="grok-meta">${duration} · Grok Imagine · <code>${video.file}</code></p>
  <video class="grok-player" controls preload="metadata" src="${video.src}">
    Seu navegador não reproduz este MP4. <a href="${video.src}">Baixar ${video.file}</a>
  </video>
</article>`;
    })
    .join("\n");

  return `<section class="grok-gallery" aria-label="Intros Grok Imagine">
  <h2>Intros Grok Imagine</h2>
  <p>MP4 versionados em <code>curso/media/videos/grok/</code>, servidos em <code>/media/videos/grok/modulo-0N-intro.mp4</code>. Complementam (e substituem no preview) os IDs HeyGen.</p>
  <div class="grok-grid">${cards}</div>
</section>`;
}

async function loadGrokGallery() {
  const res = await fetch("/api/grok-videos");
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.message || `Falha HTTP ${res.status}`);
  }
  return grokGalleryHtml(data);
}

let ttsPayloadCache = null;

async function loadTtsPayload() {
  if (ttsPayloadCache) return ttsPayloadCache;
  const res = await fetch("/api/tts-audios");
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.message || `Falha HTTP ${res.status}`);
  }
  ttsPayloadCache = data;
  return data;
}

function formatTtsDuration(seconds) {
  if (seconds == null || Number.isNaN(Number(seconds))) return "duração n/d";
  const total = Math.round(Number(seconds));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m} min ${String(s).padStart(2, "0")} s`;
}

function moduloFromPath(pagePath) {
  const guide = pagePath.match(/^modulos\/(\d{2})\.md$/);
  if (guide) return guide[1];
  const content = pagePath.match(/^conteudo\/modulo-(\d{2})\//);
  if (content) return content[1];
  return null;
}

function ttsPlayerHtml(audio, { compact = false } = {}) {
  const duration = formatTtsDuration(audio.duration_seconds);
  const heading = compact
    ? "<h3>Narração TTS desta aula</h3>"
    : `<h3>Módulo ${audio.modulo} — ${audio.title}</h3>`;
  const roteiro = audio.source_path
    ? ` · <a href="#/${audio.source_path}">roteiro</a>`
    : "";
  const pitch = audio.pitch ? ` · pitch ${audio.pitch}` : "";
  const vttSrc = audio.vtt_src || "";
  const track = vttSrc
    ? `<track kind="captions" srclang="pt-BR" label="Português (Brasil)" src="${vttSrc}" default>`
    : "";
  const vttLink = vttSrc
    ? `<p class="tts-caption-link"><a href="${vttSrc}" download>Baixar legenda VTT</a></p>`
    : "";
  return `<article class="tts-card">
  ${heading}
  <p class="tts-meta">${duration} · ${audio.voice} · rate ${audio.rate}${pitch} · <code>${audio.file}</code>${roteiro}</p>
  <audio class="tts-player" controls preload="metadata">
    <source src="${audio.src}" type="audio/mpeg">
    ${track}
    Seu navegador não reproduz este MP3. <a href="${audio.src}">Baixar ${audio.file}</a>
  </audio>
  ${vttLink}
</article>`;
}

function ttsGalleryHtml(payload) {
  const audios = payload.audios || [];
  const cards = audios.map((audio) => ttsPlayerHtml(audio)).join("\n");
  const voice = payload.voice || "pt-BR-FranciscaNeural";
  const rate = payload.rate || "-18%";
  const pitch = payload.pitch || "-2Hz";
  return `<section class="tts-gallery" aria-label="Narrações TTS">
  <h2>Narrações TTS</h2>
  <p>MP3 e legendas WebVTT em <code>curso/media/audios/tts/</code>, voz <code>${voice}</code>, rate <code>${rate}</code>, pitch <code>${pitch}</code>. Servidos em <code>/media/audios/tts/modulo-0N-narracao.mp3</code> e <code>.vtt</code>. São a leitura falada do roteiro de cada módulo (~5,5–6 min).</p>
  <div class="tts-grid">${cards}</div>
</section>`;
}

async function loadTtsGallery() {
  return ttsGalleryHtml(await loadTtsPayload());
}

async function injectLessonTtsPlayer(pagePath) {
  const modulo = moduloFromPath(pagePath);
  if (!modulo) return;
  try {
    const payload = await loadTtsPayload();
    const audio = (payload.audios || []).find((item) => item.modulo === modulo);
    if (!audio) return;
    const player = `<aside class="tts-lesson" aria-label="Narração TTS desta aula">${ttsPlayerHtml(audio, { compact: true })}</aside>`;
    const heading = articleEl.querySelector("h1");
    if (heading) heading.insertAdjacentHTML("afterend", player);
    else articleEl.insertAdjacentHTML("afterbegin", player);
  } catch {
    // Página de aula continua sem o player se o manifesto não estiver disponível.
  }
}

async function loadPage() {
  const path = currentPath();
  setActive(path);
  crumbEl.textContent = labelFor(path);
  document.title = `${labelFor(path)} — Preview do curso`;
  heroEl.hidden = path !== "README.md";
  articleEl.innerHTML = `<p class="status">Carregando <code>${path}</code>…</p>`;
  closeMenu();

  try {
    if (path === "videos/grok") {
      articleEl.innerHTML = await loadGrokGallery();
      window.scrollTo(0, 0);
      return;
    }

    if (path === "audios") {
      articleEl.innerHTML = await loadTtsGallery();
      window.scrollTo(0, 0);
      return;
    }

    const res = await fetch(`/api/page?path=${encodeURIComponent(path)}`);
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.message || `Falha HTTP ${res.status}`);
    }
    articleEl.innerHTML = data.html;
    if (path === "media/README.md") {
      try {
        articleEl.insertAdjacentHTML("beforeend", await loadGrokGallery());
      } catch (galleryErr) {
        articleEl.insertAdjacentHTML(
          "beforeend",
          `<p class="error">Intros Grok indisponíveis: ${galleryErr.message}</p>`
        );
      }
      try {
        articleEl.insertAdjacentHTML("beforeend", await loadTtsGallery());
      } catch (galleryErr) {
        articleEl.insertAdjacentHTML(
          "beforeend",
          `<p class="error">Narrações TTS indisponíveis: ${galleryErr.message}</p>`
        );
      }
    } else {
      await injectLessonTtsPlayer(path);
    }
    window.scrollTo(0, 0);
  } catch (err) {
    articleEl.innerHTML = `<p class="error">Não foi possível abrir esta página: ${err.message}</p>`;
  }
}

menuBtn.addEventListener("click", () => {
  if (sidebarEl.classList.contains("open")) closeMenu();
  else openMenu();
});

backdropEl.addEventListener("click", closeMenu);

articleEl.addEventListener("click", (event) => {
  const anchor = event.target.closest("a");
  if (!anchor) return;
  const href = anchor.getAttribute("href") || "";
  if (href.startsWith("#/")) {
    event.preventDefault();
    const next = href.slice(2);
    if (`#/${next}` !== location.hash) {
      location.hash = `/${next}`;
    } else {
      loadPage();
    }
  }
});

window.addEventListener("hashchange", loadPage);

renderNav();
loadPage();
