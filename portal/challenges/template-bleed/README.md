# Template Bleed

## Concept
Student-facing Office document challenge where a mall incident packet still leaks draft evidence about a Jamba Juice and Cinnabon rivalry.

## Intended Solver Path
1. Treat the DOCX as a ZIP container.
2. Inspect package folders under `word/`, especially `word/media`.
3. Recover the hidden promo-board asset and extract the appended archive containing the flag.

## Suggested Student Files
- `food_court_incident_<seed>.docx`
- `mall_briefing.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
