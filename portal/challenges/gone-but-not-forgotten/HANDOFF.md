# Gone But Not Forgotten Handoff

Scope: This challenge is fully self-contained in this folder.

Current State:
1. `assets/laptop.img` is a 50 MB disk image.
2. The flag is recoverable from deleted content inside the image.
3. `generate.py` copies the image into the solver bundle and adds a short orientation note.

Implement Next:
1. Add richer decoy files and directory structure to make the image feel more realistic.
2. Expand `solution/` with step-by-step recovery notes for `strings`, Foremost, and Autopsy.
3. Keep the flag recoverable without requiring unsupported portal-side services.

Do Not Do Yet:
1. Do not expose the flag in plaintext anywhere outside the disk image.
2. Do not make the challenge depend on another folder or external service.
