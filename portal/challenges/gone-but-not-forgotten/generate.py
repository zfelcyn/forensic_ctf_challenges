#!/usr/bin/env python3

from __future__ import annotations

import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, parse_common_args, seeded_rng, write_text

ASSETS_DIRECTORY = Path(__file__).resolve().parent / "assets"

def main() -> int:
    args = parse_common_args("Generate the GBNF bundle.")
    seed, _rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Gone But Not Forgotten",
            "Recover the deleted note hidden inside the disk image and extract the flag it contains.",
            seed,
            ["strings", "foremost", "Autopsy"],
            [
                "Start with quick triage against the raw image.",
                "Inspect deleted content or carve recoverable files from the image.",
                "Open the recovered note and submit the flag.",
            ],
        ),
    )

    shutil.copy(ASSETS_DIRECTORY / "laptop.img", output_dir / "laptop.img")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
