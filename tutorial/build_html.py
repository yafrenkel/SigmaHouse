#!/usr/bin/env python3
"""Convert every Markdown file under tutorial/ into a standalone HTML page.

Why: so the tutorial can be projected in a browser during camp — fully OFFLINE
(all CSS is embedded; no internet, no CDN).

Re-run any time to re-sync after edits:
    py -3 build_html.py

What it does:
  - Walks this folder and every subfolder for *.md files.
  - Converts each to <name>.html right next to the .md.
  - Rewrites links between .md files to .html so clicking works in the browser.
  - Renders markdown *inside* <details> blocks (the collapsible asides).

One-time setup (needs internet once; pure-Python so it then works offline):
    py -3 -m pip install markdown
"""

import os
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("Missing dependency. Run once (with internet):  py -3 -m pip install markdown")

ROOT = os.path.dirname(os.path.abspath(__file__))

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "md_in_html", "toc"]

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  font-size: 18px; line-height: 1.65; color: #1f2328;
  max-width: 980px; margin: 0 auto; padding: 0 24px 80px;
  background: #ffffff;
}
.topbar {
  position: sticky; top: 0; background: #ffffffee; backdrop-filter: blur(4px);
  border-bottom: 1px solid #e1e4e8; padding: 10px 0; margin-bottom: 24px;
  font-size: 0.85em;
}
.topbar a { color: #0969da; text-decoration: none; font-weight: 600; }
.topbar a:hover { text-decoration: underline; }
h1 { font-size: 2.1em; border-bottom: 2px solid #e1e4e8; padding-bottom: .3em; margin-top: 1.2em; }
h2 { font-size: 1.55em; border-bottom: 1px solid #e1e4e8; padding-bottom: .25em; margin-top: 1.6em; }
h3 { font-size: 1.25em; margin-top: 1.4em; }
h4 { font-size: 1.05em; margin-top: 1.2em; }
a { color: #0969da; }
p, li { font-size: 1em; }
code {
  font-family: Consolas, "SF Mono", Menlo, monospace; font-size: 0.88em;
  background: #f0f1f2; padding: .15em .4em; border-radius: 4px;
}
pre {
  background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 8px;
  padding: 14px 16px; overflow-x: auto; line-height: 1.5;
}
pre code { background: none; padding: 0; font-size: 0.92em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; display: block; overflow-x: auto; }
th, td { border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; vertical-align: top; }
th { background: #f0f1f2; }
tr:nth-child(even) td { background: #fafbfc; }
blockquote {
  border-left: 4px solid #d0d7de; margin: 1em 0; padding: .4em 1em;
  color: #57606a; background: #f6f8fa; border-radius: 0 6px 6px 0;
}
blockquote p { margin: .4em 0; }
details {
  border: 1px solid #d0d7de; border-radius: 8px; padding: .6em 1em; margin: 1em 0;
  background: #fbfcfd;
}
summary { cursor: pointer; font-weight: 600; }
details[open] summary { margin-bottom: .6em; }
hr { border: none; border-top: 1px solid #e1e4e8; margin: 2em 0; }
img { max-width: 100%; }
@media print {
  .topbar { display: none; }
  body { max-width: none; font-size: 12pt; }
  details { page-break-inside: avoid; }
  details:not([open]) > *:not(summary) { display: revert; }  /* print expands details */
}
"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="topbar"><a href="{index_href}">⌂ Tutorial Index</a></div>
<article>
{body}
</article>
</body>
</html>
"""


def rewrite_md_links(html):
    """Turn local .md links into .html links (leave external http(s) links alone)."""
    return re.sub(
        r'href="(?!https?://)([^"]+?)\.md(#[^"]*)?"',
        lambda m: 'href="%s.html%s"' % (m.group(1), m.group(2) or ""),
        html,
    )


def convert_file(md_path):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()

    # Let markdown render *inside* the collapsible <details> asides.
    text = text.replace("<details>", '<details markdown="1">')

    body = markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")
    body = rewrite_md_links(body)

    # Title = first <h1>, else the filename.
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title = re.sub("<.*?>", "", m.group(1)).strip() if m else os.path.basename(md_path)

    # Relative path back to the root INDEX.html (works from any subfolder).
    rel = os.path.relpath(ROOT, os.path.dirname(md_path)).replace("\\", "/")
    index_href = "INDEX.html" if rel == "." else rel + "/INDEX.html"

    out = TEMPLATE.format(title=title, css=CSS, body=body, index_href=index_href)
    html_path = os.path.splitext(md_path)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(out)
    return html_path


def main():
    count = 0
    for dirpath, _dirs, files in os.walk(ROOT):
        for name in files:
            if name.lower().endswith(".md"):
                p = convert_file(os.path.join(dirpath, name))
                print("  wrote", os.path.relpath(p, ROOT))
                count += 1
    print("\nDone - %d page(s). Open INDEX.html in your browser to start." % count)


if __name__ == "__main__":
    import sys
    # DISABLED ON PURPOSE. The tutorial is now maintained as HTML directly --
    # the .html files are the source of truth and are hand-edited. Running this
    # would OVERWRITE those hand-edited .html files from the (now stale) .md files.
    if "--force" not in sys.argv:
        print("build_html is DISABLED: the tutorial HTML is now hand-edited.")
        print("Running this would overwrite your .html edits from the stale .md files.")
        print("If you REALLY mean to regenerate from .md, run:  py -3 build_html.py --force")
        raise SystemExit(1)
    main()
