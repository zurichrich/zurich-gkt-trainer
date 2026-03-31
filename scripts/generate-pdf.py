#!/usr/bin/env python3
"""Generate bilingual PDF from the study edition markdown.

Uses pandoc for markdown→HTML conversion and weasyprint for HTML→PDF.

Features:
- German text in black (#222), English translations in blue (#2255aa)
- English paragraphs get a blue left border
- Bold terms highlighted with yellow (DE) or blue (EN) background
- Study pages styled with grey background and card layout
"""

import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_FILE = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026-study.md")
OUTPUT_PDF = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026-bilingual.pdf")
IMAGES_DIR = os.path.join(BASE_DIR, "images", "einbuergerungskurs-2026")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = r"""
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @bottom-right {
        content: counter(page);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #cc0000;
        font-weight: bold;
    }
}

@page cover {
    margin: 0;
    @bottom-right { content: none; }
}

@page study {
    background-color: #f8f8f8;
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 9pt;
    line-height: 1.45;
    color: #222;
    font-weight: 400;
}

/* ═══ Cover ═══ */
.cover-page {
    page: cover;
    background-color: #cc0000;
    color: white;
    text-align: center;
    padding-top: 8cm;
    height: 297mm;
    width: 210mm;
    box-sizing: border-box;
    page-break-after: always;
}
.cover-page h1 {
    font-size: 32pt; color: white; border-bottom: none;
    margin: 0 0 0.3em 0;
}
.cover-page p { font-size: 14pt; color: white; margin: 0.3em 0; }
.cover-page em { color: rgba(255,255,255,0.85); font-style: italic; }

/* ═══ Page breaks ═══ */
.page-break {
    break-before: page;
    page-break-before: always;
}

/* ═══ Headings ═══ */
h1 {
    font-size: 14pt; color: #cc0000;
    border-bottom: 2pt solid #cc0000; padding-bottom: 3pt;
    margin: 12pt 0 6pt 0;
    page-break-after: avoid;
}
h2 {
    font-size: 11pt; color: #cc0000;
    margin: 10pt 0 4pt 0; page-break-after: avoid;
}
h3 {
    font-size: 10pt; color: #333;
    margin: 8pt 0 3pt 0; page-break-after: avoid;
}
h4 {
    font-size: 9pt; color: #cc0000;
    margin: 6pt 0 3pt 0;
}

hr { border: none; border-top: 2pt solid #cc0000; margin: 10pt 0; }

/* ═══ German text (default) ═══ */
p {
    margin: 4pt 0 8pt 0;
    font-weight: 450;
}
strong {
    font-weight: 800;
    color: #000;
    background-color: #fff3cd;
    padding: 0 2pt;
}
ul, ol { margin: 3pt 0 6pt 16pt; padding: 0; }
li { margin-bottom: 2pt; }

/* ═══ English translations - Option A ═══ */
p.en {
    color: #2255aa;
    font-weight: 400;
}
p.en em {
    font-style: normal;
    color: #2255aa;
}
p.en strong, p.en em strong {
    color: #1a3d7a;
    font-weight: 700;
    background-color: #dde8f8;
    padding: 0 2pt;
}
li.en {
    color: #2255aa;
    font-weight: 400;
}
li.en em {
    font-style: normal;
    color: #2255aa;
}
li.en strong {
    color: #1a3d7a;
    font-weight: 700;
    background-color: #dde8f8;
}

/* ═══ Images ═══ */
img {
    max-width: 45%;
    height: auto;
    display: block;
    margin: 6pt auto;
}
figure { margin: 6pt 0; }
figcaption {
    font-size: 7pt; color: #777; text-align: center; margin-top: 2pt;
}

/* Party logos - small */
img[src*="page-23"], img[src*="page-24"], img[src*="page-25"] {
    max-width: 12%;
}
/* Full-width tables/charts */
img[src*="page-18"], img[src*="page-20"], img[src*="page-22"],
img[src*="page-16b"] {
    max-width: 80%;
}
/* Bundesrat group photo */
img[src*="page-21"] {
    max-width: 65%;
}
/* Tax map, vote results */
img[src*="page-35"], img[src*="page-31"] {
    max-width: 55%;
}
/* Insurance cartoons side by side */
img[src*="page-36"] {
    max-width: 40%;
    display: inline-block;
}
/* 3-pillar and social insurance diagrams */
img[src*="page-37"], img[src*="page-38"], img[src*="page-39"] {
    max-width: 55%;
}
/* Artists collage */
img[src*="page-12"] {
    max-width: 60%;
}
/* Architecture */
img[src*="page-11"] {
    max-width: 50%;
}
/* Schellen-Ursli */
img[src*="page-09"] {
    max-width: 30%;
}
/* Food images */
img[src*="page-10"] {
    max-width: 25%;
    display: inline-block;
}

/* ═══ Study pages ═══ */
.study-page {
    page: study;
    background-color: #f5f5f5;
    padding: 12pt;
    border-radius: 4pt;
}
.study-page blockquote {
    margin: 0 0 8pt 0;
    padding: 8pt 12pt;
    border-left: none;
    background: white;
    border-radius: 3pt;
    border: 1pt solid #e0e0e0;
}
.study-page blockquote h3 {
    color: white;
    font-size: 11pt;
    margin: -8pt -12pt 8pt -12pt;
    background-color: #cc0000;
    padding: 4pt 8pt;
    border-radius: 2pt;
}
.study-page blockquote h4 {
    color: #cc0000;
    font-size: 9pt;
    margin: 4pt 0 4pt 0;
    border-bottom: 1pt solid #eee;
    padding-bottom: 2pt;
}
.study-page table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin: 4pt 0;
}
.study-page th {
    background-color: #f0f0f0;
    font-weight: 600;
    text-align: left;
    padding: 3pt 6pt;
    border: 1pt solid #ddd;
}
.study-page td {
    padding: 2pt 6pt;
    border: 1pt solid #ddd;
}
.study-page td:first-child {
    font-weight: 600;
    color: #222;
}
.study-page td:last-child {
    color: #2255aa;
}
/* Question styling */
.study-page blockquote strong {
    background: none;
    color: #222;
}
.study-page blockquote em {
    font-style: italic;
    color: #2255aa;
}

/* ═══ Note lines in study pages ═══ */
.note-line {
    display: block;
    border-bottom: 1pt dotted #bbb;
    height: 20pt;
    margin: 2pt 0;
}

/* ═══ Tables in content ═══ */
table { width: 100%; border-collapse: collapse; margin: 6pt 0; font-size: 8pt; }
th, td { border: 1px solid #ccc; padding: 2pt 6pt; text-align: left; }
th { background-color: #f0f0f0; font-weight: 600; }
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def preprocess_md(md):
    """Fix image paths, convert page markers to page breaks, fix note lines."""
    # Replace relative image paths with absolute file:// paths
    md = md.replace(
        "../images/einbuergerungskurs-2026/",
        f"file://{IMAGES_DIR}/",
    )

    # Convert note underscores to HTML spans (pandoc turns ___ into <hr>)
    md = re.sub(
        r'^> _{10,}',
        r'> <span class="note-line">&nbsp;</span>',
        md, flags=re.MULTILINE,
    )

    # Convert <!-- Page X --> to page break divs
    lines = md.split("\n")
    out = []
    for line in lines:
        m = re.match(r"^\s*<!--\s*Page\s+(\d+)\s*-->\s*$", line)
        if m:
            pn = int(m.group(1))
            if pn == 1:
                continue
            out.append(f'<div class="page-break" id="page-{pn}"></div>')
        else:
            out.append(line)
    return "\n".join(out)


def md_to_html(md):
    """Use pandoc to convert markdown to HTML5."""
    r = subprocess.run(
        ["pandoc", "--from", "markdown", "--to", "html5", "--wrap=none"],
        input=md, capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"pandoc failed: {r.stderr}")
    return r.stdout


def mark_english_paragraphs(html):
    """Add class='en' to paragraphs that are full English translations.

    A paragraph is an English translation if the <p> tag's entire content
    is wrapped in <em>...</em> (possibly containing <strong> inside).
    Same for <li> elements.
    """
    # Match <p> whose entire content is <em>...</em>
    # Use a pattern that handles nested tags inside <em>
    html = re.sub(
        r"<p>(\s*<em>(?:(?!</em>).)*</em>\s*)</p>",
        r'<p class="en">\1</p>',
        html,
        flags=re.DOTALL,
    )
    # Match <li> whose entire content is <em>...</em>
    html = re.sub(
        r"<li>(\s*<em>(?:(?!</em>).)*</em>\s*)</li>",
        r'<li class="en">\1</li>',
        html,
        flags=re.DOTALL,
    )
    return html


def wrap_study_pages(html):
    """Wrap blockquote sections containing study page markers in a study-page div.

    In the HTML, study pages appear as a sequence of <blockquote> elements
    between two <hr /> tags. The first blockquote contains an h3 with
    'Lernseite' in it.
    """
    # Pattern: <hr /> followed by one or more <blockquote>s (the first
    # containing "Lernseite"), ending at the next <hr /> or end of content.
    # We wrap the blockquotes in <div class="study-page">.
    pattern = (
        r"(<hr\s*/?>)"                         # opening <hr>
        r"(\s*"                                 # whitespace
        r"<blockquote>\s*<h3[^>]*>.*?Lernseite.*?</h3>"  # first blockquote with Lernseite
        r".*?"                                  # rest of blockquotes
        r")"                                    # end capture
        r"(?=<hr\s*/?>|<div\s+class=\"page-break\")"  # lookahead: next hr or page-break
    )

    def wrap_match(m):
        return m.group(1) + '\n<div class="study-page">\n' + m.group(2) + "\n</div>\n"

    html = re.sub(pattern, wrap_match, html, flags=re.DOTALL)
    return html


def remove_pandoc_cover(html):
    """Remove the cover text that pandoc generates (we add our own)."""
    html = re.sub(
        r"<h1[^>]*>SCHWEIZ\s*.\s*<strong>Einb(?:ü|&uuml;)rgerungskurs</strong></h1>\s*"
        r"<p[^>]*>.*?Naturalisation Course.*?</p>\s*"
        r"<p[^>]*><strong>swissing[^<]*</strong></p>",
        "",
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def clean_blank_pages(html):
    """Remove consecutive <hr> tags and empty divs that cause blank pages."""
    # Collapse multiple consecutive <hr> into one
    html = re.sub(r'(<hr\s*/?>)\s*(<hr\s*/?>)+', r'\1', html)
    # Remove <hr> immediately before or after a page-break div
    html = re.sub(r'<hr\s*/?>\s*(<div[^>]*class="page-break")', r'\1', html)
    html = re.sub(r'(</div>)\s*<hr\s*/?>\s*(<div[^>]*class="page-break")', r'\1\n\2', html)
    # Remove <hr> immediately before or after study-page div
    html = re.sub(r'<hr\s*/?>\s*(<div[^>]*class="study-page")', r'\1', html)
    html = re.sub(r'(</div><!-- end study -->)\s*<hr\s*/?>', r'\1', html)
    return html


def cover_html():
    return """<div class="cover-page">
    <h1>SCHWEIZ<br><strong>Einb&uuml;rgerungskurs</strong></h1>
    <p><em>SWITZERLAND &mdash; Naturalisation Course</em></p>
    <br><br><br>
    <p style="font-size:16pt;"><strong>swissing</strong></p>
    <p style="font-size:11pt;">your local german school</p>
