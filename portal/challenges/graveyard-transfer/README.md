# Deceitful Transfer

## Concept
Student-facing network challenge where a private investigator captures a suspicious FTP session and the useful evidence is spread across multiple recovered transfers.

## Intended Solver Path
1. Inspect the FTP control stream and map the passive-mode data channels.
2. Recover the transferred receipts file and identify which image matters.
3. Reconstruct the suspicious JPEG.
4. Inspect the JPEG footer and carve the hidden appended archive.
5. Open the archive and recover the final evidence note.

## Suggested Student Files
- `deceitful_transfer_<seed>.pcap`
- `incident_memo.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
