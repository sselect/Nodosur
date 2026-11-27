/* Panel NodoSur Jobs: dashboard en vivo (SSE), ofertas, configuración del agente y leads. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const fmtDate = (iso) => (iso ? new Date(iso + (iso.endsWith("Z") || iso.includes("+") ? "" : "Z")).toLocaleString("es-CL", { dateStyle: "short", timeStyle: "short" }) : "—");
  const STATUS = { new: "Nueva", saved: "Guardada", applied: "Postulada", discarded: "Descartada" };
  const LEAD_STATUS = { new: "Nuevo", contacted: "Contactado", proposal: "Propuesta", won: "Ganado", lost: "Perdido" };
  const css = getComputedStyle(document.documentElement);
  const C = { signal: css.getPropertyValue("--signal").trim(), teal: css.getPropertyValue("--teal").trim(), muted: css.getPropertyValue("--text-muted").trim(), line: css.getPropertyValue("--line").trim() };

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      ...opts,
      headers: { "Content-Type": "application/json", "X-NodoSur": "1", ...(opts.headers || {}) },
      credentials: "same-origin",
    });
    if (res.status === 401) { location.href = "/admin/login"; throw new Error("401"); }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Error " + res.status);
    return data;
  }

  /* ---------- Pestañas (con flechas del teclado) ---------- */
  const tabs = $$("[role=tab]");
  function selectTab(btn) {
    tabs.forEach((t) => {
      const on = t === btn;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      $("#" + t.getAttribute("aria-controls")).hidden = !on;
    });
    btn.focus();
    const name = btn.dataset.tab;
    if (name === "jobs") loadJobs();
    if (name === "agent") { loadConfig(); loadRuns(); }
    if (name === "leads") loadLeads();
  }
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => selectTab(t));
    t.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") selectTab(tabs[(i + 1) % tabs.length]);
      if (e.key === "ArrowLeft") selectTab(tabs[(i - 1 + tabs.length) % tabs.length]);
    });
  });

  /* ---------- Dashboard ---------- */
  const charts = {};
  function chart(id, type, labels, data, extra = {}) {
    if (!window.Chart) return;
    if (charts[id]) {
      charts[id].data.labels = labels;
      charts[id].data.datasets[0].data = data;
      charts[id].update();
      return;
    }
    Chart.defaults.color = C.muted;
    Chart.defaults.font.family = "Montserrat, system-ui, sans-serif";
    charts[id] = new Chart($("#" + id), {
      type,
      data: { labels, datasets: [{ data, borderWidth: type === "line" ? 2 : 0, borderColor: C.signal, backgroundColor: extra.colors || C.signal, tension: 0.35, fill: false, pointRadius: 3, borderRadius: 6 }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
        plugins: { legend: { display: type === "doughnut", position: "right" } },
        scales: type === "doughnut" ? {} : { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: C.line }, ticks: { precision: 0 } } },
        ...(extra.options || {}),
      },
    });
  }

  function bars(el, rows, label = (r) => r[0], value = (r) => r[1]) {
    const max = Math.max(1, ...rows.map(value));
    el.innerHTML = rows.length
      ? rows.map((r) => `<li><span>${esc(label(r))}</span><b class="mono">${value(r)}</b><span class="bar"><i style="width:${(value(r) / max) * 100}%"></i></span></li>`).join("")
      : '<li class="muted">Sin datos aún. Ejecuta el agente.</li>';
  }

  async function loadStats() {
    const s = await api("/admin/api/stats");
    $("#k-total").textContent = s.total.toLocaleString("es-CL");
    $("#k-24h").textContent = s.last_24h.toLocaleString("es-CL");
    $("#k-score").textContent = s.avg_score;
    $("#k-remote").textContent = s.total ? Math.round((s.remote / s.total) * 100) + "%" : "–";
    $("#k-next").textContent = !s.agent.active ? "Agente pausado" : s.agent.due ? "En la próxima señal del cron" : fmtDate(s.agent.next_run);
    chart("c-days", "line", s.by_day.map((d) => d.date.slice(5)), s.by_day.map((d) => d.count));
    const src = Object.entries(s.by_source);
    chart("c-sources", "doughnut", src.map((r) => r[0]), src.map((r) => r[1]), { colors: [C.signal, C.teal, "#7dd3fc", "#fbbf24", "#f472b6", "#a78bfa"] });
    chart("c-scores", "bar", Object.keys(s.score_buckets), Object.values(s.score_buckets), { colors: ["#2a3632", C.muted, C.teal, C.signal] });
    bars($("#kw-list"), s.top_keywords);
    const tbody = $("#sources-table tbody");
    tbody.innerHTML = s.sources.map((x) => `<tr><td>${esc(x.label)}${x.enabled ? "" : ' <span class="hint">(off)</span>'}</td><td><span class="st ${esc(x.last_status)}" title="${esc(x.last_error)}">${esc(x.last_status || "—")}</span></td><td>${fmtDate(x.last_fetch_at)}</td><td class="mono">${x.last_count}</td></tr>`).join("");
    const badge = $("#lead-badge");
    badge.hidden = !s.new_leads;
    badge.textContent = s.new_leads;
  }

  async function loadProspects() {
    const rows = await api("/admin/api/companies");
    bars($("#prospects"), rows, (r) => r.company, (r) => r.openings);
  }

  const feed = $("#feed");
  function feedItem(text, cls = "") {
    if (feed.firstElementChild && feed.firstElementChild.classList.contains("muted")) feed.innerHTML = "";
    const li = document.createElement("li");
    li.className = cls;
    li.innerHTML = `<span class="t">${new Date().toLocaleTimeString("es-CL")}</span>${text}`;
    feed.prepend(li);
    while (feed.children.length > 60) feed.lastElementChild.remove();
  }

  let refreshTimer = null;
  const refreshSoon = () => { clearTimeout(refreshTimer); refreshTimer = setTimeout(() => { loadStats(); loadProspects(); }, 800); };

  /* ---------- Tiempo real (SSE) ---------- */
  function connect() {
    const live = $("#live-state");
    const es = new EventSource("/admin/api/stream");
    es.onopen = () => { live.classList.add("on"); live.innerHTML = '<span class="live-dot"></span>en vivo'; };
    es.onerror = () => { live.classList.remove("on"); live.innerHTML = '<span class="live-dot"></span>reconectando…'; };
    es.addEventListener("run_started", (e) => feedItem(`▶ Agente iniciado (${esc(JSON.parse(e.data).data.trigger)})`));
    es.addEventListener("source_done", (e) => {
      const d = JSON.parse(e.data).data;
      feedItem(d.status === "ok" ? `✓ ${esc(d.source)}: ${d.fetched} avisos leídos` : `✗ ${esc(d.source)}: ${esc(d.error)}`, d.status === "ok" ? "" : "err");
    });
    es.addEventListener("job_new", (e) => {
      const j = JSON.parse(e.data).data;
      feedItem(`★ [${j.score}] <a href="${esc(j.url)}" target="_blank" rel="noopener">${esc(j.title)}</a> · ${esc(j.company || "—")}`, "new");
      refreshSoon();
    });
    es.addEventListener("run_finished", (e) => {
      const r = JSON.parse(e.data).data;
      feedItem(`■ Fin: ${r.new_jobs} nuevas de ${r.fetched} leídas · ${r.notified} avisadas por correo${r.message ? " · " + esc(r.message) : ""}`);
      runBtn.disabled = false;
      refreshSoon();
      if (!$("#tab-agent").hidden) loadRuns();
    });
    es.addEventListener("lead_new", (e) => {
      const l = JSON.parse(e.data).data;
      feedItem(`✉ Nuevo lead: ${esc(l.name)} · ${esc(l.service || l.kind)}`, "new");
      refreshSoon();
    });
  }

  const runBtn = $("#run-now");
  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    try { await api("/admin/api/run", { method: "POST" }); feedItem("▶ Ejecución manual solicitada"); }
    catch (err) { feedItem("✗ " + esc(err.message), "err"); runBtn.disabled = false; }
    setTimeout(() => { runBtn.disabled = false; }, 60000);
  });

  /* ---------- Ofertas ---------- */
  let page = 1;
  const filters = $("#filters");
  async function loadJobs() {
    const params = new URLSearchParams(new FormData(filters));
    params.set("page", page);
    const data = await api("/admin/api/jobs?" + params.toString());
    const tbody = $("#jobs-table tbody");
    tbody.innerHTML = data.items.length ? data.items.map((j) => {
      const cls = j.score >= 85 ? "s85" : j.score >= 70 ? "s70" : "";
      const kws = (j.matched_keywords || []).map((k) => `<span class="tag kw">${esc(k)}</span>`).join("");
      const tags = (j.tags || []).slice(0, 3).map((k) => `<span class="tag">${esc(k)}</span>`).join("");
      const opts = Object.entries(STATUS).map(([v, l]) => `<option value="${v}" ${v === j.status ? "selected" : ""}>${l}</option>`).join("");
      return `<tr><td><span class="score ${cls}">${j.score}</span></td>
        <td><a href="${esc(j.url)}" target="_blank" rel="noopener">${esc(j.title)}</a><span class="company">${esc(j.company || "—")}</span><div class="tags">${kws}${tags}</div></td>
        <td>${esc(j.location || "—")}<br><span class="hint">${esc(j.modality)}</span></td>
        <td>${esc(j.source)}<br><span class="hint">${fmtDate(j.collected_at)}</span></td>
        <td><label class="sr-only" for="st-${j.id}">Estado</label><select id="st-${j.id}" data-job="${j.id}">${opts}</select></td></tr>`;
    }).join("") : '<tr><td colspan="5" class="muted">No hay ofertas con estos filtros.</td></tr>';
    const pages = Math.max(1, Math.ceil(data.total / data.per_page));
    $("#page-info").textContent = `Página ${data.page} de ${pages} · ${data.total} ofertas`;
    $("#prev").disabled = page <= 1;
    $("#next").disabled = page >= pages;
  }
  filters.addEventListener("input", () => { page = 1; clearTimeout(filters._t); filters._t = setTimeout(loadJobs, 300); });
  filters.addEventListener("submit", (e) => e.preventDefault());
  $("#prev").addEventListener("click", () => { page = Math.max(1, page - 1); loadJobs(); });
  $("#next").addEventListener("click", () => { page += 1; loadJobs(); });
  $("#jobs-table").addEventListener("change", async (e) => {
    const sel = e.target.closest("select[data-job]");
    if (!sel) return;
    await api(`/admin/api/jobs/${sel.dataset.job}`, { method: "PATCH", body: JSON.stringify({ status: sel.value }) });
  });

  /* ---------- Configuración del agente ---------- */
  const cfgForm = $("#config-form");
  const list = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
  async function loadConfig() {
    const c = await api("/admin/api/config");
    cfgForm.active.checked = c.active;
    cfgForm.keywords.value = c.keywords.join(", ");
    cfgForm.exclude_keywords.value = c.exclude_keywords.join(", ");
    cfgForm.locations.value = c.locations.join(", ");
    $$("input[name=sources]", cfgForm).forEach((cb) => { cb.checked = c.sources.includes(cb.value); });
    ["interval_minutes", "min_score", "notify_min_score", "max_age_days", "notify_email"].forEach((k) => { cfgForm[k].value = c[k]; });
  }
  cfgForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = $(".form-status", cfgForm);
    status.className = "form-status";
    const body = {
      active: cfgForm.active.checked,
      keywords: list(cfgForm.keywords.value),
      exclude_keywords: list(cfgForm.exclude_keywords.value),
      locations: list(cfgForm.locations.value),
      sources: $$("input[name=sources]:checked", cfgForm).map((cb) => cb.value),
      interval_minutes: Number(cfgForm.interval_minutes.value),
      min_score: Number(cfgForm.min_score.value),
      notify_min_score: Number(cfgForm.notify_min_score.value),
      max_age_days: Number(cfgForm.max_age_days.value),
      notify_email: cfgForm.notify_email.value.trim(),
    };
    try {
      await api("/admin/api/config", { method: "PUT", body: JSON.stringify(body) });
      status.textContent = "Configuración guardada. Se aplica en la próxima ejecución.";
      status.classList.add("ok");
      loadStats();
    } catch (err) {
      status.textContent = "No se pudo guardar: " + err.message;
      status.classList.add("err");
    }
  });

  async function loadRuns() {
    const rows = await api("/admin/api/runs");
    $("#runs-table tbody").innerHTML = rows.length ? rows.map((r) => `<tr><td>${fmtDate(r.started_at)}</td><td>${esc(r.trigger)}</td><td><span class="st ${esc(r.status)}" title="${esc(r.message)}">${esc(r.status)}</span></td><td class="mono">${r.fetched}</td><td class="mono">${r.new_jobs}</td><td class="mono">${r.notified}</td></tr>`).join("") : '<tr><td colspan="6" class="muted">Aún no hay ejecuciones.</td></tr>';
  }

  /* ---------- Leads ---------- */
  async function loadLeads() {
    const rows = await api("/admin/api/leads");
    $("#leads-table tbody").innerHTML = rows.length ? rows.map((l) => {
      const opts = Object.entries(LEAD_STATUS).map(([v, t]) => `<option value="${v}" ${v === l.status ? "selected" : ""}>${t}</option>`).join("");
      return `<tr><td>${fmtDate(l.created_at)}</td><td><b>${esc(l.name)}</b><br><a href="mailto:${esc(l.email)}">${esc(l.email)}</a><br><span class="hint">${esc(l.company)} ${esc(l.phone)}</span></td><td>${esc(l.service || l.kind)}</td><td>${esc(l.message)}</td><td><label class="sr-only" for="ld-${l.id}">Estado</label><select id="ld-${l.id}" data-lead="${l.id}">${opts}</select></td></tr>`;
    }).join("") : '<tr><td colspan="5" class="muted">Todavía no llegan leads. Comparte la landing.</td></tr>';
  }
  $("#leads-table").addEventListener("change", async (e) => {
    const sel = e.target.closest("select[data-lead]");
    if (!sel) return;
    await api(`/admin/api/leads/${sel.dataset.lead}`, { method: "PATCH", body: JSON.stringify({ status: sel.value }) });
    loadStats();
  });

  /* ---------- Inicio ---------- */
  const start = () => { loadStats(); loadProspects(); connect(); };
  if (window.Chart) start(); else window.addEventListener("load", start);
  setInterval(loadStats, 60000);
})();
