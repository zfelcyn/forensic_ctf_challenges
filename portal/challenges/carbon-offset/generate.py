#!/usr/bin/env python3

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, parse_common_args, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "carbon-offset"
ASSET_PATH = Path(__file__).resolve().parent / "assets" / "clav.jpg"


def jpeg_from_asset() -> bytes:
    with Image.open(ASSET_PATH) as image:
        converted = image.convert("RGB")
        buffer = io.BytesIO()
        converted.save(buffer, format="JPEG", quality=92, optimize=True)
    return buffer.getvalue()


def main() -> int:
    args = parse_common_args("Generate the Carbon Offset challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    capture_tag = rng.choice(["kick", "stream", "vod", "clip"])
    photo_name = f"clav_stream_capture_{capture_tag}_{seed[:4]}.jpg"

    hidden_note = (
        "Recovered note\n"
        "--------------\n"
        "Clavicular got frame mogged on stream, but the real damage was in the bytes tacked onto the image.\n"
        "ASU Frat Leader left the evidence in the upload instead of the chat log.\n"
        f"{flag_for(SLUG)}\n"
    )
    hidden_archive = zip_bytes(
        {
            "evidence/mog_report.txt": hidden_note,
            "evidence/stream_notes.txt": (
                "source=kick-export\n"
                "clip_status=normal_render\n"
                "review_hint=check_after_real_jpeg_footer\n"
            ),
        }
    )

    image_bytes = jpeg_from_asset()
    write_bytes(output_dir / photo_name, image_bytes + hidden_archive)
    write_text(
        output_dir / "briefing.txt",
        (
            "The photo of Clav and ASU Frat Leader looks normal from a Kick stream capture.\n"
            "Clavicular got brutally frame mogged, but someone also hid extra bytes after the real JPEG image data.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Carbon Offset",
            "Inspect the stream capture JPEG and recover the hidden payload appended after the real image footer.",
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
