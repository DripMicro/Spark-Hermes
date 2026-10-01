"""The repository's miner-facing documents as pages of the site, so a miner never leaves it to read the rules.

The Markdown in the repository stays the source (`submissions/README.md`, `docs/pins.md`); this renders it with
the site's header, footer and a table of contents. Only the Markdown those files use is understood: headings,
paragraphs, lists, fenced code, tables, `code`, **bold**, *emphasis* and links.

    python -m sh.web.docs            # rewrites docs/guide/index.html and docs/pins/index.html
    python -m sh.web.docs --check    # exits 1 if either page is stale (CI and the tests run this)
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

from sh.web.chrome import REPO_URL, footer, header

ROOT = Path(__file__).resolve().parents[2]

# (source, page, menu entry, title, description, lead)
PAGES = [
    (
        "submissions/README.md",
        "docs/guide/index.html",
        "guide",
        "Miner guide",
        "How to enter Spark-Hermes: what a strategy is, the commands for each round, what you are scored on and how the crown is paid.",
        "Everything a miner needs, from practice bugs to a paid crown",
    ),
    (
        "docs/pins.md",
        "docs/pins/index.html",
        "",
        "Pins",
        "What every Spark-Hermes round is measured against: the agent, model, engine, sampling, sandbox, scoring and round clock.",
        "What every strategy runs against",
    ),
]

# a file named in the text that is also a page of the site links there; anything else in the repository links to GitHub
ON_SITE = {"docs/pins.md": "pins/", "submissions/README.md": "guide/", "docs/live/live.json": "live/live.json"}


def _slug(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"[^a-z0-9]+", "-", html.unescape(s).lower()).strip("-")
    return s or "section"


def _inline(text: str, root: str) -> str:
    """Code spans are set aside first (their content is literal), then the rest is escaped and gets links, bold
    and emphasis, which may wrap a code span; the spans go back in last."""
    text = text.replace("\\`", "\x00")  # an escaped backtick is a literal one, even inside a code span
    spans: list[str] = []

    def keep(m: re.Match) -> str:
        code = m.group(1).replace("\x00", "`")
        span = f"<code>{html.escape(code)}</code>"
        if code in ON_SITE:
            span = f'<a href="{root}{ON_SITE[code]}">{span}</a>'
        spans.append(span)
        return f"\x01{len(spans) - 1}\x02"

    t = re.sub(r"`([^`]*)`", keep, text)
    t = html.escape(t.replace("\x00", "`"), quote=False)

    def link(m: re.Match) -> str:
        label, url = m.group(1), html.unescape(m.group(2))
        if not re.match(r"https?://", url):
            url = f"{root}{ON_SITE[url]}" if url in ON_SITE else f"{REPO_URL}/blob/main/{url}"
        return f'<a href="{html.escape(url)}">{label}</a>'

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return re.sub(r"\x01(\d+)\x02", lambda m: spans[int(m.group(1))], t)


def render_markdown(md: str, root: str) -> tuple[str, str, list[tuple[str, str]]]:
    """(the first heading, the body HTML, the table of contents as (id, title) for each `##`)."""
    lines = md.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    title = ""
    seen: set[str] = set()
    i = 0

    def para_end(j: int) -> bool:
        s = lines[j]
        return not s.strip() or s.startswith(("#", "```", "|")) or bool(re.match(r"\s{0,3}(?:[-*]|\d+\.)\s", s))

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(body), quote=False)
            copy = '<button class="copy" type="button">Copy</button>' if lang in ("sh", "bash") else ""
            out.append(f'<div class="codeblock"><pre><code>{code}</code></pre>{copy}</div>')
            continue
        m = re.match(r"(#{1,3})\s+(.*)", line)
        if m:
            level, text = len(m.group(1)), _inline(m.group(2), root)
            if level == 1 and not title:
                title = re.sub(r"<[^>]+>", "", text)
            else:
                sid = base = _slug(text)
                n = 2
                while sid in seen:
                    sid, n = f"{base}-{n}", n + 1
                seen.add(sid)
                if level <= 2:
                    toc.append((sid, re.sub(r"<[^>]+>", "", text)))
                tag = "h2" if level <= 2 else "h3"
                out.append(f'<{tag} id="{sid}"><a class="anchor" href="#{sid}">{text}</a></{tag}>')
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = re.split(r"(?<!\\)\|", lines[i].strip()[1:-1])  # an escaped pipe belongs to its cell
                rows.append([c.strip().replace("\\|", "|") for c in cells])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            th = "".join(f"<th>{_inline(c, root)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{_inline(c, root)}</td>" for c in r) + "</tr>" for r in body)
            out.append(
                f'<div class="wrap"><table class="doc-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'
            )
            continue
        m = re.match(r"(\s{0,3})([-*]|\d+\.)\s+(.*)", line)
        if m:
            ordered = m.group(2)[0].isdigit()
            items: list[str] = []
            while i < len(lines):
                m = re.match(r"\s{0,3}([-*]|\d+\.)\s+(.*)", lines[i])
                if m and (m.group(1)[0].isdigit()) == ordered:
                    items.append(m.group(2))
                    i += 1
                elif items and lines[i].startswith("  ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(t, root)}</li>" for t in items) + f"</{tag}>")
            continue
        buf = [line.strip()]
        i += 1
        while i < len(lines) and not para_end(i):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(buf), root)}</p>")
    return title, "\n".join(out), toc


def render_page(md: str, current: str, title: str, description: str, lead: str, source: str) -> str:
    root = "../"
    _, body, toc = render_markdown(md, root)
    nav = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t in toc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Spark-Hermes</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#06050d">
<link rel="icon" href="{root}assets/favicon.png">
<link rel="stylesheet" href="{root}site.css">
</head>
<body data-root="{root}">
{header(root, current)}
<main class="doc">
  <div class="doc-head">
    <h1>{html.escape(title)}</h1>
    <p class="lead">{html.escape(lead)}</p>
  </div>
  <div class="doc-grid">
    <nav class="toc" aria-label="On this page"><p>On this page</p><ol>{nav}</ol></nav>
    <article class="prose">
{body}
      <p class="doc-src">Generated from <code>{source}</code></p>
    </article>
  </div>
</main>
{footer(root, "Strategy competition on Gittensor SN74")}
<script src="{root}site.js"></script>
</body>
</html>
"""


def build(check: bool = False) -> list[str]:
    """Write (or, with `check`, compare) every page; returns the pages that were stale."""
    stale = []
    for src, dst, current, title, description, lead in PAGES:
        page = render_page((ROOT / src).read_text(), current, title, description, lead, src)
        out = ROOT / dst
        if not out.exists() or out.read_text() != page:
            stale.append(dst)
            if not check:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(page)
    return stale


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if a page is out of date with its Markdown")
    a = ap.parse_args(argv)
    stale = build(check=a.check)
    for s in stale:
        print(("stale: " if a.check else "wrote: ") + s)
    return 1 if (a.check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
