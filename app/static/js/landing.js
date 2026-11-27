/* NodoSur landing: escenas con scroll, apariciones, menú, formulario y chat. Sin dependencias. */
(() => {
  "use strict";
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  /* ---------- Header ---------- */
  const header = $(".site-header");
  const onScrollHeader = () => header && header.classList.toggle("scrolled", window.scrollY > 24);

  /* ---------- Menú móvil ---------- */
  const toggle = $(".nav-toggle");
  const menu = $("#nav-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    $$("a", menu).forEach((a) =>
      a.addEventListener("click", () => {
        menu.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      })
    );
  }

  /* ---------- Escenas fijadas: progreso 0..1 según el scroll ---------- */
  const scenes = $$("[data-scene]");
  const heroLines = $$(".hero-scene .console-log li");
  const iaSteps = $$(".ia-steps li");
  const iaNodes = $$(".ia-visual .node");
  const iaWires = $$(".ia-visual .wire");

  const progressOf = (el) => {
    const rect = el.getBoundingClientRect();
    const total = el.offsetHeight - window.innerHeight;
    if (total <= 0) return 1;
    return Math.min(1, Math.max(0, -rect.top / total));
  };

  const renderScenes = () => {
    scenes.forEach((scene) => {
      const p = progressOf(scene);
      if (scene.classList.contains("hero-scene")) {
        // la consola termina de revelarse al 70% de la escena
        const reveal = Math.min(1, p / 0.7);
        scene.style.setProperty("--p", reveal.toFixed(4));
        scene.classList.toggle("done", reveal >= 1);
        scene.classList.toggle("copy-off", reveal > 0.42);
        const lit = Math.floor(Math.max(0, (p - 0.25) / 0.6) * (heroLines.length + 1));
        heroLines.forEach((li, i) => li.classList.toggle("on", i < lit));
      } else {
        scene.style.setProperty("--p", p.toFixed(4));
        const steps = Number(scene.dataset.steps || 1);
        const active = Math.min(steps - 1, Math.floor(p * steps));
        iaSteps.forEach((li, i) => li.classList.toggle("active", i === active));
        iaNodes.forEach((n, i) => n.classList.toggle("lit", i <= active));
        iaWires.forEach((w, i) => w.classList.toggle("lit", i < active));
      }
    });
  };

  if (reduce) {
    heroLines.forEach((li) => li.classList.add("on"));
    iaSteps.forEach((li) => li.classList.add("active"));
    iaNodes.forEach((n) => n.classList.add("lit"));
    scenes.forEach((s) => s.style.setProperty("--p", "1"));
  }

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      onScrollHeader();
      if (!reduce) renderScenes();
      ticking = false;
    });
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  /* ---------- Aparición al entrar en pantalla ---------- */
  const revealEls = $$("[data-reveal]");
  if (reduce || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("is-visible"));
  } else {
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        }),
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );
    revealEls.forEach((el, i) => {
      el.style.transitionDelay = `${(i % 3) * 70}ms`;
      io.observe(el);
    });
  }

  /* ---------- Botones que preseleccionan servicio ---------- */
  $$("[data-service]").forEach((a) =>
    a.addEventListener("click", () => {
      const sel = $("#c-service");
      if (sel) sel.value = a.dataset.service;
    })
  );

  /* ---------- Formulario de contacto ---------- */
  const form = $("#contact-form");
  if (form) {
    const status = $(".form-status", form);
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      status.className = "form-status";
      const data = Object.fromEntries(new FormData(form).entries());
      const name = $("#c-name");
      const email = $("#c-email");
      let bad = null;
      [name, email].forEach((f) => f.removeAttribute("aria-invalid"));
      if ((data.name || "").trim().length < 2) bad = name;
      else if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test((data.email || "").trim())) bad = email;
      if (bad) {
        bad.setAttribute("aria-invalid", "true");
        status.textContent = bad === name ? "Escribe tu nombre." : "Revisa tu correo, parece incompleto.";
        status.classList.add("err");
        bad.focus();
        return;
      }
      if ((data.service || "").includes("ERP · demo")) data.kind = "erp_demo";
      const btn = $("button[type=submit]", form);
      btn.disabled = true;
      status.textContent = "Enviando…";
      try {
        const res = await fetch("/api/contact", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error(res.status === 429 ? "Demasiados envíos, intenta más tarde." : "No pudimos enviar tu solicitud.");
        form.reset();
        status.textContent = "¡Listo! Te escribiremos en menos de 24 horas hábiles.";
        status.classList.add("ok");
      } catch (err) {
        status.textContent = `${err.message} También puedes escribir a contacto@nodosur.cl.`;
        status.classList.add("err");
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* ---------- Chat Nodo ---------- */
  const chat = $("#chat");
  const log = $("#chat-log");
  const chatForm = $("#chat-form");
  const input = $("#chat-input");
  const fab = $(".chat-fab");
  const history = [];
  let lastOpener = null;

  const openChat = (opener) => {
    lastOpener = opener || fab;
    chat.hidden = false;
    fab.setAttribute("aria-expanded", "true");
    input.focus();
  };
  const closeChat = () => {
    chat.hidden = true;
    fab.setAttribute("aria-expanded", "false");
    (lastOpener || fab).focus();
  };
  const addMsg = (text, who) => {
    const li = document.createElement("li");
    li.className = `msg ${who}`;
    li.textContent = text;
    log.appendChild(li);
    log.scrollTop = log.scrollHeight;
    return li;
  };
  const ask = async (text) => {
    const q = text.trim().slice(0, 800);
    if (!q) return;
    addMsg(q, "user");
    history.push({ role: "user", content: q });
    const typing = addMsg("Nodo está escribiendo…", "bot typing");
    try {
      const res = await fetch("/api/assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history.slice(-8) }),
      });
      const data = await res.json();
      const reply = res.ok ? data.reply : data.detail || "No pude responder ahora.";
      typing.remove();
      addMsg(reply, "bot");
      history.push({ role: "assistant", content: reply });
      const mode = $("#chat-mode");
      if (mode && data.mode) mode.textContent = data.mode === "ai" ? "en línea · IA" : "en línea · modo básico";
    } catch {
      typing.remove();
      addMsg("Se cortó la conexión. Intenta de nuevo o escríbenos a contacto@nodosur.cl.", "bot");
    }
  };

  if (chat) {
    $$("[data-open-chat]").forEach((b) => b.addEventListener("click", () => openChat(b)));
    $$("[data-close-chat]").forEach((b) => b.addEventListener("click", closeChat));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !chat.hidden) closeChat();
    });
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const v = input.value;
      input.value = "";
      ask(v);
    });
    $$("[data-ask]").forEach((b) => b.addEventListener("click", () => ask(b.dataset.ask)));
  }
})();
