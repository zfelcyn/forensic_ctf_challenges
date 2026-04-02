#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, minimal_docx, parse_common_args, poster_image_bytes, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "template-bleed"


def main() -> int:
    args = parse_common_args("Generate the Template Bleed challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    doc_name = f"performance_review_{seed[:4]}.docx"
    media_name = f"chart_{rng.choice(['alpha', 'bravo', 'charlie', 'delta'])}.png"
    document_text = f"Performance review export {seed[:6]} prepared for legal hold."
    inner_note = (
        "Embedded revision note\n"
        "----------------------\n"
        "The final export still carried a draft image artifact from the original case folder.\n"
        f"{flag_for(SLUG)}\n"
    )
    hidden_archive = zip_bytes(
        {
            "redactions/revision_note.txt": inner_note,
            "redactions/chain_of_custody.txt": "owner=hr-intake\nstatus=removed-from-final-draft\n",
        }
    )
    media_bytes = poster_image_bytes(1024, 640, (44, 52, 63), (181, 242, 73), "Disciplinary Timeline", "PNG") + hidden_archive
    write_bytes(output_dir / doc_name, minimal_docx(document_text, media_name, media_bytes))
    write_text(
        output_dir / "case_summary.txt",
        (
            "HR claims the evidence was removed before distribution.\n"
            "Treat the DOCX as a package and inspect the embedded media before assuming the export is clean.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Template Bleed",
            "Unpack the DOCX, inspect its package contents, and recover the hidden payload from the embedded media file.",
            seed,
            ["unzip", "find", "xxd", "binwalk"],
            [
                "Unzip the DOCX to inspect the internal package structure.",
                "Look under word/media for a suspicious embedded asset.",
                "Inspect the asset bytes and carve the appended archive.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
