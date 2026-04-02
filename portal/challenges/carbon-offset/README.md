# Carbon Offset

## Concept
Student-facing steganography challenge based on a normal-looking JPEG with appended hidden data.

## Intended Solver Path
1. Inspect the file tail.
2. Confirm the real JPEG footer.
3. Recover the appended payload and extract the flag.

## Suggested Student Files
- `retreat_photo_<seed>.jpg`
- `briefing.txt`

## Generator
Run `generate.py` to create the solver bundle for this challenge.
