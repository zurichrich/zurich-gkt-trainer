#!/usr/bin/env python3
"""
Generate a bilingual PDF from the Einbürgerungskurs 2026 markdown file.
Uses pandoc for markdown→HTML conversion and weasyprint for HTML→PDF.

The markdown has <!-- Page X --> comments marking original page boundaries.
We insert CSS page breaks at these markers. The bilingual text (DE+EN) is
roughly 2× the original German-only text, so we use compact styling to
fit as much as possible per page. Some pages will still overflow, creating
extra pages — this is acceptable for a bilingual study document.
"""

import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_FILE = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026.md")
OUTPUT_PDF = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026-bilingual.pdf")
IMAGES_DIR = os.path.join(BASE_DIR, "images", "einbuergerungskurs-2026")

# All page markers 4-75 get hard page breaks
HARD_BREAK_PAGES = set(range(4, 76))

CSS = r"""
@page {
    size: A4;
    margin: 1.8cm 1.8cm 2cm 1.8cm;
    @bottom-right {
        content: counter(page);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #cc0000;
        font-weight: bold;
    }
}

@page cover {
    margin: 0;
    @bottom-right { content: none; }
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 7pt;
    line-height: 1.2;
    color: #222;
    orphans: 1;
    widows: 1;
}

/* ═══════════════ Cover ═══════════════ */
.cover-page {
    page: cover;
    background-color: #cc0000;
    color: white;
    text-align: center;
    padding-top: 10cm;
    height: 297mm;
    width: 210mm;
    box-sizing: border-box;
    page-break-after: always;
}
.cover-page h1 {
    font-size: 28pt; color: white; border-bottom: none;
    page-break-before: auto; margin: 0 0 0.3em 0;
}
.cover-page p { font-size: 12pt; color: white; margin: 0.2em 0; }
.cover-page em { color: rgba(255,255,255,0.85); font-style: italic; }

/* ═══════════════ Page breaks ═══════════════ */
.page-break {
    break-before: page;
    page-break-before: always;
}

/* ═══════════════ Headings ═══════════════ */
h1 {
    font-size: 11pt; color: #cc0000;
    border-bottom: 1.5pt solid #cc0000; padding-bottom: 2pt;
    margin: 3pt 0 2pt 0;
    page-break-before: auto; page-break-after: avoid;
}
h2 {
    font-size: 9pt; color: #cc0000;
    margin: 2pt 0 1pt 0; page-break-after: avoid;
}
h3 {
    font-size: 8pt; color: #333;
    margin: 2pt 0 1pt 0; page-break-after: avoid;
}

hr { border: none; border-top: 1.5pt solid #cc0000; margin: 3pt 0; }

/* ═══════════════ Text ═══════════════ */
em { font-style: italic; color: #555; }
strong { font-weight: 700; }
p { margin: 1.5pt 0; }
ul, ol { margin: 1pt 0 1pt 12pt; padding: 0; }
li { margin-bottom: 0.5pt; }

/* ═══════════════ Images ═══════════════ */
img {
    max-width: 90%; height: auto;
    display: block; margin: 3pt auto;
}
figure { margin: 3pt 0; }
figcaption {
    font-size: 6pt; color: #777; text-align: center; margin-top: 1pt;
}

/* ═══════════════ Food 2×2 grid ═══════════════ */
.food-grid {
    display: flex; flex-wrap: wrap;
    justify-content: space-between; gap: 4pt; margin: 4pt 0;
}
.food-grid .food-item { width: 48%; box-sizing: border-box; }
.food-grid .food-item img { width: 100%; height: auto; margin: 0; }
.food-grid .food-item figcaption { font-size: 5.5pt; }

/* ═══════════════ Tables ═══════════════ */
table { width: 100%; border-collapse: collapse; margin: 3pt 0; font-size: 6.5pt; }
th, td { border: 1px solid #ccc; padding: 1.5pt 4pt; text-align: left; }
th { background-color: #f0f0f0; font-weight: 600; }
"""


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def preprocess(md):
    """Fix image paths and insert page-break divs at selected markers."""
    md = md.replace(
        "../images/einbuergerungskurs-2026/",
        f"file://{IMAGES_DIR}/",
    )
    lines = md.split("\n")
    out = []
    for line in lines:
        m = re.match(r"^\s*<!--\s*Page\s+(\d+)\s*-->\s*$", line)
        if m:
            pn = int(m.group(1))
            if pn == 1:
                continue
            if pn in HARD_BREAK_PAGES:
                out.append('<div class="page-break"></div>')
        else:
            out.append(line)
    return "\n".join(out)


def md_to_html(md):
    r = subprocess.run(
        ["pandoc", "--from", "markdown", "--to", "html5", "--wrap=none"],
        input=md, capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"pandoc failed: {r.stderr}")
    return r.stdout


def cover_html():
    return """<div class="cover-page">
    <h1>SCHWEIZ &ndash; <strong>Einb&uuml;rgerungskurs</strong></h1>
    <p><em>SWITZERLAND &ndash; <strong>Naturalisation Course</strong></em></p>
    <br><br>
    <p><strong>swissing &ndash; your local german school</strong></p>
</div>"""


def postprocess(html):
    """Remove pandoc cover block; build food-image grid."""
    # Remove cover
    html = re.sub(
        r'<h1[^>]*>SCHWEIZ\s*.\s*<strong>Einbürgerungskurs</strong></h1>\s*'
        r'<p><em>SWITZERLAND\s*.\s*<strong>Naturalisation Course</strong></em></p>\s*'
        r'<p><strong>swissing[^<]*</strong></p>',
        '', html, count=1, flags=re.DOTALL,
    )

    # Food grid
    tags = []
    for ch in 'abcd':
        pat = rf'<figure>\s*<img[^>]*page-10{ch}\.png[^>]*/?\s*>\s*<figcaption[^>]*>.*?</figcaption>\s*</figure>'
        m2 = re.search(pat, html, re.DOTALL)
        if m2:
            tags.append((m2.start(), m2.end(), m2.group()))
    if len(tags) == 4:
        grid = '<div class="food-grid">\n'
        for _, _, t in tags:
            grid += f'  <div class="food-item">{t}</div>\n'
        grid += '</div>'
        for i in range(3, 0, -1):
            html = html[:tags[i][0]] + html[tags[i][1]:]
        html = html[:tags[0][0]] + grid + html[tags[0][1]:]

    return html


def full_document(body):
    return f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<style>{CSS}</style>
</head><body>
{cover_html()}
{body}
</body></html>"""


def main():
    print("1. Reading markdown …")
    md = read_file(MD_FILE)

    print("2. Preprocessing …")
    md = preprocess(md)

    print("3. Markdown → HTML (pandoc) …")
    body = md_to_html(md)

    print("4. Post-processing …")
    body = postprocess(body)

    print("5. Assembling HTML …")
    html = full_document(body)

    print("6. HTML → PDF (weasyprint) …")
    from weasyprint import HTML
    HTML(string=html, base_url=BASE_DIR).write_pdf(OUTPUT_PDF)

    r = subprocess.run(
        ["mdls", "-name", "kMDItemNumberOfPages", OUTPUT_PDF],
        capture_output=True, text=True,
    )
    print(f"   {r.stdout.strip()}")
    print(f"   → {OUTPUT_PDF}")
    print("Done.")


if __name__ == "__main__":
    main()