</div>"""


def full_document(body, css):
    return f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<style>{css}</style>
</head><body>
{cover_html()}
{body}
</body></html>"""


def main():
    print("1. Reading study edition markdown...")
    md = read_file(MD_FILE)

    print("2. Preprocessing...")
    md = preprocess_md(md)

    print("3. Converting markdown -> HTML (pandoc)...")
    body = md_to_html(md)

    print("4. Post-processing HTML...")
    body = remove_pandoc_cover(body)
    body = mark_english_paragraphs(body)
    body = wrap_study_pages(body)
    body = clean_blank_pages(body)

    print("5. Assembling document...")
    html = full_document(body, CSS)

    # Write HTML for debugging
    html_path = OUTPUT_PDF.replace(".pdf", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   HTML written to {html_path}")

    print("6. Generating PDF (weasyprint)...")
    from weasyprint import HTML as WeasyprintHTML

    WeasyprintHTML(string=html, base_url=BASE_DIR).write_pdf(OUTPUT_PDF)

    # Check file size
    size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"   File size: {size_mb:.1f} MB")

    # Check page count
    r = subprocess.run(
        ["mdls", "-name", "kMDItemNumberOfPages", OUTPUT_PDF],
        capture_output=True,
        text=True,
    )
    print(f"   {r.stdout.strip()}")
    print(f"   -> {OUTPUT_PDF}")
    print("Done.")


if __name__ == "__main__":
    main()
