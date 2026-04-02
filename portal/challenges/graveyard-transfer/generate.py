#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

from challenge_utils import (
    TcpConversation,
    bundle_readme,
    ensure_output_dir,
    flag_for,
    parse_common_args,
    pcap_bytes,
    poster_image_bytes,
    seeded_rng,
    write_bytes,
    write_text,
    zip_bytes,
)

SLUG = "graveyard-transfer"


def run_pasv_transfer(
    control: TcpConversation,
    packets: list[tuple[float, bytes]],
    *,
    client_ip: str,
    server_ip: str,
    src_mac: bytes,
    dst_mac: bytes,
    rng,
    command: str,
    payload: bytes,
    response_line: bytes,
    chunk_size: int,
) -> None:
    data_client_port = rng.randrange(43001, 45000)
    data_server_port = rng.randrange(50000, 52000)

    control.client_send(b"PASV\r\n")
    high, low = divmod(data_server_port, 256)
    control.server_send(f"227 Entering Passive Mode (10,13,37,44,{high},{low})\r\n".encode("utf-8"))
    control.client_send(f"{command}\r\n".encode("utf-8"))
    control.server_send(response_line)

    data_stream = TcpConversation(
        packets,
        client_ip,
        server_ip,
        data_client_port,
        data_server_port,
        rng,
        control.timestamp + 0.2,
        src_mac,
        dst_mac,
    )
    data_stream.server_send(payload, chunk_size=chunk_size)
    data_stream.close()
    control.timestamp = max(control.timestamp, data_stream.timestamp + 0.05)
    control.server_send(b"226 Transfer complete\r\n")


