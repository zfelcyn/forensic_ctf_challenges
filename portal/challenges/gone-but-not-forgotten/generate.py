#!/usr/bin/env python3

from __future__ import annotations

import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, parse_common_args, seeded_rng, write_text

ASSETS_DIRECTORY = Path(__file__).resolve().parent/"assets"

def main() -> int:
    args = parse_common_args("Generate the GBNF bundle.")
    seed, _rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    # README_FIRST.txt
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Gone but not forgotten",
            "Browse the files within the disk image to find a secret file someone tried to delete.",
            seed,
            ["strings"],
            [
                "Open the file using Autopsy",
                "Browse the recovered files.",
                "I get the secret back.",
            ],
        ),
    )


    # Add disk image
    shutil.copy(
        ASSETS_DIRECTORY / "laptop.img",
        output_dir / "laptop.img"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
