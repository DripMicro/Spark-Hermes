/* What every page shares: the animated background, the header's live round chip and menu, the previous/next links
   on a round's page, and the copy buttons beside commands. `data-root` on <body> is the path back to the site root. */
(function () {
  "use strict";
  const ROOT = document.body.dataset.root || "./";
  const REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ─── the background: a dim grid, with signals running along its lines like packets on a board ────────────
  (function background() {
    const host = document.createElement("div");
    host.className = "bg";
    host.setAttribute("aria-hidden", "true");
    const cv = document.createElement("canvas");
    host.appendChild(cv);
    document.body.prepend(host);
    const ctx = cv.getContext("2d");
    if (!ctx) return;
    const S = 34;                                   // grid pitch, CSS px
    const COLORS = ["167,139,250", "167,139,250", "196,181,253", "34,211,238"];
    let W = 0, H = 0, dpr = 1, dots = null, pulses = [], raf = 0, last = 0, pointer = null;

    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      W = window.innerWidth; H = window.innerHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dots = document.createElement("canvas");      // the grid is drawn once and copied every frame
      dots.width = cv.width; dots.height = cv.height;
      const d = dots.getContext("2d");
      d.setTransform(dpr, 0, 0, dpr, 0, 0);
      d.fillStyle = "rgba(167,139,250,.16)";
      for (let x = S / 2; x < W; x += S) for (let y = S / 2; y < H; y += S) d.fillRect(x - .75, y - .75, 1.5, 1.5);
      const want = Math.max(4, Math.min(14, Math.round(W * H / 110000)));
      while (pulses.length < want) pulses.push(spawn());
      pulses.length = want;
    }
    function spawn() {
      const cols = Math.max(1, Math.floor(W / S)), rows = Math.max(1, Math.floor(H / S));
      const dir = [[1, 0], [-1, 0], [0, 1], [0, -1]][Math.floor(Math.random() * 4)];
      return { x: S / 2 + S * Math.floor(Math.random() * cols), y: S / 2 + S * Math.floor(Math.random() * rows), dx: dir[0], dy: dir[1],
               v: 1.1 + Math.random() * 1.3, trail: [], c: COLORS[Math.floor(Math.random() * COLORS.length)], life: 260 + Math.random() * 520 };
    }
    function step(p) {
      p.x += p.dx * p.v; p.y += p.dy * p.v; p.life -= 1;
      p.trail.push([p.x, p.y]);
      if (p.trail.length > 34) p.trail.shift();
      const ox = (p.x - S / 2) / S, oy = (p.y - S / 2) / S;   // at a grid crossing, sometimes turn
      if (Math.abs(ox - Math.round(ox)) * S < p.v / 2 + .01 && Math.abs(oy - Math.round(oy)) * S < p.v / 2 + .01 && Math.random() < .28) {
        p.x = S / 2 + Math.round(ox) * S; p.y = S / 2 + Math.round(oy) * S;
        const turn = Math.random() < .5 ? 1 : -1;
        [p.dx, p.dy] = [p.dy * turn, p.dx * -turn];
      }
      return p.life > 0 && p.x > -S && p.y > -S && p.x < W + S && p.y < H + S;
    }
    function draw(t) {
      raf = requestAnimationFrame(draw);
      if (t - last < 28) return;                    // ~35 fps is plenty for a background
      last = t;
      ctx.clearRect(0, 0, W, H);
      ctx.drawImage(dots, 0, 0, W, H);
      if (pointer) {
        const g = ctx.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, 220);
        g.addColorStop(0, "rgba(167,139,250,.10)"); g.addColorStop(1, "rgba(167,139,250,0)");
        ctx.fillStyle = g; ctx.fillRect(pointer.x - 220, pointer.y - 220, 440, 440);
      }
      ctx.lineCap = "round";
      pulses.forEach((p, i) => {
        if (!step(p)) { pulses[i] = spawn(); return; }
        const n = p.trail.length;
        for (let k = 1; k < n; k++) {
          ctx.strokeStyle = "rgba(" + p.c + "," + (0.4 * k / n).toFixed(3) + ")";
          ctx.lineWidth = 1.4;
          ctx.beginPath(); ctx.moveTo(p.trail[k - 1][0], p.trail[k - 1][1]); ctx.lineTo(p.trail[k][0], p.trail[k][1]); ctx.stroke();
        }
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 9);
        g.addColorStop(0, "rgba(" + p.c + ",.65)"); g.addColorStop(1, "rgba(" + p.c + ",0)");
        ctx.fillStyle = g; ctx.fillRect(p.x - 9, p.y - 9, 18, 18);
      });
    }
    size();
    if (REDUCED) { ctx.drawImage(dots, 0, 0, W, H); window.addEventListener("resize", () => { size(); ctx.clearRect(0, 0, W, H); ctx.drawImage(dots, 0, 0, W, H); }); return; }
    let rt = 0;
    window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(size, 150); });
    if (window.matchMedia("(pointer: fine)").matches) {
      window.addEventListener("pointermove", (e) => { pointer = { x: e.clientX, y: e.clientY }; }, { passive: true });
      document.addEventListener("pointerleave", () => { pointer = null; });
    }
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) { cancelAnimationFrame(raf); raf = 0; } else if (!raf) raf = requestAnimationFrame(draw);
    });
    raf = requestAnimationFrame(draw);
  })();

  // ─── the header: menu on small screens, and the round on now ──────────────────────────────────────────────
  const btn = document.querySelector(".menu-btn"), menu = document.getElementById("menu");
  if (btn && menu) {
    const set = (open) => { menu.classList.toggle("open", open); btn.setAttribute("aria-expanded", String(open)); };
    btn.addEventListener("click", () => set(!menu.classList.contains("open")));
    menu.addEventListener("click", (e) => { if (e.target.closest("a")) set(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && menu.classList.contains("open")) { set(false); btn.focus(); } });
  }
  const chip = document.getElementById("now");
  const STAGE = { window: "window open", seal: "sealing", images: "building tasks", evaluate: "evaluating", close: "scoring", crown: "crowning",
                  announce: "announcing", export: "exporting", publish_close: "publishing", done: "closed", waiting: "waiting", open: "opening" };
  async function now() {
    if (!chip) return;
    try {
      const r = await fetch(ROOT + "live/live.json?t=" + Date.now(), { cache: "no-store" });
      if (!r.ok) return;
      const L = await r.json(), st = L.stage, p = L.progress || {};
      const stale = typeof L.updated === "number" && Date.now() / 1000 - L.updated > 900;
      const crowned = st === "done" && L.crown && L.crown.king;
      let what = crowned ? "crowned" : STAGE[st] || st;
      if (st === "evaluate" && p.total) what += " " + (p.done || 0) + "/" + p.total;
      if (st === "window" && L.window) { const left = Math.max(0, L.window.closes_at - Date.now() / 1000); what += " · " + Math.floor(left / 3600) + "h " + String(Math.floor(left % 3600 / 60)).padStart(2, "0") + "m"; }
      chip.className = "now " + (stale ? "" : crowned ? "crowned" : st === "done" || st === "waiting" ? "" : "live");
      chip.innerHTML = "<i></i><span>" + String(L.round_id || "").replace(/[^a-z0-9]/gi, "") + "<b> · " + what.replace(/[<>&]/g, "") + (stale ? " (stale)" : "") + "</b></span>";
      chip.title = "Round " + L.round_id + ": " + what;
      chip.hidden = false;
    } catch (e) { /* the chip stays hidden offline */ }
  }
  now();
  setInterval(now, 30000);

  // ─── a closed round's page: links to the rounds either side ───────────────────────────────────────────────
  const rid = document.body.dataset.round, pager = document.getElementById("pager");
  if (rid && pager) {
    fetch(ROOT + "rounds/index.json", { cache: "no-store" }).then((r) => r.ok ? r.json() : null).then((j) => {
      const ids = ((j && j.rounds) || []).map((r) => r.round_id).filter((x) => /^[a-z]\d{1,4}$/.test(x)).sort();
      const i = ids.indexOf(rid);
      if (i < 0) return;
      const a = (id, txt) => '<a href="' + ROOT + "rounds/" + id + '/">' + txt + "</a>";
      pager.innerHTML = "<span>" + (i > 0 ? a(ids[i - 1], "‹ " + ids[i - 1]) : "") + "</span><span>" + (i < ids.length - 1 ? a(ids[i + 1], ids[i + 1] + " ›") : '<a href="' + ROOT + 'live/">The round on now ›</a>') + "</span>";
    }).catch(() => {});
  }

  // ─── copy buttons ─────────────────────────────────────────────────────────────────────────────────────────
  document.addEventListener("click", (e) => {
    const b = e.target.closest(".copy");
    if (!b) return;
    const code = b.parentElement.querySelector("code");
    if (!code) return;
    const done = () => { b.textContent = "Copied"; b.classList.add("done"); setTimeout(() => { b.textContent = "Copy"; b.classList.remove("done"); }, 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(code.textContent).then(done, () => {});
  });
})();
