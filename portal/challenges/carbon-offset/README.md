# Carbon Offset

## Concept
Student-facing steganography challenge based on a Kick stream capture of Clav and ASU Frat Leader with appended hidden data.

## Intended Solver Path
1. Inspect the file tail.
2. Confirm the real JPEG footer.
3. Recover the appended payload and extract the flag.

## Suggested Student Files
- `clav_stream_capture_<seed>.jpg`
- `briefing.txt`

## Generator
`generate.py` converts the provided `assets/clav.jpg` source image into a real JPEG, appends a hidden ZIP payload, and writes the solver bundle.
