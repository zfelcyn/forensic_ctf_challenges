# Ledger Burn

## Concept
Student-facing archive challenge where a valid ZIP hides a second payload after its official end.

## Intended Solver Path
1. Inspect ZIP metadata.
2. Compare the reported end of archive to the real file size.
3. Carve the appended object and recover the flag.

## Suggested Student Files
- `quarter_close_<seed>.zip`
- `audit_note.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
