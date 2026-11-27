/* NodoSur landing: escenas con GSAP + ScrollTrigger, apariciones con AOS, menú, formulario y chat. */
(() => {
  "use strict";
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const root = document.documentElement;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hasGsap = Boolean(window.gsap && window.ScrollTrigger);

  /* ---------- Menú móvil ---------- */
  const toggle = $(".nav-toggle");
  const menu = $("#mobile-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });
    $$("a", menu).forEach((a) =>
      a.addEventListener("click", () => {
        menu.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      })
    );
  }

  /* ---------- Apariciones fade-up (AOS) ---------- */
  if (window.AOS) {
    window.AOS.init({ duration: 800, easing: "ease-out-cubic", once: true, offset: 60, disable: reduce });
    if (!reduce) root.classList.add("aos-ready");
  }

  /* ---------- Matriz de puntos (escena "señales") ---------- */
  function SignalField(canvas) {
    const ctx = canvas.getContext("2d");
    const GAP = 16;
    let w = 0, h = 0, dots = [];
    // generador determinista: la escena se dibuja igual en cada visita
    const rand = (seed) => () => {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const r = rand(42);
      const centers = Array.from({ length: 9 }, () => ({ x: r() * w, y: r() * h, s: 60 + r() * 120, t: 0.15 + r() * 0.5 }));
      dots = [];
      for (let y = GAP / 2; y < h; y += GAP) {
        for (let x = GAP / 2; x < w; x += GAP) {
          let lit = 2;
          for (const c of centers) {
            const d = Math.hypot(x - c.x, y - c.y);
            if (d < c.s) lit = Math.min(lit, c.t + (d / c.s) * 0.25 + r() * 0.05);
          }
          dots.push({ x, y, lit, fix: lit + 0.12 + r() * 0.25 });
        }
      }
    };
    const draw = (p) => {
      ctx.clearRect(0, 0, w, h);
      for (const d of dots) {
        if (p >= d.lit) {
          ctx.fillStyle = p >= d.fix ? "rgba(200,242,92,0.95)" : "rgba(251,191,36,0.95)";
          ctx.fillRect(d.x - 2, d.y - 2, 4, 4);
        } else {
          ctx.fillStyle = "rgba(120,140,132,0.18)";
          ctx.fillRect(d.x - 1, d.y - 1, 2, 2);
        }
      }
    };
    resize();
    return { resize, draw };
  }

  const canvas = $(".signals__canvas");
  const field = canvas ? SignalField(canvas) : null;
  let fieldP = reduce ? 1 : 0.6;
  if (field) {
    field.draw(fieldP);
    window.addEventListener("resize", () => {
      field.resize();
      field.draw(fieldP);
    });
  }


  /* ---------- Globo de nodos del hero: la red NodoSur emerge con borde de luz ---------- */
  function NodeGlobe(canvas) {
    const ctx = canvas.getContext("2d");
    const N = window.innerWidth < 861 ? 300 : 460; // menos puntos en pantallas chicas
    const golden = Math.PI * (3 - Math.sqrt(5));
    const pts = [];
    for (let i = 0; i < N; i++) {
      const y = 1 - (i / (N - 1)) * 2;
      const r = Math.sqrt(1 - y * y);
      pts.push({ x: Math.cos(golden * i) * r, y, z: Math.sin(golden * i) * r, hot: i % 11 === 0 });
    }
    // dos vecinos más cercanos por punto, sin ordenar listas (barato también en celulares)
    const links = [];
    for (let i = 0; i < N; i++) {
      let d1 = Infinity, d2 = Infinity, j1 = -1, j2 = -1;
      const a = pts[i];
      for (let j = 0; j < N; j++) {
        if (j === i) continue;
        const b = pts[j];
        const d = (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2;
        if (d < d1) { d2 = d1; j2 = j1; d1 = d; j1 = j; } else if (d < d2) { d2 = d; j2 = j; }
      }
      if (i < j1) links.push([i, j1]);
      if (i < j2) links.push([i, j2]);
    }
    let w = 0, h = 0;
    const clamp = (v) => Math.min(1, Math.max(0, v));
    const easeOut = (v) => 1 - (1 - v) ** 3;
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const draw = (p, t) => {
      ctx.clearRect(0, 0, w, h);
      const emerge = easeOut(clamp(p / 0.42));
      const recede = clamp((p - 0.42) / 0.3);
      const minDim = Math.min(w, h);
      const R = minDim * (0.36 + 0.06 * emerge) * (1 - 0.28 * recede);
      const cx = w / 2;
      const cy = h * (1.14 - 0.6 * emerge) - h * 0.02 * recede;
      const alpha = (0.5 + 0.5 * emerge) * (1 - 0.72 * recede);
      const rot = p * Math.PI * 1.8 + t * 0.06;
      const tilt = -0.42 + 0.22 * emerge;
      const cr = Math.cos(rot), sr = Math.sin(rot), ct = Math.cos(tilt), st = Math.sin(tilt);
      const D = 3.2;
      const proj = pts.map((q) => {
        const x = q.x * cr + q.z * sr;
        const z = -q.x * sr + q.z * cr;
        const y2 = q.y * ct - z * st;
        const z2 = q.y * st + z * ct;
        const k = D / (D - z2);
        return { x: cx + x * R * k, y: cy + y2 * R * k, z: z2, k, hot: q.hot };
      });
      ctx.lineWidth = 1;
      for (const [i, j] of links) {
        const a = proj[i], b = proj[j];
        const front = ((a.z + b.z) / 2 + 1) / 2;
        ctx.strokeStyle = `rgba(150,185,170,${alpha * (0.05 + 0.25 * front)})`;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
      for (const q of proj) {
        const front = (q.z + 1) / 2;
        if (q.hot) {
          const pulse = 0.55 + 0.45 * Math.sin(t * 2.2 + q.x * 0.02);
          ctx.fillStyle = `rgba(200,242,92,${alpha * (0.3 + 0.7 * front) * pulse})`;
          ctx.beginPath();
          ctx.arc(q.x, q.y, 2.6 * q.k, 0, Math.PI * 2);
          ctx.fill();
        } else {
          ctx.fillStyle = `rgba(225,238,232,${alpha * (0.12 + 0.62 * front)})`;
          ctx.fillRect(q.x - q.k, q.y - q.k, 2 * q.k, 2 * q.k);
        }
      }
      // borde de luz sobre el contorno superior (como el producto iluminado de la referencia):
      // trazo fino que se desvanece hacia los extremos, con halo; degradado cónico = pocas operaciones
      const a0 = Math.PI * 1.02, a1 = Math.PI * 1.98;
      const rimPaint = (rgb, peak) => {
        if (!ctx.createConicGradient) return `rgba(${rgb},${peak * 0.6})`;
        const g = ctx.createConicGradient(a0, cx, cy);
        const span = (a1 - a0) / (Math.PI * 2);
        for (let k = 0; k <= 8; k++) {
          const u = k / 8;
          g.addColorStop(u * span, `rgba(${rgb},${peak * Math.sin(Math.PI * u) ** 2})`);
        }
        g.addColorStop(Math.min(1, span + 0.001), `rgba(${rgb},0)`);
        return g;
      };
      ctx.save();
      ctx.lineCap = "round";
      for (const [width, rgb, peak] of [[14, "200,242,92", 0.1 * alpha], [6, "200,242,92", 0.28 * alpha], [2.4, "240,255,200", 0.95 * alpha]]) {
        ctx.beginPath();
        ctx.arc(cx, cy, R * 1.03, a0, a1);
        ctx.strokeStyle = rimPaint(rgb, peak);
        ctx.lineWidth = width;
        ctx.stroke();
      }
      ctx.restore();
    };
    resize();
    return { resize, draw };
  }

  const globeCanvas = $(".hero__globe");
  const globe = globeCanvas ? NodeGlobe(globeCanvas) : null;
  let heroP = 0;
  let globeT = 0;
  let globeVisible = true;
  let globeIdleP = null; // en celular o movimiento reducido el globo queda en una pose fija
  if (globe) {
    const frame = (now) => {
      globeT = now / 1000;
      if (globeVisible) globe.draw(globeIdleP ?? heroP, reduce ? 0 : globeT);
      if (!reduce) requestAnimationFrame(frame);
    };
    const start = () => requestAnimationFrame(frame);
    if ("requestIdleCallback" in window) requestIdleCallback(start, { timeout: 800 });
    else setTimeout(start, 200);
    window.addEventListener("resize", () => {
      globe.resize();
      globe.draw(globeIdleP ?? heroP, globeT);
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => (globeVisible = e.isIntersecting)).observe(globeCanvas);
    }
  }

  /* ---------- Estados que dependen del progreso ---------- */
  const heroLines = $$(".hero .console-log li");
  const modes = $$(".mode");
  const track = $(".modes__track");
  const count = $(".modes__count b");
  const dots = $$(".modes__dots li");
  const iaSteps = $$(".ia-steps li");
  const iaNodes = $$(".ia-visual .node");
  const iaWires = $$(".ia-visual .wire");
  const appSteps = $$(".app-steps li");
  const appViews = $$(".window .view");

  let modeIndex = -1;
  const setMode = (i) => {
    if (i === modeIndex) return;
    modeIndex = i;
    if (track) track.style.transform = `translate3d(${-i * 100}%, 0, 0)`;
    modes.forEach((m, k) => m.classList.toggle("active", k === i));
    dots.forEach((d, k) => d.classList.toggle("on", k === i));
    if (count) count.textContent = String(i + 1).padStart(2, "0");
  };
  const setIa = (i) => {
    iaSteps.forEach((li, k) => li.classList.toggle("active", k === i));
    iaNodes.forEach((n, k) => n.classList.toggle("lit", k <= i));
    iaWires.forEach((wire, k) => wire.classList.toggle("lit", k < i));
  };
  const setApp = (i) => {
    appSteps.forEach((li, k) => li.classList.toggle("active", k === i));
    appViews.forEach((v, k) => v.classList.toggle("active", k === i));
  };
  const showAll = () => {
    heroLines.forEach((li) => li.classList.add("on"));
    modes.forEach((m) => m.classList.add("active"));
    iaSteps.forEach((li) => li.classList.add("active"));
    iaNodes.forEach((n) => n.classList.add("lit"));
    appSteps.forEach((li) => li.classList.add("active"));
    appViews.forEach((v) => v.classList.add("active"));
  };

  /* ---------- Escenas con GSAP + ScrollTrigger ---------- */
  if (!hasGsap) {
    root.classList.remove("js"); // sin librerías: todo visible y estático
    showAll();
    globeIdleP = 0.42;
  } else {
    const { gsap, ScrollTrigger, SplitText, Lenis } = window;
    gsap.registerPlugin(ScrollTrigger);

    // En celular el hero se muestra al tiro (mejor LCP); las animaciones de entrada quedan para el resto
    const narrow = window.matchMedia("(max-width: 860px)").matches;
    const animated = (el) => !(narrow && el.closest(".hero"));

    // Cede el hilo principal entre pasos: en celulares ninguna tarea larga bloquea el primer toque (TBT)
    const yieldToMain = () => new Promise((resolve) => setTimeout(resolve, 0));
    const useSplit = Boolean(SplitText) && !reduce;
    if (useSplit) gsap.registerPlugin(SplitText);

    // Titulares que se revelan línea por línea (SplitText con máscara)
    const splitOne = (el) =>
      SplitText.create(el, {
        type: "lines",
        mask: "lines",
        linesClass: "split-line",
        autoSplit: true,
        onSplit(self) {
          gsap.set(el, { visibility: "visible" });
          return gsap.from(self.lines, {
            yPercent: 110,
            duration: 1.1,
            ease: "power4.out",
            stagger: 0.1,
            scrollTrigger: el.classList.contains("split--load") ? undefined : { trigger: el, start: "top 88%", once: true },
          });
        },
      });

    const scenes = () => {
      const mm = gsap.matchMedia();

      mm.add("(min-width: 861px) and (prefers-reduced-motion: no-preference)", () => {
        // Scroll suave (Lenis) sincronizado con ScrollTrigger
        let lenis = null;
        let tick = null;
        if (Lenis) {
          lenis = new Lenis({ lerp: 0.12, anchors: { offset: -56 } });
          lenis.on("scroll", ScrollTrigger.update);
          tick = (time) => lenis.raf(time * 1000);
          gsap.ticker.add(tick);
          gsap.ticker.lagSmoothing(0);
        }
        const scrollToY = (y) => (lenis ? lenis.scrollTo(y, { duration: 1.4 }) : window.scrollTo({ top: y, behavior: "smooth" }));
        globeIdleP = null;

        // 1 · Hero: el globo emerge y gira, el texto sube y se va, luego la consola pasa al frente
        const hero = $(".hero");
        gsap.timeline({
          scrollTrigger: {
            trigger: hero,
            start: "top top",
            end: "bottom bottom",
            scrub: 0.6,
            onUpdate: (st) => {
              heroP = st.progress;
              const lit = Math.floor(Math.max(0, (st.progress - 0.6) / 0.28) * (heroLines.length + 1));
              heroLines.forEach((li, i) => li.classList.toggle("on", i < lit));
              hero.classList.toggle("copy-off", st.progress > 0.3);
            },
          },
        })
          .to(".hero__copy", { y: -160, opacity: 0, ease: "none", duration: 0.28 }, 0.06)
          .to(".hero__bg", { y: -200, ease: "none", duration: 1 }, 0)
          .fromTo(".ops-console", { y: "60vh", scale: 0.8, rotateX: 30, opacity: 0 }, { y: 0, scale: 1, rotateX: 0, opacity: 1, ease: "none", duration: 0.34 }, 0.44)
          .fromTo(".hero__caption", { opacity: 0, y: 40 }, { opacity: 1, y: 0, ease: "none", duration: 0.12 }, 0.84)
          .to({}, { duration: 0.04 });

        // 3 · Señales: el titular entra (0,85 → 1), se queda y luego "atraviesa" (1 → 1,09 y se desvanece)
        if (field) {
          gsap.timeline({
            scrollTrigger: {
              trigger: ".signals",
              start: "top top",
              end: "bottom bottom",
              scrub: 0.5,
              onUpdate: (st) => {
                fieldP = st.progress;
                field.draw(fieldP);
              },
            },
          })
            .fromTo(".signals__copy", { scale: 0.85, opacity: 0, y: 60 }, { scale: 1, opacity: 1, y: 0, ease: "none", duration: 0.25 })
            .to(".signals__copy", { duration: 0.35 })
            .to(".signals__copy", { scale: 1.09, opacity: 0.13, ease: "none", duration: 0.3 });
        }

        // 4 · Servicios: carrusel horizontal que avanza un paso (800 ms) por tramo de scroll
        const n = modes.length;
        const modesST = ScrollTrigger.create({
          trigger: ".modes__scroll",
          start: "top top",
          end: "bottom bottom",
          onUpdate: (st) => setMode(Math.min(n - 1, Math.floor(st.progress * n))),
        });
        setMode(0);
        $$("[data-slide]").forEach((a) => {
          a.onclick = (e) => {
            e.preventDefault();
            const i = Number(a.dataset.slide);
            scrollToY(modesST.start + ((i + 0.5) / n) * (modesST.end - modesST.start));
          };
        });

        // 5 · Antes y después: el panel "con NodoSur" se abre de 85 % a 50 % y aparecen las etiquetas
        gsap.timeline({ scrollTrigger: { trigger: ".compare", start: "top top", end: "bottom bottom", scrub: 0.5 } })
          .fromTo(".compare", { "--w": "85%" }, { "--w": "50%", ease: "none", duration: 0.7 }, 0.05)
          .fromTo(".compare .ticket-pile", { y: -40 }, { y: 0, ease: "none", duration: 0.7 }, 0.05)
          .fromTo(".compare .chip", { opacity: 0, y: 40 }, { opacity: 1, y: 0, ease: "none", duration: 0.2, stagger: 0.05 }, 0.7);

        // 6 · IA: un paso por tramo
        ScrollTrigger.create({
          trigger: ".ia-scene",
          start: "top top",
          end: "bottom bottom",
          onUpdate: (st) => setIa(Math.min(iaSteps.length - 1, Math.floor(st.progress * iaSteps.length))),
        });
        setIa(0);

        // 7 · ERP: la ventana cambia de vista
        ScrollTrigger.create({
          trigger: ".app-window",
          start: "top top",
          end: "bottom bottom",
          onUpdate: (st) => setApp(Math.min(appViews.length - 1, Math.floor(st.progress * appViews.length))),
        });
        setApp(0);

        return () => {
          $$("[data-slide]").forEach((a) => (a.onclick = null));
          modeIndex = -1;
          if (tick) gsap.ticker.remove(tick);
          if (lenis) lenis.destroy();
        };
      });

      // Celular, tablet o movimiento reducido: sin escenas fijadas, todo visible
      mm.add("(max-width: 860px), (prefers-reduced-motion: reduce)", () => {
        showAll();
        globeIdleP = 0.42;
        if (field) field.draw((fieldP = reduce ? 1 : 0.6));
        $$("[data-slide]").forEach((a) => {
          a.onclick = (e) => {
            const target = modes[Number(a.dataset.slide)];
            if (target) {
              e.preventDefault();
              target.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
            }
          };
        });
        if (!reduce && field) {
          ScrollTrigger.create({
            trigger: ".signals",
            start: "top bottom",
            end: "bottom top",
            onUpdate: (st) => field.draw((fieldP = st.progress)),
          });
        }
      });
    };

    (async () => {
      const splits = useSplit ? $$(".split").filter(animated) : [];
      if (!useSplit) $$(".split").forEach((el) => (el.style.visibility = "visible"));
      splits.filter((el) => el.classList.contains("split--load")).forEach(splitOne); // lo visible al cargar, primero
      await yieldToMain();
      scenes();
      await yieldToMain();
      // Fade-in-up de titulares (80 px, como el efecto de la referencia)
      if (!reduce) {
        ScrollTrigger.batch($$(".sfx").filter(animated), {
          start: "top 90%",
          once: true,
          onEnter: (els) => gsap.to(els, { opacity: 1, y: 0, duration: 1, ease: "power3.out", stagger: 0.12, overwrite: true }),
        });
      }
      for (const el of splits.filter((e) => !e.classList.contains("split--load"))) {
        await yieldToMain();
        splitOne(el);
      }
      if (document.readyState === "complete") ScrollTrigger.refresh();
    })();

    window.addEventListener("load", () => ScrollTrigger.refresh());
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
