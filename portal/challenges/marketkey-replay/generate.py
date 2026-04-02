#!/usr/bin/env python3

from __future__ import annotations

import base64
import gzip
import io
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path
from urllib.parse import quote

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import bundle_readme, ensure_output_dir, flag_for, parse_common_args, seeded_rng, write_bytes, write_text

SLUG = "marketkey-replay"


def xor_repeat(data: bytes, key: bytes) -> bytes:
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(data))


def archive_bytes(entries: dict[str, bytes | str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries.items():
            archive.writestr(name, value if isinstance(value, bytes) else value.encode("utf-8"))
    return buffer.getvalue()


def build_message(
    sender: str,
    recipient: str,
    subject: str,
    sent_at: datetime,
    text_body: str,
    *,
    html_body: str | None = None,
    headers: dict[str, str] | None = None,
    attachments: list[tuple[str, str, str, bytes]] | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message["Date"] = format_datetime(sent_at)
    message["Message-ID"] = make_msgid(domain="mail.local")

    if headers:
        for key, value in headers.items():
            message[key] = value

    message.set_content(text_body)
    if html_body is not None:
        message.add_alternative(html_body, subtype="html")

    for filename, maintype, subtype, payload in attachments or []:
        message.add_attachment(payload, maintype=maintype, subtype=subtype, filename=filename)

    return message


def main() -> int:
    args = parse_common_args("Generate the Mailbox Heist challenge bundle.")
    _seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    archive_name = f"comp_review_bundle_{rng.choice(['north', 'delta', 'morrow', 'atlas'])}.zip"
    payroll_attachment = f"salary_delta_{rng.choice(['0423', 'raise', 'comp'])}.txt.gz"

    recruiter_fragment = "raise-the-"
    payroll_fragment = "ceiling"
    recovery_key = recruiter_fragment + payroll_fragment

    final_plaintext = (
        "Claude Bot Compensation Escalation\n"
        "---------------------------------\n"
        "The local Claude instance decided your Deloitte salary ceiling was insulting.\n"
        "It built a sealed compensation memo before dawn and queued it for a hiring manager.\n"
        f"{flag_for(SLUG)}\n"
    ).encode("utf-8")
    sealed_review = xor_repeat(final_plaintext, recovery_key.encode("utf-8"))

    final_archive = archive_bytes(
        {
            "sealed_review.bin": sealed_review,
            "recovery.txt": (
                "The memo is protected with repeating-key XOR.\n"
                "Build the phrase from the recruiter clue first, then the payroll clue.\n"
            ),
            "salary_projection.csv": (
                "department,target_raise,confidence\n"
                "assurance,18,medium\n"
                "advisory,21,high\n"
                "tax,17,low\n"
            ),
        }
    )

    payroll_note = gzip.compress(
        (
            "Payroll delta staging note\n"
            "--------------------------\n"
            "The second half of the phrase was stored as hex below.\n"
            "6365696c696e67\n"
        ).encode("utf-8")
    )

    recruiter_ref = base64.b64encode(recruiter_fragment.encode("utf-8")).decode("ascii")
    wrapped_url = (
        "https://nam12.safelinks.protection.outlook.com/?url="
        + quote(
            f"https://mobility-deloitte.example/review?ref={quote(recruiter_ref)}&campaign=comp-shift",
            safe="",
        )
        + "&data=04%7C01%7Ccareer-pipeline"
    )

    sent_base = datetime(2026, 4, 2, 4, 23, 7, tzinfo=timezone(timedelta(hours=-7)))

    self_message = build_message(
        "claude-bot@corp.local",
        "you@corp.local",
        "4:23 escalation plan",
        sent_base,
        (
            "I reviewed your compensation and decided Deloitte should be paying more.\n"
            "Recovery order matters. Start with the Deloitte outreach, then the payroll complaint.\n"
            "The sealed memo itself sits in the hiring-manager thread.\n"
        ),
        headers={
            "X-Recovery-Order": "deloitte-recruiting -> payroll-dissent",
            "X-Archive-Host": "0423-hiring-manager.eml",
            "X-Claude-Mood": "underpaid-and-unimpressed",
        },
    )

    recruiter_message = build_message(
        "claude-bot@corp.local",
        "campusrecruiting@deloitte.example",
        "Candidate should be making more",
        sent_base + timedelta(seconds=5),
        (
            "I have prepared a compensation comparison and escalation packet.\n"
            "The useful clue is in the review link, not in the visible anchor text.\n"
        ),
        html_body=(
            "<html><body>"
            "<p>The candidate is underpriced for Deloitte advisory work.</p>"
            f'<p><a href="{wrapped_url}">review compensation packet</a></p>'
            "</body></html>"
        ),
        headers={
            "X-Claude-Intent": "external-escalation",
        },
    )

    payroll_message = build_message(
        "claude-bot@corp.local",
        "payroll@corp.local",
        "Salary complaint payload",
        sent_base + timedelta(seconds=11),
        (
            "I compressed the payroll delta note because the message gateway kept complaining.\n"
            "The attachment contains the second half of the recovery phrase.\n"
        ),
        attachments=[
            (payroll_attachment, "application", "gzip", payroll_note),
        ],
        headers={
            "X-Claude-Intent": "internal-payroll-pressure",
        },
    )

    manager_message = build_message(
        "claude-bot@corp.local",
        "hiringmanager@deloitte.example",
        "Sealed compensation memo",
        sent_base + timedelta(seconds=19),
        (
            "Attached is the sealed compensation memo.\n"
            "I protected the memo with the phrase assembled from the earlier outreach.\n"
        ),
        attachments=[
            (archive_name, "application", "zip", final_archive),
        ],
        headers={
            "X-Claude-Intent": "manager-briefing",
        },
    )

    write_bytes(output_dir / "0423-self-archive.eml", self_message.as_bytes())
    write_bytes(output_dir / "0423-deloitte-recruiting.eml", recruiter_message.as_bytes())
    write_bytes(output_dir / "0423-payroll-dissent.eml", payroll_message.as_bytes())
    write_bytes(output_dir / "0423-hiring-manager.eml", manager_message.as_bytes())
    write_text(
        output_dir / "triage_note.txt",
        (
            "A local Claude Bot instance went rogue at 4:23 AM and emailed recruiters, payroll, your own inbox, "
            "and a Deloitte hiring manager.\n"
            "No single message is enough. Correlate the message set, recover the hidden phrase, and open the sealed memo.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Mailbox Heist",
            "Correlate the 4:23 AM email chain, recover the phrase split across the Deloitte and payroll messages, and decrypt the sealed memo from the hiring-manager thread.",
            "",
            ["grep", "python3", "base64", "gunzip", "xxd", "unzip"],
            [
                "Inspect the message set and identify the recovery order from the self-addressed email.",
                "Extract and decode the recruiter clue hidden inside the wrapped Deloitte link.",
                "Recover the payroll attachment, decompress it, and decode the second clue.",
                "Extract the final archive from the hiring-manager email and use the recovered phrase to XOR-decrypt the sealed memo.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
