#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, parse_common_args, seeded_rng, write_text


def main() -> int:
    args = parse_common_args("Generate the template challenge bundle.")
    seed, _rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Template Challenge",
            "Replace this generator with a real challenge bundle writer.",
            seed,
            ["tool1", "tool2"],
            [
                "Write the solver-facing files into the provided output directory.",
                "Keep the real flag out of plaintext portal assets.",
                "Update the challenge metadata to match the generated files.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
