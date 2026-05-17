# Zürich GKT Trainer

A bilingual (German / English) study companion for the **Grundkenntnistest (GKT)** — the basic-knowledge test required for naturalisation in the Canton of Zürich.

The project bundles two things:

1. A **single-file web app** with 271 multiple-choice questions across the five official GKT categories.
2. A set of **bilingual study materials** (Markdown + PDF) generated from the original German course PDFs, with side-by-side English translations, vocabulary tables, and practice questions for the interview.

## Try it

Open [`zurich-gkt-trainer.html`](./zurich-gkt-trainer.html) directly in a browser — no build step, no server, no dependencies. `index.html` redirects to it for static hosting (e.g. GitHub Pages).

## Features

### Quiz app

- **271 questions** in five categories:
  1. Staat und Politik (State and Politics)
  2. Sozialstaat und Zivilgesellschaft (Social State and Civil Society)
  3. Geschichte (History)
  4. Geografie (Geography)
  5. Kultur und Alltagskultur (Culture and Everyday Culture)
- Filter by **category** or **subcategory** (Bund / Kanton / Gemeinde), or run **all questions** at once.
- Optional **shuffle**.
- Every question and every answer option is shown in **German with an English subtitle**, and key vocabulary is highlighted inline.
- Score summary at the end.
- Pure HTML/CSS/JS — works offline, mobile-friendly.

### Course materials

Located in [`course-material/`](./course-material/), generated from the originals in `course-material-originals/`:

| File | What it is |
|---|---|
| `einbuergerungskurs-2026.md` | Full course text, German with inline English translations |
| `einbuergerungskurs-2026-study.md` | Study edition: each page gets a facing page with vocab tables (nouns / adjectives / verbs), practice interview questions, and a notes area |
| `einbuergerungskurs-2026-bilingual.html` / `.pdf` | Rendered study edition — German in black, English in blue, highlighted key terms |
| `der-bund-kurz-erklaert.md`, `heks-echo-2023-arbeitsblaetter.md`, `lesematerial-kanton-zuerich-und-waedenswil.md`, etc. | Additional bilingual references |

## Repository layout

```
zurich-gkt-trainer.html        # the quiz app (single file, 271 questions embedded)
index.html                     # redirect → zurich-gkt-trainer.html
course-material/               # bilingual Markdown + generated HTML/PDF
course-material-originals/     # original German PDFs (source-of-truth)
images/                        # images extracted from the source PDFs
scripts/
  build-study-edition.py       # injects vocab + practice pages into the markdown
  generate-pdf.py              # renders the study edition to bilingual HTML/PDF
```

## Regenerating the study PDF

The two scripts in `scripts/` are stand-alone and chain together:

```bash
python3 scripts/build-study-edition.py   # einbuergerungskurs-2026.md → -study.md
python3 scripts/generate-pdf.py          # -study.md → bilingual .html + .pdf
```

`generate-pdf.py` shells out to **pandoc** (markdown → HTML) and uses **weasyprint** (HTML → PDF), so both need to be installed:

```bash
brew install pandoc
pip install weasyprint
```

## About the test

The GKT is the written part of the naturalisation procedure in the Canton of Zürich. It covers Swiss federal, cantonal and municipal institutions, history, geography, and everyday culture. This repo is an unofficial study aid — the authoritative materials are the PDFs in `course-material-originals/`.
