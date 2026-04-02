# Template Bleed

## Concept
Student-facing Office document challenge where embedded package contents still leak the evidence.

## Intended Solver Path
1. Treat the DOCX as a ZIP container.
2. Inspect package folders under `word/`.
3. Recover the hidden media object and extract the flag.

## Suggested Student Files
- `performance_review_<seed>.docx`
- `case_summary.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
