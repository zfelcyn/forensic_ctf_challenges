#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, parse_common_args, poster_image_bytes, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "carbon-offset"


def main() -> int:
    args = parse_common_args("Generate the Carbon Offset challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    project_code = rng.choice(["glass-harbor", "night-garden", "amber-lift", "silent-dune"])
    photo_name = f"retreat_photo_{project_code}_{seed[:4]}.jpg"
    accent = rng.choice([(181, 242, 73), (120, 208, 255), (255, 182, 90)])
    base = rng.choice([(34, 39, 46), (28, 34, 40), (36, 32, 44)])

    hidden_note = (
        "Recovered note\n"
        "--------------\n"
        "The chat export was scrubbed, but the staged image still carried the confession.\n"
        f"{flag_for(SLUG)}\n"
    )
    hidden_archive = zip_bytes(
        {
            "evidence/recovered_note.txt": hidden_note,
            "evidence/camera_roll.log": "transfer complete\nsource=conference-share\nstatus=archived\n",
        }
    )

    image_bytes = poster_image_bytes(1280, 720, base, accent, f"Project {project_code}", "JPEG")
    write_bytes(output_dir / photo_name, image_bytes + hidden_archive)
    write_text(
        output_dir / "briefing.txt",
        (
            "A departing analyst sent one final retreat photo before their laptop was taken.\n"
            "The image renders normally, but the file size does not line up with what the photo should contain.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Carbon Offset",
            "Inspect the JPEG structure and recover the hidden payload appended after the real image footer.",
            seed,
            ["xxd", "binwalk", "dd", "unzip"],
            [
                "Inspect the end of the JPEG and confirm where the legitimate image data stops.",
                "Carve the appended payload into a separate file.",
                "Identify the carved object and extract the recovered note.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
