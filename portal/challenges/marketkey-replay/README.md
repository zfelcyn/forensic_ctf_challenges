# Mailbox Heist

## Concept
Student-facing email forensics challenge where solvers recover a ZIP attachment from a raw `.eml` artifact.

## Intended Solver Path
1. Inspect the raw email structure.
2. Recover the archived attachment from the MIME message.
3. Extract the attachment and inspect the recovered draft.

## Suggested Student Files
- `target_<seed>.eml`
- `triage_note.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
