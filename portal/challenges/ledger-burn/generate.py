#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, gzip_bytes, parse_common_args, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "ledger-burn"


def main() -> int:
    args = parse_common_args("Generate the Ledger Burn challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    archive_name = f"quarter_close_{rng.choice(['north', 'echo', 'delta', 'mosaic'])}_{seed[:4]}.zip"
    quarter = rng.choice(["Q1", "Q2", "Q3", "Q4"])
    visible_archive = zip_bytes(
        {
            "finance/summary.csv": (
                "account,amount,status\n"
                f"payroll-hold,14220,review\n"
                f"vendor-credit,9820,approved\n"
                f"{quarter}-close,55120,archived\n"
            ),
            "finance/review_notes.txt": (
                "Archive copied before workstation reset.\n"
                "Any material outside the official ZIP end marker should be treated as suspect.\n"
            ),
        }
    )
    hidden_gzip = gzip_bytes(
        "{\n"
        '  "recovered": true,\n'
        '  "source": "manual append",\n'
        f'  "flag": "{flag_for(SLUG)}"\n'
        "}\n"
    )

    write_bytes(output_dir / archive_name, visible_archive + hidden_gzip)
    write_text(
        output_dir / "audit_note.txt",
        (
            "The archive opens, but its byte length is larger than the ZIP metadata says it should be.\n"
            "Use the real end-of-central-directory offset as your carve point.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Ledger Burn",
            "Compare the ZIP metadata to the raw file length and recover the appended payload after the real archive footer.",
            seed,
            ["zipinfo", "dd", "file", "gunzip"],
            [
                "Inspect the ZIP archive metadata to determine where the archive really ends.",
                "Carve everything after that offset into a separate file.",
                "Identify the carved file type and decompress it.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
