"""The header and footer every generated page shares with the hand-written ones in `docs/` (landing, live board).

`root` is the relative path back to the site root (`../../` from a round page); `current` names the menu entry
the page belongs to, so the header can mark it.
"""

from __future__ import annotations

import html

REPO_URL = "https://github.com/gittensor-model-hub/Spark-Hermes"
DATASET_URL = "https://huggingface.co/datasets/gittensor-model-hub/spark-hermes-rounds"
SITE_URL = "https://gittensor-model-hub.github.io/Spark-Hermes/"

MENU_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
    '<path d="M4 7h16M4 12h16M4 17h16"/></svg>'
)


def social(title: str, description: str, path: str = "") -> str:
    """Link-preview tags, so a page pasted into Discord or X shows the banner, its title and what it is."""
    t, d, url = html.escape(title), html.escape(description), html.escape(SITE_URL + path)
    return f"""<meta property="og:type" content="website">
<meta property="og:site_name" content="Spark-Hermes">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}assets/banner.jpg">
<meta name="twitter:card" content="summary_large_image">"""


def header(root: str, current: str = "") -> str:
    items = [
        ("live", f"{root}live/", "Live"),
        ("season", f"{root}live/#season", "Season"),
        ("rounds", f"{root}live/#rounds", "Rounds"),
        ("guide", f"{root}guide/", "Guide"),
        ("dataset", DATASET_URL, "Dataset"),
        ("github", REPO_URL, "GitHub"),
    ]
    menu = "\n".join(
        f'      <a href="{html.escape(u)}"{' aria-current="page"' if k == current else ""}>{t}</a>' for k, u, t in items
    )
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="top-in">
    <a class="brand" href="{root}"><img src="{root}assets/logo.png" alt="" width="30" height="30">Spark-Hermes<em>SN74</em></a>
    <nav class="menu" id="menu" aria-label="Site">
{menu}
    </nav>
    <a class="round-chip" id="now" href="{root}live/" hidden></a>
    <button class="icon-btn menu-btn" type="button" aria-controls="menu" aria-expanded="false" aria-label="Menu">{MENU_ICON}</button>
  </div>
</header>"""


def footer(root: str, blurb: str) -> str:
    return f"""<footer class="foot">
  <div>
    <a class="brand" href="{root}"><img src="{root}assets/logo.png" alt="" width="26" height="26">Spark-Hermes</a>
    <p>{blurb}</p>
  </div>
  <div><h3>Competition</h3><ul><li><a href="{root}live/">Live round</a></li><li><a href="{root}live/#season">Season standings</a></li><li><a href="{root}live/#rounds">Closed rounds</a></li></ul></div>
  <div><h3>Compete</h3><ul><li><a href="{root}guide/">Miner guide</a></li><li><a href="{root}pins/">Pins</a></li><li><a href="{root}#how">How a round runs</a></li></ul></div>
  <div><h3>Open</h3><ul><li><a href="{DATASET_URL}">Training dataset</a></li><li><a href="{REPO_URL}">Source code</a></li></ul></div>
  <div class="legal">Gittensor SN74 · MIT licence</div>
</footer>"""
