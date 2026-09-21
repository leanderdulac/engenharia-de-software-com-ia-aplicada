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

async function loadPage() {
  const path = currentPath();
  setActive(path);
  crumbEl.textContent = labelFor(path);
  document.title = `${labelFor(path)} — Preview do curso`;
  heroEl.hidden = path !== "README.md";
  articleEl.innerHTML = `<p class="status">Carregando <code>${path}</code>…</p>`;
  closeMenu();

  try {
    const res = await fetch(`/api/page?path=${encodeURIComponent(path)}`);
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.message || `Falha HTTP ${res.status}`);
    }
    articleEl.innerHTML = data.html;
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