def main() -> int:
    args = parse_common_args("Generate the Deceitful Transfer challenge bundle.")
    seed, rng = seeded_rng(args.seed)
    output_dir = ensure_output_dir(args.output_dir)

    src_mac = b"\x00\x16\x3e\x10\x13\x37"
    dst_mac = b"\x00\x16\x3e\x20\x21\x42"
    client_ip = "10.13.37.18"
    server_ip = "10.13.37.44"
    control_port = rng.randrange(41000, 43000)

    username = rng.choice(["michael", "m.smith", "husband", "homeoffice"])
    password = rng.choice(["p@tioSunset7", "northfence!", "fidelity?", "latepass_23"])

    decoy_name = f"family_trip_{rng.choice(['beach', 'cabin', 'orchid'])}.jpg"
    receipts_name = f"of_receipts_{rng.choice(['q1', 'march', '0423'])}.csv"
    stash_name = f"candids_{rng.choice(['0423', 'late', 'mirror'])}.jpg"
    pcap_name = f"deceitful_transfer_{seed[:4]}.pcap"

    decoy_photo = poster_image_bytes(1280, 720, (34, 42, 48), (122, 181, 255), "Family Trip", "JPEG")

    hidden_archive = zip_bytes(
        {
            "evidence/private_note.txt": (
                "Recovered private note\n"
                "----------------------\n"
                "The PI was right. The hidden gallery was being mirrored through FTP.\n"
                f"{flag_for(SLUG)}\n"
            ),
            "evidence/onlyfans_spend.csv": (
                "date,merchant,amount,category\n"
                "2026-03-17,OF*CREATORPASS,299.00,subscription\n"
                "2026-03-24,OF*TIPBUNDLE,425.00,tip\n"
                "2026-03-31,OF*LOCKEDSET,615.00,content\n"
            ),
        }
    )
    stash_photo = (
        poster_image_bytes(1280, 720, (37, 33, 44), (255, 129, 163), "Candids 04:23", "JPEG")
        + hidden_archive
    )

    receipts_csv = (
        "date,merchant,amount,note\n"
        "2026-03-17,OF*CREATORPASS,299.00,subscription renewed\n"
        "2026-03-24,OF*TIPBUNDLE,425.00,tip package unlocked\n"
        f"2026-03-31,OF*LOCKEDSET,615.00,mirror target={stash_name}\n"
        "2026-04-01,FTP-VPS-HOST,18.00,photo sync endpoint\n"
    ).encode("utf-8")

    listing = (
        "drwxr-xr-x    2 1000     1000         4096 Apr 02 04:20 archives\r\n"
        f"-rw-r--r--    1 1000     1000        {len(decoy_photo):5d} Apr 02 04:21 {decoy_name}\r\n"
        f"-rw-r--r--    1 1000     1000        {len(receipts_csv):5d} Apr 02 04:22 {receipts_name}\r\n"
        f"-rw-r--r--    1 1000     1000        {len(stash_photo):5d} Apr 02 04:23 {stash_name}\r\n"
    ).encode("utf-8")

    packets: list[tuple[float, bytes]] = []
    control = TcpConversation(packets, client_ip, server_ip, control_port, 21, rng, 1712056930.0, src_mac, dst_mac)
    control.server_send(b"220 residence FTP gateway ready\r\n")
    control.client_send(f"USER {username}\r\n".encode("utf-8"))
    control.server_send(b"331 Password required\r\n")
    control.client_send(f"PASS {password}\r\n".encode("utf-8"))
    control.server_send(b"230 User logged in\r\n")
    control.client_send(b"SYST\r\n")
    control.server_send(b"215 UNIX Type: L8\r\n")
    control.client_send(b"PWD\r\n")
    control.server_send(b'257 "/vault/private" is the current directory\r\n')
    control.client_send(b"TYPE A\r\n")
    control.server_send(b"200 Type set to A\r\n")

    run_pasv_transfer(
        control,
        packets,
        client_ip=client_ip,
        server_ip=server_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        rng=rng,
        command="LIST",
        payload=listing,
        response_line=b"150 Opening ASCII mode data connection for file list\r\n",
        chunk_size=180,
    )

    control.client_send(b"TYPE I\r\n")
    control.server_send(b"200 Type set to I\r\n")

    run_pasv_transfer(
        control,
        packets,
        client_ip=client_ip,
        server_ip=server_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        rng=rng,
        command=f"RETR {decoy_name}",
        payload=decoy_photo,
        response_line=b"150 Opening BINARY mode data connection\r\n",
        chunk_size=256,
    )

    run_pasv_transfer(
        control,
        packets,
        client_ip=client_ip,
        server_ip=server_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        rng=rng,
        command=f"RETR {receipts_name}",
        payload=receipts_csv,
        response_line=b"150 Opening BINARY mode data connection\r\n",
        chunk_size=160,
    )

    run_pasv_transfer(
        control,
        packets,
        client_ip=client_ip,
        server_ip=server_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        rng=rng,
        command=f"RETR {stash_name}",
        payload=stash_photo,
        response_line=b"150 Opening BINARY mode data connection\r\n",
        chunk_size=256,
    )

    control.client_send(b"QUIT\r\n")
    control.server_send(b"221 Goodbye\r\n")
    control.close()

    write_bytes(output_dir / pcap_name, pcap_bytes(packets))
    write_text(
        output_dir / "incident_memo.txt",
        (
            "You are a private investigator. A woman hired you because she believes her husband has been unfaithful, "
            "has spent thousands on OnlyFans, and has been stashing pictures through plain FTP.\n"
            "You parked outside the house, captured this traffic, and need to determine what he was really retrieving.\n"
        ),
    )
    write_text(
        output_dir / "README_FIRST.txt",
        bundle_readme(
            "Deceitful Transfer",
            "Use Wireshark to map the passive-mode FTP transfers, reconstruct the right files, and inspect the suspicious JPEG for hidden appended data.",
            seed,
            ["Wireshark", "Follow TCP Stream", "xxd", "binwalk", "unzip"],
            [
                "Inspect the FTP control stream to identify the directory listing and file retrieval order.",
                "Recover the receipts file and determine which image matters.",
                "Reconstruct the suspicious JPEG from its passive data stream.",
                "Inspect the recovered JPEG tail and extract the hidden appended archive.",
                "Open the hidden archive and inspect the recovered evidence files.",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
