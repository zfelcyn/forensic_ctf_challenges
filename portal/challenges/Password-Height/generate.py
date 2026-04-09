#!/usr/bin/env python3

from __future__ import annotations

import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, parse_common_args, seeded_rng, write_text

ASSETS_DIRECTORY = Path(__file__).resolve().parent / "assets"


def main() -> int:
    args = parse_common_args("Generate the Password-Height bundle.")
    seed, _rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Password-Height",
            "Recover the cropped password from the JPEG and submit the resulting flag.",
            seed,
            ["Hex editor", "ExifTool", "xxd"],
            [
                "Inspect the JPEG metadata and structure before changing anything.",
                "Compare the stored image dimensions against what the file actually contains.",
                "Restore the hidden portion of the image to recover the password.",
            ],
        ),
    )

    shutil.copy(ASSETS_DIRECTORY / "heightLimit.jpg", output_dir / "heightLimit.jpg")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
