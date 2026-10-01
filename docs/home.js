/* The landing page's view of the arena: the round on now, the season so far and its kings. Read from the same two
   files as the live board (live/live.json and rounds/index.json); the full board is one click away. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const STAGE_TEXT = { window: "submissions open", seal: "sealing", images: "building tasks", evaluate: "evaluating",
                       close: "scoring", crown: "crowning", announce: "announcing", export: "exporting data",
                       publish_close: "publishing", done: "closed", waiting: "waiting for tasks", open: "opening" };
  const CROWN = '<svg class="crown-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8l4.6 3.8L12 5l4.4 6.8L21 8l-1.9 10.5H4.9z"/></svg>';
  let LIVE = null, ALL = null;

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const short = (h) => !h ? "" : h.length <= 14 ? h : h.slice(0, 6) + "…" + h.slice(-4);
  const pad = (n) => String(n).padStart(2, "0");
  const hms = (s) => { s = Math.max(0, Math.round(s)); return pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s % 3600 / 60)) + ":" + pad(s % 60); };
  const ago = (t) => { const s = Math.max(0, Date.now() / 1000 - t);
    return s < 60 ? "just now" : s < 3600 ? Math.round(s / 60) + " min ago" : s < 86400 ? Math.round(s / 3600) + " h ago" : Math.round(s / 86400) + " d ago"; };
  const rounds = () => (Array.isArray(ALL) && ALL.length ? ALL : (LIVE && LIVE.history) || []);

  // the same colours as the live board: one palette, in order of first appearance
  const PALETTE = ["#a78bfa", "#22d3ee", "#f472b6", "#a3e635", "#fb923c", "#60a5fa", "#2dd4bf", "#e879f9", "#38bdf8", "#818cf8", "#fda4af", "#bef264"];  // no yellow: gold is the crown
  const colours = {};
  function assignColours() {   // recomputed from scratch, so every page gives a miner the same colour once the index is in
    Object.keys(colours).forEach((k) => delete colours[k]);
    const order = [];
    rounds().forEach((r) => { if (r.king) order.push(r.king); Object.keys(r.crown || {}).sort().forEach((h) => order.push(h)); Object.keys(r.github || {}).sort().forEach((h) => order.push(h)); });
    if (LIVE) { Object.keys(LIVE.active || {}).sort().forEach((h) => order.push(h)); (LIVE.submissions || []).forEach((x) => order.push(x.hotkey)); }
    order.forEach((h) => { if (h && !(h in colours) && h !== "null" && h !== "canon") colours[h] = Object.keys(colours).length; });
  }
  const color = (h) => { const i = colours[h]; return i == null ? "#9c9bb4" : i < PALETTE.length ? PALETTE[i] : "hsl(" + ((i * 137.5) % 360).toFixed(0) + " 75% 65%)"; };
  const githubOf = (h) => {
    if (LIVE && LIVE.github && LIVE.github[h]) return LIVE.github[h];
    const rs = rounds();
    for (let i = rs.length - 1; i >= 0; i--) { const g = (rs[i].github || {})[h]; if (g) return g; }
    return null;
  };
  const nameOf = (h) => githubOf(h) ? "@" + githubOf(h) : short(h);
  function avatar(h, cls) {
    const g = githubOf(h), c = color(h);
    const initials = esc((g || h).replace(/^[^a-z0-9]+/i, "").slice(0, 2).toUpperCase());
    if (!g) return '<span class="' + cls + ' ph" style="--c:' + c + '">' + initials + "</span>";
    return '<img class="' + cls + '" style="--c:' + c + '" src="https://github.com/' + encodeURIComponent(g) + '.png?size=96" alt="" loading="lazy" referrerpolicy="no-referrer"' +
      " onerror=\"this.outerHTML='<span class=&quot;" + cls + " ph&quot; style=&quot;--c:" + c + "&quot;>" + initials + "</span>'\">";
  }

  function flaps(text) {
    const box = $("flaps");
    if (box.dataset.len !== String(text.length)) {
      box.innerHTML = [...text].map((ch) => ch === ":" ? '<span class="sep">:</span>' : '<span class="flap"></span>').join("");
      box.dataset.len = String(text.length);
    }
    [...box.children].forEach((el, i) => {
      if (el.classList.contains("sep") || el.textContent === text[i]) return;
      el.textContent = text[i];
      if (!REDUCED && box.dataset.ready) { el.classList.remove("flip"); void el.offsetWidth; el.classList.add("flip"); }
    });
    box.dataset.ready = "1";
  }

  function paintClock() {
    if (!LIVE) return;
    const st = LIVE.stage, w = LIVE.window, now = Date.now() / 1000, p = LIVE.progress || {};
    let label, text = "--:--:--", frac = 0, val = "—", mlabel;
    if (st === "window" && w) {
      label = w.closes_at > now ? "window closes in" : "closing…";
      text = hms(w.closes_at - now);
      frac = Math.min(1, Math.max(0, (now - w.opens_at) / w.seconds));
      const n = (LIVE.submissions || []).length;
      val = n + (n === 1 ? " entry" : " entries"); mlabel = "submission window";
    } else if (st === "done" || st === "waiting") {
      const last = rounds().slice(-1)[0];
      label = last ? "since the last close" : "waiting for the first round";
      text = last ? hms(now - last.closed_at) : text;
      frac = 1; val = last ? last.round_id + " closed" : "—"; mlabel = "round";
    } else {
      const ph = (s) => { const x = (LIVE.phases || []).find((q) => q.stage === s); return x ? x.t : null; };
      const t0 = ph("evaluate") || ph("images") || ph("seal");
      label = st === "evaluate" ? "evaluating for" : (STAGE_TEXT[st] || st) + " · round time";
      text = t0 ? hms(now - t0) : text;
      frac = p.total ? (p.done || 0) / p.total : 0;
      val = p.total ? (p.done || 0) + " / " + p.total + " episodes" : "—"; mlabel = "evaluation";
    }
    $("clock-label").textContent = label;
    $("meter-label").textContent = mlabel;
    flaps(text);
    $("meter").style.width = Math.round(100 * frac) + "%";
    $("meter-value").textContent = val;
  }

  function renderRound() {
    const L = LIVE, st = L.stage, rs = rounds(), active = L.active || {};
    $("round").textContent = L.round_id || "—";
    const crowned = !!(L.crown && L.crown.king);
    $("phase").className = "badge " + (st === "window" ? "window" : st === "done" || st === "waiting" ? (crowned ? "crowned" : "") : "evaluate");
    $("phase-txt").textContent = st === "done" && crowned ? "crowned" : STAGE_TEXT[st] || st;
    $("arena").classList.toggle("idle", st === "done" || st === "waiting");
    const stale = typeof L.updated === "number" && Date.now() / 1000 - L.updated > 900;
    document.body.classList.toggle("stale", stale);
    $("status").innerHTML = '<span class="pulse"></span>' + (stale ? "stale, " : "") + (typeof L.updated === "number" ? "updated " + ago(L.updated) : "");

    let king = crowned ? L.crown.king : null, how = "crowned this round";
    if (!king) { const inc = Object.keys(active).find((h) => active[h].incumbent); if (inc) { king = inc; how = "defending the crown"; } }
    if (!king) { for (let i = rs.length - 1; i >= 0; i--) if (rs[i].king) { king = rs[i].king; how = "reigning"; break; } }
    if (king) {
      const crowns = rs.filter((r) => r.king === king).length;
      $("king-av").innerHTML = avatar(king, "") + CROWN;
      $("king-name").textContent = nameOf(king);
      $("king-meta").textContent = how + " · " + crowns + (crowns === 1 ? " crown" : " crowns");
    }
    let field;
    if (st === "window") field = [...new Set((L.submissions || []).map((s) => s.hotkey))].filter((h) => h !== king);
    else { const sealed = Object.keys(active).filter((h) => h !== king && !active[h].incumbent); field = sealed.length ? sealed : Object.keys(active).filter((h) => h !== king); }
    $("field-count").innerHTML = field.length + "<small>" + (field.length === 1 ? "challenger" : "challengers") + "</small>";
    $("field-avs").innerHTML = field.slice(0, 12).map((h) => '<span title="' + esc(nameOf(h)) + '">' + avatar(h, "av") + "</span>").join("");
  }

  function countUp(el, to) {
    const from = Number(el.dataset.v || 0);
    el.dataset.v = String(to);
    if (REDUCED || from === to) { el.textContent = to.toLocaleString(); return; }
    const t0 = performance.now();
    const step = (t) => { const k = Math.min(1, (t - t0) / 1100), e = 1 - Math.pow(1 - k, 3);
      el.textContent = Math.round(from + (to - from) * e).toLocaleString(); if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }

  function renderSeason() {
    const rs = rounds(), crowns = {}, above = {}, miners = new Set();
    let changes = 0, prev = null, rows = 0;
    rs.forEach((r) => {
      Object.keys(r.github || {}).forEach((h) => miners.add(h));
      Object.keys(r.crown || {}).forEach((h) => { miners.add(h); above[h] = (above[h] || 0) + 1; });
      if (r.king) { crowns[r.king] = (crowns[r.king] || 0) + 1; miners.add(r.king); if (prev && prev !== r.king) changes++; prev = r.king; }
      rows += (r.sft_rows || 0) + (r.dpo_pairs || 0);
    });
    miners.delete("null"); miners.delete("canon");
    const kings = Object.keys(crowns).length;
    const cards = [[rs.length, "rounds closed"], [changes, "times the crown changed hands"], [kings, kings === 1 ? "king so far" : "different kings"],
                   [miners.size, "miners have competed"], [rows, "training rows published"]];
    const box = $("season");
    if (!box.children.length) box.innerHTML = cards.map(() => '<div class="num-card"><b>0</b><span></span></div>').join("");
    [...box.children].forEach((el, i) => { el.querySelector("span").textContent = cards[i][1]; countUp(el.querySelector("b"), cards[i][0]); });

    const pooled = (LIVE && LIVE.standings) || {};
    const top = Object.keys(crowns).sort((a, b) => crowns[b] - crowns[a] || (above[b] || 0) - (above[a] || 0)).slice(0, 3);
    $("podium").innerHTML = top.length ? top.map((h, i) => {
      const g = githubOf(h), w = (pooled[h] || {}).weight;
      return '<div class="pod p' + (i + 1) + '" style="--c:' + color(h) + '"><span class="pod-rk">' + (i + 1) + "</span>" +
        '<span class="pod-av">' + avatar(h, "") + (i === 0 ? CROWN : "") + "</span>" +
        '<span><span class="pod-name">' + (g ? '<a href="https://github.com/' + encodeURIComponent(g) + '">@' + esc(g) + "</a>" : esc(short(h))) + "</span>" +
        '<span class="pod-stats"><b>' + crowns[h] + "</b> " + (crowns[h] === 1 ? "crown" : "crowns") + "</span>" +
        '<span class="pod-sub">' + (above[h] || 0) + " rounds above the baseline" + (w != null ? ", " + Math.round(100 * w) + "% of today's weight" : "") + "</span></span></div>";
    }).join("") : '<p class="muted">No king yet: the first strategy to beat the baseline takes the crown.</p>';
  }

  let lastTimeline = "";
  function renderTimeline() {
    const rs = rounds(), crowns = {};
    rs.forEach((r) => { if (r.king) crowns[r.king] = (crowns[r.king] || 0) + 1; });
    const key = rs.map((r) => r.round_id + r.king).join();
    if (key === lastTimeline) return;
    lastTimeline = key;
    const dOf = (r) => r.king && r.crown && r.crown[r.king] ? r.crown[r.king].delta : null;
    const maxD = Math.max(0.05, ...rs.map((r) => dOf(r) || 0));
    let last = null;
    $("timeline").innerHTML = rs.map((r) => {
      const d = dOf(r), h = r.king ? Math.max(8, Math.round(130 * (d || 0) / maxD)) : 6;
      const cap = r.king && r.king !== last ? avatar(r.king, "cap") : "";
      if (r.king) last = r.king;
      const t = r.round_id + ": " + (r.king ? nameOf(r.king) + (d != null ? ", +" + Math.round(100 * d) + " pts over the baseline" : "") : "nobody beat the baseline");
      return '<a class="tl' + (r.king ? "" : " none") + '" href="rounds/' + esc(r.round_id) + '/" style="height:' + h + "px;--c:" + (r.king ? color(r.king) : "#2a2545") + '" title="' + esc(t) + '" aria-label="' + esc(t) + '">' + cap + "</a>";
    }).join("");
    $("tl-first").textContent = rs.length ? rs[0].round_id : "";
    $("tl-last").textContent = rs.length ? rs[rs.length - 1].round_id : "";
    $("legend").innerHTML = Object.keys(crowns).sort((a, b) => crowns[b] - crowns[a]).map((h) =>
      '<span style="--c:' + color(h) + '"><i></i><b>' + esc(nameOf(h)) + "</b> " + crowns[h] + "</span>").join("");
  }

  function render() {
    if (!LIVE) return;
    assignColours(); renderRound(); paintClock(); renderSeason(); renderTimeline();
  }
  async function tick() {
    try {
      const r = await fetch("live/live.json?t=" + Date.now(), { cache: "no-store" });
      if (!r.ok) return;
      LIVE = await r.json();
      render();
    } catch (e) { $("status").innerHTML = '<span class="pulse warn"></span>offline, retrying'; }
  }
  async function loadRounds() {
    try {
      const r = await fetch("rounds/index.json?t=" + Date.now(), { cache: "no-store" });
      const j = r.ok ? await r.json() : null;
      if (j && Array.isArray(j.rounds)) { ALL = j.rounds; render(); }
    } catch (e) { /* the last 20 rounds from live.json still fill the page */ }
  }
  tick().then(loadRounds);
  setInterval(tick, 15000);
  setInterval(loadRounds, 120000);
  setInterval(paintClock, 1000);
})();
