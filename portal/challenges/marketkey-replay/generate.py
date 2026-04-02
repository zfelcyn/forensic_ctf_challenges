#!/usr/bin/env python3

from __future__ import annotations

import sys
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, parse_common_args, seeded_rng, write_bytes, write_text, zip_bytes

SLUG = "marketkey-replay"


def main() -> int:
    args = parse_common_args("Generate the Mailbox Heist challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    attachment_name = f"invoice_bundle_{seed[:4]}.zip"
    eml_name = f"target_{seed[:4]}.eml"
    sender = rng.choice(["billing@northline-support.com", "notices@glass-audit.net", "ops@heliogrid-mail.com"])
    recipient = rng.choice(["ap@company.example", "records@company.example", "finance@company.example"])
    subject = rng.choice(["Outstanding vendor packet", "Updated invoice archive", "Resent vendor attachment"])

    attachment_bytes = zip_bytes(
        {
            "records/reply_draft.txt": (
                "Attachment recovery\n"
                "-------------------\n"
                f"{flag_for(SLUG)}\n"
            ),
            "records/mailflow.log": f"message-seed={seed}\nstatus=queued\n",
        }
    )

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="inbound.local")
    message.set_content(
        "Please review the attached vendor packet before end of day.\n"
        "The previous attachment was recalled by gateway policy, so I resent it as a bundled archive.\n"
    )
    message.add_alternative(
        "<html><body><p>Please review the attached vendor packet before end of day.</p>"
        "<p>The previous attachment was recalled by gateway policy, so I resent it as a bundled archive.</p>"
        "</body></html>",
        subtype="html",
    )
    message.add_attachment(attachment_bytes, maintype="application", subtype="zip", filename=attachment_name)

    write_bytes(output_dir / eml_name, message.as_bytes())
    write_text(
        output_dir / "triage_note.txt",
        (
            "The sender claims the real document was bundled to get around a mail gateway problem.\n"
            "Extract the attachment from the message source and inspect the recovered archive.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Mailbox Heist",
            "Recover the archived attachment from the EML and inspect its contents without relying on a mail client GUI.",
            seed,
            ["python3", "base64", "grep", "unzip"],
            [
                "Inspect the EML structure and locate the attachment payload.",
                "Recover the ZIP attachment from the MIME message.",
                "Extract the archived files and inspect the recovered draft.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
