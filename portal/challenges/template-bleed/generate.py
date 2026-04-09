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

    doc_name = f"food_court_incident_{seed[:4]}.docx"
    media_name = f"promo_board_{rng.choice(['mango', 'cinnamon', 'smoothie', 'pretzel'])}.png"
    document_text = (
        f"Southpoint Mall incident packet {seed[:6]} prepared for tenant-relations review. "
        "Complaint references Kyan Kotschevar-Smead (Jamba Juice) and James Richards-Perhatch (Cinnabon)."
    )
    inner_note = (
        "Embedded draft complaint\n"
        "------------------------\n"
        "Kyan says James keeps stepping into the Jamba line, redirecting customers, and trying to make the smoothie bar look slow.\n"
        "Mall management cut this accusation from the final packet, but the old promo board still carries the draft archive.\n"
        f"{flag_for(SLUG)}\n"
    )
    hidden_archive = zip_bytes(
        {
            "drafts/kyan_statement.txt": inner_note,
            "drafts/mall_ops_log.txt": (
                "owner=mall-ops\n"
                "status=removed-from-final-tenant-packet\n"
                "stores=Jamba Juice,Cinnabon\n"
            ),
        }
    )
    media_bytes = poster_image_bytes(1024, 640, (64, 40, 24), (255, 188, 67), "Food Court Traffic", "PNG") + hidden_archive
    write_bytes(output_dir / doc_name, minimal_docx(document_text, media_name, media_bytes))
    write_text(
        output_dir / "mall_briefing.txt",
        (
            "Mall management says the final incident packet was scrubbed before it went to tenants.\n"
            "Kyan Kotschevar-Smead from Jamba Juice insists an earlier draft still described how James Richards-Perhatch from Cinnabon was sabotaging orders and stealing customers.\n"
            "Treat the DOCX as a package and inspect embedded media before assuming the export is clean.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Template Bleed",
            "Unpack the mall incident DOCX, inspect its package contents, and recover the hidden draft payload from the embedded media file.",
            seed,
            ["unzip", "find", "xxd", "binwalk"],
            [
                "Unzip the DOCX to inspect the internal package structure.",
                "Check `word/media` for the promo-board image bundled with the complaint packet.",
                "Inspect that asset's bytes and carve the appended archive.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
