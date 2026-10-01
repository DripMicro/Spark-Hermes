/* The live arena. Everything here is computed in the browser from two files the validator publishes:
   live.json (the round on now, rewritten at every stage and every few minutes) and ../rounds/index.json (every
   closed round, rewritten at each close). Nothing is trusted that a reader could not recompute from those. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ROUND_ID = /^[a-z]\d{1,4}$/;
  const LABEL = { open: "open", window: "window", seal: "seal", images: "images", evaluate: "evaluate", close: "score",
                  crown: "crown", announce: "verdict", export: "export", publish_close: "publish", done: "done" };
  const STAGE_TEXT = { window: "submissions open", seal: "sealing", images: "building tasks", evaluate: "evaluating",
                       close: "scoring", crown: "crowning", announce: "announcing", export: "exporting data",
                       publish_close: "publishing", done: "closed", waiting: "waiting for tasks", open: "opening" };

  let LIVE = null, ALL = null, indexTried = false, deepLinked = false, lastFocus = null;
  let openLane = null;                 // the one lane whose per-task detail is open
  let prevPos = {}, moved = {};        // tower positions on the last render, and recent moves
  let seen = null;                     // what the feed has already reported (null until the first render)
  const feed = [];                     // newest first

  // ─── small helpers ─────────────────────────────────────────────────────────────────────────────────────
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const short = (h) => !h ? "" : h.length <= 14 ? h : h.slice(0, 6) + "…" + h.slice(-4);
  const pad = (n) => String(n).padStart(2, "0");
  const hms = (s) => { s = Math.max(0, Math.round(s)); return pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s % 3600 / 60)) + ":" + pad(s % 60); };
  const hhmm = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const when = (t) => new Date(t * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  const ago = (t) => { const s = Math.max(0, Date.now() / 1000 - t);
    return s < 60 ? "just now" : s < 3600 ? Math.round(s / 60) + " min ago" : s < 86400 ? Math.round(s / 3600) + " h ago" : Math.round(s / 86400) + " d ago"; };
  const num = (x, d) => x == null || isNaN(x) ? "—" : Number(x).toFixed(d);
  const pts = (d) => d == null ? "—" : (d > 0 ? "+" : d < 0 ? "−" : "±") + Math.abs(Math.round(100 * d));
  const signed = (x, d) => x == null ? "—" : (x > 0 ? "+" : "") + Number(x).toFixed(d);
  const iso = (s) => s ? Date.parse(s) / 1000 : null;
  const repo = () => (LIVE && LIVE.repo) || "gittensor-model-hub/Spark-Hermes";
  const branch = () => (LIVE && LIVE.branch) || "main";
  const prLink = (n) => '<a href="https://github.com/' + esc(repo()) + "/pull/" + Number(n) + '">#' + Number(n) + "</a>";

  // every miner keeps one colour across the page: its lane, its bars in the crown history, its legend swatch. Colours
  // come from one palette in order of first appearance, so they stay put as rounds close and newcomers get their own.
  const PALETTE = ["#a78bfa", "#22d3ee", "#f472b6", "#a3e635", "#fb923c", "#60a5fa", "#2dd4bf", "#e879f9", "#38bdf8", "#818cf8", "#fda4af", "#bef264"];  // no yellow: gold is the crown
  const colours = {};
  function assignColours() {   // recomputed from scratch, so every page gives a miner the same colour once the index is in
    Object.keys(colours).forEach((k) => delete colours[k]);
    const order = [];
    closedRounds().forEach((r) => { if (r.king) order.push(r.king); Object.keys(r.crown || {}).sort().forEach((h) => order.push(h)); Object.keys(r.github || {}).sort().forEach((h) => order.push(h)); });
    if (LIVE) { Object.keys(LIVE.active || {}).sort().forEach((h) => order.push(h)); (LIVE.submissions || []).forEach((x) => order.push(x.hotkey)); }
    order.forEach((h) => { if (h && !(h in colours) && h !== "null" && h !== "canon") colours[h] = Object.keys(colours).length; });
  }
  function color(h) {
    if (h === "null") return "#d9d4f2";
    if (h === "canon") return "#8b8aa6";
    const i = colours[h];
    if (i == null) return "#9c9bb4";
    return i < PALETTE.length ? PALETTE[i] : "hsl(" + ((i * 137.5) % 360).toFixed(0) + " 75% 65%)";  // past the palette: golden-angle hues
  }
  const githubOf = (h) => {
    if (LIVE && LIVE.github && LIVE.github[h]) return LIVE.github[h];
    const rs = closedRounds();
    for (let i = rs.length - 1; i >= 0; i--) { const g = (rs[i].github || {})[h]; if (g) return g; }
    return null;
  };
  const nameOf = (h) => h === "null" ? "baseline" : h === "canon" ? "canon" : githubOf(h) ? "@" + githubOf(h) : short(h);
  function avatar(h, cls) {
    const g = githubOf(h), c = color(h);
    if (h === "null" || h === "canon") return '<span class="' + cls + ' ph ref-glyph" style="--c:' + c + '" title="' + (h === "null" ? "no strategy" : "reference strategy") + '">' + (h === "null" ? "∅" : "◆") + "</span>";
    const initials = esc((githubOf(h) || h).replace(/^[^a-z0-9]+/i, "").slice(0, 2).toUpperCase());
    if (!g) return '<span class="' + cls + ' ph" style="--c:' + c + '">' + initials + "</span>";
    return '<img class="' + cls + '" style="--c:' + c + '" src="https://github.com/' + encodeURIComponent(g) + '.png?size=96" alt="" loading="lazy" referrerpolicy="no-referrer"' +
      " onerror=\"this.outerHTML='<span class=&quot;" + cls + " ph&quot; style=&quot;--c:" + c + "&quot;>" + initials + "</span>'\">";
  }
  const CROWN = '<svg class="crown-ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8l4.6 3.8L12 5l4.4 6.8L21 8l-1.9 10.5H4.9z"/></svg>';
  const closedRounds = () => (Array.isArray(ALL) && ALL.length ? ALL : (LIVE && LIVE.history) || []);

  // ─── the split-flap clock ───────────────────────────────────────────────────────────────────────────────
  function flaps(text) {
    const box = $("flaps");
    if (box.dataset.len !== String(text.length)) {
      box.innerHTML = [...text].map((ch) => ch === ":" ? '<span class="sep">:</span>' : '<span class="flap"></span>').join("");
      box.dataset.len = String(text.length);
    }
    [...box.children].forEach((el, i) => {
      if (el.classList.contains("sep")) return;
      const ch = text[i];
      if (el.textContent !== ch) {
        el.textContent = ch;
        if (!REDUCED && box.dataset.ready) { el.classList.remove("flip"); void el.offsetWidth; el.classList.add("flip"); }
      }
    });
    box.dataset.ready = "1";
  }

  // ─── the round on now ──────────────────────────────────────────────────────────────────────────────────
  const phaseTime = (stage) => { const p = ((LIVE && LIVE.phases) || []).find((x) => x.stage === stage); return p ? p.t : null; };
  function evalStart() { return phaseTime("evaluate") || phaseTime("images") || phaseTime("seal") || null; }

  function paintClock() {
    if (!LIVE) return;
    const st = LIVE.stage, w = LIVE.window, now = Date.now() / 1000, p = LIVE.progress || {};
    let label = "", text = "--:--:--", frac = 0, val = "—", note = "", note2 = "";
    if (st === "window" && w) {
      label = w.closes_at > now ? "window closes in" : "closing…";
      text = hms(w.closes_at - now);
      frac = Math.min(1, Math.max(0, (now - w.opens_at) / w.seconds));
      const n = (LIVE.submissions || []).length;
      val = n + (n === 1 ? " entry" : " entries");
      note = "opened " + hhmm(w.opens_at) + (w.reopened ? " · window " + (w.reopened + 1) : "");
      note2 = "closes " + hhmm(w.closes_at);
      $("meter-label").textContent = "submission window";
    } else if (st === "done" || st === "waiting") {
      const last = closedRounds().slice(-1)[0];
      label = last ? "since the last close" : "waiting for the first round";
      text = last ? hms(now - last.closed_at) : "--:--:--";
      frac = 1; val = last ? "round " + last.round_id + " closed" : "—";
      $("meter-label").textContent = "round";
    } else {
      const t0 = evalStart();
      label = st === "evaluate" ? "evaluating for" : (STAGE_TEXT[st] || st) + " · round time";
      text = t0 ? hms(now - t0) : "--:--:--";
      const done = p.done || 0, total = p.total || 0;
      frac = total ? done / total : 0;
      val = total ? done + " / " + total + " episodes" : "—";
      if (t0 && done >= 2 && total > done && st === "evaluate") {
        const left = (now - t0) / done * (total - done);
        note = "about " + Math.max(1, Math.round(left / 60)) + " min to go";
      } else if (total && done >= total) note = "all episodes in";
      note2 = w ? "window closed " + hhmm(w.closes_at) : "";
      $("meter-label").textContent = "evaluation";
    }
    $("clock-label").textContent = label;
    flaps(text);
    $("meter").style.width = Math.round(100 * frac) + "%";
    $("meter-value").textContent = val;
    $("meter-note").textContent = note;
    $("meter-note-2").textContent = note2;
  }

  function renderHero() {
    const L = LIVE, st = L.stage;
    $("round").textContent = L.round_id || "—";
    const crowned = !!(L.crown && L.crown.king);
    const cls = st === "window" ? "window" : st === "done" || st === "waiting" ? (crowned ? "crowned" : "") : "evaluate";
    $("phase").className = "badge " + cls;
    $("phase-txt").textContent = st === "done" && crowned ? "crowned" : STAGE_TEXT[st] || st;
    $("arena").classList.toggle("idle", st === "done" || st === "waiting");
    const stale = typeof L.updated === "number" && Date.now() / 1000 - L.updated > 900;
    document.body.classList.toggle("stale", stale);
    $("status").innerHTML = '<span class="pulse"></span>' + (stale ? "stale, " : "live, ") + (typeof L.updated === "number" ? "updated " + ago(L.updated) : "");

    // the stage track
    const stages = (Array.isArray(L.stages) && L.stages.length > 1 ? L.stages : Object.keys(LABEL)).filter((s) => LABEL[s]);
    const reached = new Set((L.phases || []).map((p) => p.stage));
    const nowIdx = stages.indexOf(st);
    $("track").innerHTML = stages.map((s, i) => {
      const t = phaseTime(s);
      const state = s === st ? "now" : reached.has(s) || (nowIdx >= 0 && i < nowIdx) || st === "done" ? "done" : "";
      return '<div class="st ' + state + '"><b>' + esc(LABEL[s]) + "</b>" + (t ? hhmm(t) : "&nbsp;") + "</div>";
    }).join("");
    const cur = $("track").querySelector(".st.now");   // on a narrow screen, keep the current stage in view
    if (cur && $("track").scrollWidth > $("track").clientWidth) $("track").scrollLeft = Math.max(0, cur.offsetLeft - $("track").offsetLeft - 40);

    // the king and the field
    const rounds = closedRounds();
    const active = L.active || {};
    let king = L.crown && L.crown.king ? L.crown.king : null, how = "crowned this round";
    if (!king) { const inc = Object.keys(active).find((h) => active[h].incumbent); if (inc) { king = inc; how = "defending the crown"; } }
    if (!king) { for (let i = rounds.length - 1; i >= 0; i--) if (rounds[i].king) { king = rounds[i].king; how = "reigning"; break; } }
    const crowns = {}; rounds.forEach((r) => { if (r.king) crowns[r.king] = (crowns[r.king] || 0) + 1; });
    let streak = 0;
    for (let i = rounds.length - 1; i >= 0; i--) { if (rounds[i].king === king) streak++; else if (rounds[i].king) break; }
    if (king) {
      const g = githubOf(king);
      $("king-av").innerHTML = avatar(king, "") + CROWN;
      $("king-name").innerHTML = g ? '<a href="https://github.com/' + encodeURIComponent(g) + '">@' + esc(g) + "</a>" : esc(short(king));
      const a = active[king];
      const defense = a && a.incumbent ? (a.pr ? "defense PR " + prLink(a.pr) : "no defense PR, a win is not paid") : "";
      $("king-meta").innerHTML = esc(how) + (defense ? " · " + defense : "") + '<br><span class="hk" title="' + esc(king) + '">' + esc(short(king)) + "</span>";
      const pooled = (L.standings || {})[king] || {};
      $("king-facts").innerHTML =
        '<div class="fact"><b class="gold">' + (crowns[king] || 0) + "</b><span>" + ((crowns[king] || 0) === 1 ? "crown" : "crowns") + "</span></div>" +
        '<div class="fact"><b>' + streak + "</b><span>" + (streak === 1 ? "round" : "rounds") + " in a row</span></div>" +
        '<div class="fact"><b>' + num(pooled.score, 3) + "</b><span>pooled score</span></div>" +
        '<div class="fact"><b>' + (pooled.weight != null ? Math.round(100 * pooled.weight) + "%" : "—") + "</b><span>reward weight</span></div>";
    }
    // the field: who is challenging this round
    let field, note;
    const sealed = Object.keys(active).filter((h) => h !== king && !active[h].incumbent);
    if (st === "window") {
      field = [...new Set((L.submissions || []).map((s) => s.hotkey))].filter((h) => h !== king);
      note = field.length ? "entered so far" : "no entries yet";
    } else {
      field = sealed.length ? sealed : Object.keys(active).filter((h) => h !== king);
      note = st === "done" ? "challengers this round" : "racing the baseline";
    }
    $("field-count").innerHTML = field.length + "<small>" + (field.length === 1 ? "challenger" : "challengers") + "</small>";
    $("field-avs").innerHTML = field.slice(0, 14).map((h) => '<span title="' + esc(nameOf(h)) + '">' + avatar(h, "av") + "</span>").join("");
    $("field-note").textContent = note;
  }

  // ─── the timing tower ──────────────────────────────────────────────────────────────────────────────────
  function paired(mine, base) {     // mean gain over the baseline on the tasks both have finished
    const ids = Object.keys(mine || {}).filter((t) => base && base[t] && !mine[t].void && !base[t].void);
    if (!ids.length) return null;
    return ids.reduce((a, t) => a + (mine[t].credit - base[t].credit), 0) / ids.length;
  }
  function laneDetail(s, by) {
    const mine = (by[s] || {}).tasks || {}, base = (by["null"] || {}).tasks || {};
    const ids = [...new Set([...Object.keys(mine), ...Object.keys(base)])].sort();
    if (!ids.length) return '<div class="lane-detail"><div class="td"><span>no episode has finished yet</span></div></div>';
    const c = color(s);
    return '<div class="lane-detail" style="--c:' + c + '">' + ids.map((t) => {
      const m = mine[t], b = base[t];
      const val = m ? (m.dq ? "DQ" : m.void ? "void" : Math.round(100 * m.credit) + "%") : "…";
      const d = m && b && s !== "null" && !m.void ? pts(m.credit - b.credit) : "";
      return '<div class="td"><span class="tid" title="' + esc(t) + '">' + esc(t) + '</span><span class="tb">' +
        (m ? '<i style="width:' + (100 * m.credit).toFixed(1) + '%"></i>' : "") + (b && s !== "null" ? '<b style="left:' + (100 * b.credit).toFixed(1) + '%"></b>' : "") +
        '</span><span class="tv">' + val + '</span><span class="tv">' + esc(d) + "</span></div>";
    }).join("") + "</div>";
  }

  function renderTower() {
    const L = LIVE, st = L.stage, by = (L.progress || {}).by_surface || {}, active = L.active || {};
    const tasks = L.tasks || 0;
    const crown = L.crown && L.crown.standings ? L.crown : null;
    const tower = $("tower");
    let rows = [];

    if (st === "window") {
      $("tower-title").textContent = "On the grid";
      $("tower-sub").textContent = "entries so far, the race starts when the window closes";
      const subs = (L.submissions || []).slice().sort((a, b) => (iso(a.created_at) || 0) - (iso(b.created_at) || 0));
      if (!subs.length) { tower.innerHTML = '<div class="tower-empty">No entries yet: <a href="../guide/">enter a strategy</a></div>'; return; }
      tower.innerHTML = subs.map((s, i) =>
        '<div class="lane" style="--c:' + color(s.hotkey) + '"><span class="lp">' + (i + 1) + '</span>' + who(s.hotkey) +
        '<span class="field-note">entered ' + (iso(s.created_at) ? hhmm(iso(s.created_at)) : "—") + (s.updated_at && s.updated_at !== s.created_at ? " · updated " + hhmm(iso(s.updated_at)) : "") + "</span>" +
        '<span class="gap zero-g">' + prLink(s.pr) + '</span><span class="mv"></span></div>').join("");
      return;
    }

    const surfaces = [...new Set(["null", ...Object.keys(by), ...Object.keys(active)])].filter((s) => s !== "canon" || by.canon);
    const base = (by["null"] || {}).tasks || {};
    rows = surfaces.map((s) => {
      const r = by[s] || { n: 0, verified: 0, tasks: {} };
      const cr = crown && crown.standings[s];
      const d = s === "null" || s === "canon" ? null : cr && cr.delta != null ? cr.delta : paired(r.tasks, base);
      const credit = r.n ? (r.credit != null ? r.credit : r.verified / r.n) : null;
      return { s, r, d, credit, rank: cr && cr.rank, dq: Object.values(r.tasks || {}).some((t) => t.dq) };
    });
    // order: the crown's ranks once decided, otherwise the live gain; the baseline sits where its own score puts it
    const key = (x) => x.rank ? -1e6 + x.rank : x.s === "null" ? -(x.credit ?? -1) * 1e3 + 0.0001 : -(x.credit ?? -1) * 1e3;
    rows.sort((a, b) => key(a) - key(b) || a.s.localeCompare(b.s));
    let pos = 0;
    const kingNow = crown && crown.king;
    $("tower-title").textContent = crown ? "Final standings" : "Timing tower";
    $("tower-sub").textContent = crown
      ? "ranked by gain over the baseline"
      : (L.progress && L.progress.total ? "hidden checks passed, the marker is the baseline" : "lanes fill as episodes finish");

    // remember where each lane was, to animate the reorder
    const before = {};
    tower.querySelectorAll(".lane[data-s]").forEach((el) => { before[el.dataset.s] = el.getBoundingClientRect().top; });
    const now = Date.now();
    const html = rows.map((x) => {
      const ref = x.s === "null" || x.s === "canon";
      const p = ref ? null : ++pos;
      const old = prevPos[x.s];
      if (p && old && old !== p) moved[x.s] = { by: old - p, at: now };
      const mv = moved[x.s] && now - moved[x.s].at < 90000 ? moved[x.s].by : 0;
      if (p) prevPos[x.s] = p;
      const a = active[x.s] || {};
      const chips = (x.s === kingNow ? '<span class="chip king">crowned</span>' : a.incumbent ? '<span class="chip king">' + (a.pr ? "defending " + prLink(a.pr) : "incumbent") + "</span>" : a.pr ? '<span class="chip">' + prLink(a.pr) + "</span>" : "") +
                    (x.dq ? '<span class="chip dq">disqualified</span>' : "");
      const fin = Object.keys(x.r.tasks || {}).length;
      const width = x.credit == null ? 0 : 100 * x.credit;
      const baseCredit = (by["null"] || {}).n ? ((by["null"].credit != null ? by["null"].credit : by["null"].verified / by["null"].n)) : null;
      const gapCls = x.d == null ? "zero-g" : x.d > 1e-9 ? "pos-g" : x.d < -1e-9 ? "neg-g" : "zero-g";
      const open = openLane === x.s;
      return '<div class="lane' + (ref ? " ref" : "") + (x.s === kingNow ? " king" : "") + (x.dq ? " dq" : "") + '" data-s="' + esc(x.s) + '" style="--c:' + color(x.s) + '" tabindex="0" role="button" aria-expanded="' + open + '">' +
        '<span class="lp">' + (ref ? (x.s === "null" ? "BASE" : "REF") : p) + "</span>" +
        who(x.s, chips) +
        '<span class="lane-bar"><i style="width:' + width.toFixed(1) + '%"></i>' + (!ref && baseCredit != null ? '<b style="left:' + (100 * baseCredit).toFixed(1) + '%"></b>' : "") +
        "<s>" + (x.credit == null ? "" : Math.round(width) + "%") + "</s></span>" +
        '<span class="gap ' + gapCls + '" title="gain over the baseline on the tasks both have finished, in points">' + (ref ? "" : pts(x.d)) + "</span>" +
        '<span class="mv">' + (ref ? (tasks ? fin + "/" + tasks : String(fin)) : mv > 0 ? '<span class="up">▲' + mv + "</span>" : mv < 0 ? '<span class="down">▼' + (-mv) + "</span>" : tasks ? fin + "/" + tasks : "") + "</span>" +
        (open ? laneDetail(x.s, by) : "") + "</div>";
    }).join("");
    tower.innerHTML = html || '<div class="tower-empty">Waiting for the seal</div>';
    if (!REDUCED) tower.querySelectorAll(".lane[data-s]").forEach((el) => {   // FLIP: lanes glide to their new place
      const b = before[el.dataset.s]; if (b == null) return;
      const dy = b - el.getBoundingClientRect().top; if (Math.abs(dy) < 2) return;
      el.animate([{ transform: "translateY(" + dy + "px)" }, { transform: "none" }], { duration: 600, easing: "cubic-bezier(.2,.8,.2,1)" });
    });
    const rej = Object.entries(L.rejected || {});
    $("rejected").hidden = !rej.length;
    $("rejected").innerHTML = rej.length ? "Rejected at the seal: " + rej.map(([n, why]) => prLink(n) + " — " + esc(why)).join(" · ") : "";
  }
  function who(h, chips) {
    return '<span class="who">' + avatar(h, "") + '<span class="nm"><b>' + esc(nameOf(h)) + "</b>" +
      '<span title="' + esc(h) + '">' + (h === "null" ? "no strategy" : h === "canon" ? "reference strategy" : esc(short(h))) + (chips || "") + "</span></span></span>";
  }
  function toggleLane(el) {
    const s = el.dataset.s; if (!s) return;
    openLane = openLane === s ? null : s;   // opening one closes the other
    renderTower();
    const el2 = $("tower").querySelector('.lane[data-s="' + CSS.escape(s) + '"]');   // keep the lane in view inside the scrolling tower
    if (openLane && el2) { const t = $("tower"); const top = el2.offsetTop; /* the tower is the lanes' offset parent */ if (top < t.scrollTop || top + el2.offsetHeight > t.scrollTop + t.clientHeight) t.scrollTo({ top: Math.max(0, top - 8), behavior: REDUCED ? "auto" : "smooth" }); }
  }
  $("tower").addEventListener("click", (e) => { if (e.target.closest("a")) return; const el = e.target.closest(".lane[data-s]"); if (el && !e.target.closest(".lane-detail")) toggleLane(el); });
  $("tower").addEventListener("keydown", (e) => { if (e.key !== "Enter" && e.key !== " ") return; const el = e.target.closest(".lane[data-s]"); if (el) { e.preventDefault(); toggleLane(el); } });

  // ─── the live feed: what changed since the last poll ───────────────────────────────────────────────────
  const svg = (d) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + d + "</svg>";
  const ICON = { crown: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 8l4.6 3.8L12 5l4.4 6.8L21 8l-1.9 10.5H4.9z"/></svg>',
                 sub: svg('<path d="M12 4v11m0 0l-4-4m4 4l4-4M5 19h14"/>'), ep: svg('<path d="M13 3L5 14h6l-1 7 8-11h-6l1-7z"/>'),
                 stage: svg('<circle cx="12" cy="12" r="3"/><path d="M5 12a7 7 0 0114 0M2 12a10 10 0 0120 0"/>'),
                 seal: svg('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>'), dq: svg('<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>') };
  function push(kind, t, html, fresh) {
    feed.push({ kind, t, html, fresh, id: kind + t + html });
  }
  function seed() {
    const rounds = closedRounds();
    let prev = null;
    rounds.forEach((r) => {
      if (r.king) {
        const d = r.crown && r.crown[r.king] ? r.crown[r.king].delta : null;
        const took = prev && prev !== r.king ? " from <b>" + esc(nameOf(prev)) + "</b>" : prev === r.king ? " again" : "";
        push("crown", r.closed_at, "<b>" + esc(nameOf(r.king)) + "</b> took the crown" + took + " in " + esc(r.round_id) + (d != null ? " (" + pts(d) + " pts over the baseline)" : ""));
        prev = r.king;
      } else push("stage", r.closed_at, esc(r.round_id) + ": nobody beat the baseline, the crown stays");
    });
    const L = LIVE;
    (L.phases || []).forEach((p) => { if (["open", "seal", "evaluate"].includes(p.stage)) push(p.stage === "seal" ? "seal" : "stage", p.t, stageLine(p.stage)); });
    (L.submissions || []).forEach((s) => { const t = iso(s.created_at); if (t) push("sub", t, "<b>" + esc(nameOf(s.hotkey)) + "</b> entered " + esc(L.round_id) + " " + prLink(s.pr)); });
    feed.sort((a, b) => b.t - a.t);
    feed.splice(60);
  }
  function stageLine(stage) {
    const L = LIVE, n = Object.keys(L.active || {}).length;
    if (stage === "open") return "Round <b>" + esc(L.round_id) + "</b> opened: " + (L.tasks || 6) + " hidden bugs, a two-hour window";
    if (stage === "seal") return "Round <b>" + esc(L.round_id) + "</b> sealed with " + n + " strateg" + (n === 1 ? "y" : "ies");
    if (stage === "evaluate") return "Evaluation started";
    return esc(STAGE_TEXT[stage] || stage);
  }
  function diff() {
    const L = LIVE, now = Date.now() / 1000, by = (L.progress || {}).by_surface || {};
    const snap = { round: L.round_id, stages: new Set((L.phases || []).map((p) => p.stage)), subs: new Set((L.submissions || []).map((s) => s.hotkey + ":" + s.updated_at)),
                   eps: new Set(), king: L.crown && L.crown.king };
    Object.entries(by).forEach(([s, r]) => Object.keys(r.tasks || {}).forEach((t) => snap.eps.add(s + "|" + t)));
    if (seen && seen.round === snap.round) {
      (L.phases || []).forEach((p) => { if (!seen.stages.has(p.stage) && (p.stage === "seal" || p.stage === "evaluate")) push(p.stage === "seal" ? "seal" : "stage", p.t || now, stageLine(p.stage), true); });
      (L.submissions || []).forEach((s) => { if (!seen.subs.has(s.hotkey + ":" + s.updated_at)) push("sub", iso(s.updated_at) || now, "<b>" + esc(nameOf(s.hotkey)) + "</b> " + (s.created_at === s.updated_at ? "entered" : "updated their entry") + " " + prLink(s.pr), true); });
      Object.entries(by).forEach(([s, r]) => Object.entries(r.tasks || {}).forEach(([t, v]) => {
        if (seen.eps.has(s + "|" + t)) return;
        const base = ((by["null"] || {}).tasks || {})[t];
        const tail = t.split("-").slice(-1)[0];
        const vs = s !== "null" && base && !v.void ? " · " + pts(v.credit - base.credit) + " vs baseline" : "";
        push(v.dq ? "dq" : "ep", now, "<b>" + esc(nameOf(s)) + "</b> finished bug " + esc(tail) + ": " + (v.dq ? "disqualified" : v.void ? "void, re-running" : Math.round(100 * v.credit) + "% of checks") + vs, true);
      }));
      if (snap.king && !seen.king) {
        const d = L.crown.standings && L.crown.standings[snap.king] ? L.crown.standings[snap.king].delta : null;
        push("crown", now, "<b>" + esc(nameOf(snap.king)) + "</b> wins " + esc(L.round_id) + (d != null ? " with " + pts(d) + " pts over the baseline" : ""), true);
      }
    } else if (seen && seen.round !== snap.round) {
      push("stage", now, "Round <b>" + esc(L.round_id) + "</b> is on", true);
    }
    seen = snap;
    feed.sort((a, b) => b.t - a.t);
    feed.splice(60);
  }
  function renderFeed() {
    $("feed").innerHTML = feed.length ? feed.map((e) =>
      '<li class="k-' + e.kind + (e.fresh ? " new" : "") + '"><span class="ic" aria-hidden="true">' + (ICON[e.kind] || "•") + '</span><span class="tx">' + e.html +
      '<span class="tm">' + (Date.now() / 1000 - e.t < 86400 ? hhmm(e.t) + " · " + ago(e.t) : when(e.t)) + "</span></span></li>").join("")
      : '<li><span class="ic">' + ICON.stage + '</span><span class="tx">Nothing yet this round</span></li>';
    feed.forEach((e) => { e.fresh = false; });
  }

  // ─── the season ────────────────────────────────────────────────────────────────────────────────────────
  function countUp(el, to, dec) {
    const from = Number(el.dataset.v || 0);
    el.dataset.v = String(to);
    if (REDUCED || from === to) { el.textContent = to.toLocaleString(undefined, { maximumFractionDigits: dec || 0 }); return; }
    const t0 = performance.now(), dur = 1100;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = (from + (to - from) * e).toLocaleString(undefined, { maximumFractionDigits: dec || 0, minimumFractionDigits: 0 });
      if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  let lastTimeline = "";
  const TL_RECENT = 30;
  let tlRange = "recent";
  try { tlRange = localStorage.getItem("sh-tl-range") === "all" ? "all" : "recent"; } catch (e) { /* the default */ }
  function renderSeason() {
    const rounds = closedRounds();
    const crowns = {}, above = {}, bestD = {}, bestRun = {}, miners = new Set();
    let run = { h: null, n: 0 }, changes = 0, prev = null, rows = 0;
    rounds.forEach((r) => {
      Object.keys(r.github || {}).forEach((h) => miners.add(h));
      Object.entries(r.crown || {}).forEach(([h, c]) => { miners.add(h); above[h] = (above[h] || 0) + 1; if (c.delta != null) bestD[h] = Math.max(bestD[h] ?? -1, c.delta); });
      if (r.king) {
        crowns[r.king] = (crowns[r.king] || 0) + 1; miners.add(r.king);
        if (prev && prev !== r.king) changes++;
        prev = r.king;
        run = run.h === r.king ? { h: r.king, n: run.n + 1 } : { h: r.king, n: 1 };
        bestRun[r.king] = Math.max(bestRun[r.king] || 0, run.n);
      }
      rows += (r.sft_rows || 0) + (r.dpo_pairs || 0);
    });
    const kings = Object.keys(crowns).length;
    const cards = [[rounds.length, "rounds closed"], [changes, "times the crown changed hands"], [kings, kings === 1 ? "king so far" : "different kings"],
                   [miners.size, "miners have competed"], [rows, "training rows published"]];
    const box = $("season");
    if (!box.children.length) box.innerHTML = cards.map(() => '<div class="num-card"><b>0</b><span></span></div>').join("");
    [...box.children].forEach((el, i) => { el.querySelector("span").textContent = cards[i][1]; countUp(el.querySelector("b"), cards[i][0]); });

    // standings
    const pooled = (LIVE && LIVE.standings) || {};
    const all = [...new Set([...miners, ...Object.keys(pooled)])].filter((h) => h !== "null" && h !== "canon");
    all.sort((a, b) => (crowns[b] || 0) - (crowns[a] || 0) || (above[b] || 0) - (above[a] || 0) || ((pooled[b] || {}).score || 0) - ((pooled[a] || {}).score || 0));
    const top = Math.max(1, ...all.map((h) => crowns[h] || 0));
    $("season-body").innerHTML = all.length ? all.map((h, i) => {
      const p = pooled[h] || {};
      return '<tr style="--c:' + color(h) + '"><td class="l rk">' + (i + 1) + '</td><td class="l">' + who(h) + "</td>" +
        '<td><span class="crowns"><i style="width:' + Math.round(70 * (crowns[h] || 0) / top) + 'px"></i><b>' + (crowns[h] || 0) + "</b></span></td>" +
        '<td class="opt">' + (above[h] || 0) + '</td><td class="opt">' + (bestRun[h] || 0) + '</td><td class="opt">' + (bestD[h] != null ? pts(bestD[h]) : "—") + "</td>" +
        "<td>" + num(p.score, 3) + "</td><td>" + (p.weight != null ? Math.round(100 * p.weight) + "%" : "—") + "</td></tr>";
    }).join("") : '<tr><td class="l" colspan="8">No closed rounds yet</td></tr>';

    // the crown timeline (rebuilt only when a round closes)
    const tlKey = rounds.map((r) => r.round_id + r.king).join() + tlRange + (window.innerWidth >> 6);
    if (tlKey === lastTimeline) return;
    lastTimeline = tlKey;
    const every = rounds, shown = tlRange === "all" ? every : every.slice(-TL_RECENT);
    const tlBox = $("timeline");
    const dense = tlBox.clientWidth > 0 && tlBox.clientWidth / Math.max(1, shown.length) < 20;   // too narrow for a face on each change of hands
    $("tl-range").hidden = every.length <= TL_RECENT;
    $("tl-all").textContent = "All " + every.length;
    [...$("tl-range").children].forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.range === tlRange)));
    tlBox.classList.toggle("dense", dense);
    const dOf = (r) => r.king && r.crown && r.crown[r.king] ? r.crown[r.king].delta : null;
    const maxD = Math.max(0.05, ...shown.map((r) => dOf(r) || 0));
    let last = null;
    tlBox.innerHTML = shown.map((r) => {
      const d = dOf(r), h = r.king ? Math.max(5, Math.round(100 * (d || 0) / maxD)) : 4;
      const cap = !dense && r.king && r.king !== last ? avatar(r.king, "cap") : "";
      if (r.king) last = r.king;
      const tip = r.king ? nameOf(r.king) + (d != null ? ", " + pts(d) + " pts over the baseline" : "") : "nobody beat the baseline";
      return '<button class="tl' + (r.king ? "" : " none") + '" type="button" data-round="' + esc(r.round_id) + '"' + ' style="height:' + h + "%;--c:" + (r.king ? color(r.king) : "#2a2545") + '" data-tip-title="' + esc(r.round_id) + '" data-tip="' + esc(tip) + '" aria-label="' + esc(r.round_id + ": " + tip) + '">' + cap + "</button>";
    }).join("");
    $("tl-first").textContent = shown.length ? shown[0].round_id : "";
    $("tl-last").textContent = shown.length ? shown[shown.length - 1].round_id : "";
    $("legend").innerHTML = Object.keys(crowns).sort((a, b) => crowns[b] - crowns[a]).map((h) =>
      '<span style="--c:' + color(h) + '"><i></i><b>' + esc(nameOf(h)) + "</b> " + crowns[h] + "</span>").join("");
  }
  $("timeline").addEventListener("click", (e) => { const b = e.target.closest(".tl"); if (b) openRound(b.dataset.round); });
  $("tl-range").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-range]"); if (!b) return;
    tlRange = b.dataset.range;
    try { localStorage.setItem("sh-tl-range", tlRange); } catch (err) { /* only this visit */ }
    renderSeason();
  });
  let tlResize = 0;
  window.addEventListener("resize", () => { clearTimeout(tlResize); tlResize = setTimeout(() => { if (LIVE) renderSeason(); }, 200); });

  // ─── closed rounds and the round detail ────────────────────────────────────────────────────────────────
  function identCell(h, gh) {
    const g = (gh || {})[h] || githubOf(h);
    return '<span class="ident">' + avatar(h, "gh-av") + '<span class="ident-txt">' + (g ? '<a class="gh-name" href="https://github.com/' + encodeURIComponent(g) + '">@' + esc(g) + "</a>" : '<span class="gh-name gh-anon">unlinked</span>') +
      '<span class="hk" title="' + esc(h) + '">' + esc(short(h)) + "</span></span></span>";
  }
  let lastHistory = "", showAll = false;
  const SHOWN = 12;
  function renderHistory() {
    const hist = closedRounds().slice().reverse();
    $("rounds-count").textContent = hist.length ? String(hist.length) : "";
    const key = JSON.stringify(hist.map((h) => [h.round_id, h.king, h.pr])) + showAll;
    if (key === lastHistory) return;
    lastHistory = key;
    const rows = showAll ? hist : hist.slice(0, SHOWN);
    $("history").innerHTML = rows.length ? rows.map((h) => {
      const ks = h.king && h.scores ? h.scores[h.king] : null, kc = h.king && h.crown ? h.crown[h.king] : null;
      return '<tr><td class="l"><a class="round-link" href="../rounds/' + esc(h.round_id) + '/" data-round="' + esc(h.round_id) + '">' + esc(h.round_id) + "</a></td>" +
        '<td class="l">' + (h.king ? identCell(h.king, h.github) : '<span class="zero">nobody beat the baseline</span>') + "</td>" +
        '<td class="l">' + (h.king && h.pr ? prLink(h.pr) : '<span class="zero">—</span>') + "</td>" +
        "<td class='" + (kc && kc.delta > 0 ? "pos" : "zero") + "'>" + signed(kc && kc.delta, 3) + "</td><td>" + num(ks && ks.score, 4) + "</td><td>" + num(ks && ks.weight, 3) + "</td>" +
        "<td>" + (h.sft_rows ?? "—") + "</td><td>" + (h.dpo_pairs ?? "—") + "</td>" +
        "<td class='l'>" + (h.commitments_ok ? "<span class='ok'>verified</span>" : "<span class='neg'>mismatch</span>") + "</td><td class='faint'>" + when(h.closed_at) + "</td></tr>";
    }).join("") : '<tr><td class="empty" colspan="10">No closed rounds yet</td></tr>';
    const more = $("rounds-more");
    more.hidden = hist.length <= SHOWN;
    more.textContent = showAll ? "Show the latest " + SHOWN : "Show all " + hist.length + " rounds";
    const q = (LIVE && LIVE.queue) || [];
    $("queue-line").textContent = q.length ? "Minted ahead: " + q.map((r) => r.round_id).join(", ") + " (digests in rounds/queue.json)" : "";
  }
  $("rounds-more").addEventListener("click", () => { showAll = !showAll; renderHistory(); if (!showAll) $("rounds").scrollIntoView({ block: "start" }); });
  function roundDetail(h) {
    const scores = h.scores || {}, crown = h.crown || {};
    const ranked = Object.keys(scores).sort((a, b) => ((crown[a] || {}).rank || 99) - ((crown[b] || {}).rank || 99) || ((scores[b] || {}).weight || 0) - ((scores[a] || {}).weight || 0));
    const rows = ranked.map((k) => { const s = scores[k] || {}, c = crown[k] || {};
      return "<tr" + (k === h.king ? " class='king'" : "") + "><td class='l'>" + identCell(k, h.github) + "</td><td>" + (c.rank || "—") + "</td><td class='" + (c.delta > 0 ? "pos" : "zero") + "'>" + signed(c.delta, 3) +
        "</td><td>" + num(s.score, 4) + "</td><td>" + num(s.weight, 3) + "</td></tr>"; }).join("") || "<tr><td class='empty' colspan='5'>no strategies were sealed</td></tr>";
    const stat = (v, k) => "<div class='stat'><b>" + v + "</b><span>" + k + "</span></div>";
    const tree = "https://github.com/" + esc(repo()) + "/tree/" + esc(branch()) + "/rounds/" + esc(h.round_id);
    return "<div class='head'><h1>Round " + esc(h.round_id) + "</h1><span class='badge" + (h.king ? " crowned'>crowned" : "'>no king") + "</span><span class='muted small'>closed " + when(h.closed_at) + "</span></div>" +
      "<div class='strip' style='margin:1rem 0'>" + stat(h.king ? identCell(h.king, h.github) : "<span class='zero'>none</span>", "king" + (h.pr ? " · " + prLink(h.pr) : "")) +
      stat(h.sft_rows ?? "—", "SFT rows") + stat(h.dpo_pairs ?? "—", "DPO pairs") +
      stat("<span class='" + (h.commitments_ok ? "pos" : "neg") + "'>" + (h.commitments_ok ? "verified" : "mismatch") + "</span>", "commitments") + "</div>" +
      "<div class='wrap'><table><thead><tr><th class='l'>strategy</th><th>rank</th><th>Δ round</th><th>score</th><th>weight</th></tr></thead><tbody>" + rows + "</tbody></table></div>" +
      '<p class="note" style="margin-top:1rem"><a href="../rounds/' + esc(h.round_id) + '/">Full round page</a> · <a href="' + tree + '">rounds/' + esc(h.round_id) + "/</a>" +
      (Array.isArray(h.revealed) && h.revealed.length ? ' · <a href="' + tree + '/revealed">revealed bundles (' + h.revealed.length + ")</a>" : "") +
      (typeof h.hf === "string" && h.hf.startsWith("https://") ? ' · <a href="' + esc(h.hf) + '">dataset</a>' : "") + "</p>";
  }
  const behind = () => document.querySelectorAll("main, header.top, footer");
  function openRound(id) {
    if (!ROUND_ID.test(id || "")) return;
    const h = closedRounds().find((x) => x.round_id === id);
    if (!h) { location.href = "../rounds/" + id + "/"; return; }
    const modal = $("round-modal"), card = modal.querySelector(".modal-card");
    $("rm-body").innerHTML = roundDetail(h);
    if (modal.hidden) lastFocus = document.activeElement;
    modal.hidden = false; document.body.classList.add("modal-open");
    behind().forEach((el) => { el.inert = true; });
    card.tabIndex = -1; card.focus({ preventScroll: true });
    if (location.hash !== "#round-" + id) history.replaceState(null, "", "#round-" + id);
  }
  function closeRound() {
    $("round-modal").hidden = true; document.body.classList.remove("modal-open");
    behind().forEach((el) => { el.inert = false; });
    if (location.hash.startsWith("#round-")) history.replaceState(null, "", location.pathname + location.search);
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    lastFocus = null;
  }
  $("history").addEventListener("click", (e) => { const a = e.target.closest(".round-link"); if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); openRound(a.dataset.round); });
  $("round-modal").addEventListener("click", (e) => { if (e.target.matches("[data-close]")) closeRound(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("round-modal").hidden) closeRound(); });
  window.addEventListener("hashchange", () => { const m = location.hash.match(/^#round-([a-z]\d{1,4})$/); if (m) openRound(m[1]); else if (!$("round-modal").hidden) closeRound(); });

  // ─── polling ───────────────────────────────────────────────────────────────────────────────────────────
  function render() {
    if (!LIVE) return;
    assignColours();
    if (seen === null && indexTried) seed();
    if (indexTried) diff();
    renderHero(); paintClock(); renderTower(); renderFeed(); renderSeason(); renderHistory();
    if (!deepLinked && indexTried) {
      deepLinked = true;
      const m = location.hash.match(/^#round-([a-z]\d{1,4})$/);
      if (m) { try { openRound(m[1]); } catch (e) { console.warn("round modal", e); } }
    }
  }
  async function tick() {
    try {
      const r = await fetch("live.json?t=" + Date.now(), { cache: "no-store" });
      if (!r.ok) { $("status").innerHTML = '<span class="pulse warn"></span>live.json returned ' + r.status; return; }
      LIVE = await r.json();
      render();
    } catch (e) { $("status").innerHTML = '<span class="pulse warn"></span>offline, retrying'; }
  }
  async function loadRounds() {
    const before = JSON.stringify(ALL);
    try {
      const r = await fetch("../rounds/index.json?t=" + Date.now(), { cache: "no-store" });
      const j = r.ok ? await r.json() : null;
      if (j && Array.isArray(j.rounds)) ALL = j.rounds;
    } catch (e) { /* the last 20 rounds from live.json still fill the page */ }
    const first = !indexTried;
    indexTried = true;
    if (LIVE && (first || JSON.stringify(ALL) !== before)) render();
  }
  tick(); loadRounds();
  setInterval(tick, 10000);
  setInterval(loadRounds, 60000);
  setInterval(paintClock, 1000);
})();
