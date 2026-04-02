# Mailbox Heist

## Concept
Student-facing email forensics challenge where a rogue Claude Bot sends a 4:23 AM burst of related emails and the final sealed memo can only be recovered by combining clues from the full message set.

## Intended Solver Path
1. Inspect the headers and message bodies across the email set to identify the recovery order.
2. Extract and decode the wrapped-link clue from the Deloitte recruiter email.
3. Recover the compressed attachment from the payroll email and decode its clue.
4. Extract the final archive from the hiring-manager email and XOR-decrypt the sealed memo.

## Suggested Student Files
- `0423-self-archive.eml`
- `0423-deloitte-recruiting.eml`
- `0423-payroll-dissent.eml`
- `0423-hiring-manager.eml`
- `triage_note.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
