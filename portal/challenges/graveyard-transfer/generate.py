#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, ftp_retr_pcap, parse_common_args, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "graveyard-transfer"


def main() -> int:
    args = parse_common_args("Generate the Graveyard Transfer challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    drop_name = f"handoff_{rng.choice(['delta', 'orchid', 'cipher', 'morrow'])}_{seed[:4]}.zip"
    username = rng.choice(["buildsvc", "nightops", "deploy", "archive"])
    password = rng.choice(["Lantern7!", "coldstorage!", "northwind!", "relay@night"])

    transferred_archive = zip_bytes(
        {
            "drop/session_note.txt": (
                "Recovered transfer note\n"
                "-----------------------\n"
                f"{flag_for(SLUG)}\n"
            ),
            "drop/inventory.log": f"batch={seed[:6]}\nmode=pasv\nstatus=complete\n",
        }
    )

    pcap_name = f"graveyard_transfer_{seed[:4]}.pcap"
    write_bytes(output_dir / pcap_name, ftp_retr_pcap(drop_name, transferred_archive, username, password, rng))
    write_text(
        output_dir / "incident_memo.txt",
        (
            "A contractor said they only moved harmless maintenance logs during the graveyard shift.\n"
            "The capture includes both control traffic and a separate passive-mode data connection.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Graveyard Transfer",
            "Use Wireshark to reconstruct the transferred object from the FTP data channel, then inspect the recovered archive.",
            seed,
            ["Wireshark", "Follow TCP Stream", "Export", "unzip"],
            [
                "Identify the passive-mode data connection associated with the FTP retrieval.",
                "Reconstruct the transferred file from the data stream.",
                "Extract the recovered archive and inspect the transferred note.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
