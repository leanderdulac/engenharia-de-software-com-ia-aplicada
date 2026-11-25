const btn = document.getElementById("menu-btn");
const nav = document.getElementById("nav-principal");
if (btn && nav) {
  btn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

const here = location.pathname;
for (const a of document.querySelectorAll(".nav a")) {
  try {
    const u = new URL(a.href, location.origin);
    if (u.pathname === here) a.setAttribute("aria-current", "page");
  } catch {
    /* ignore */
  }
}
