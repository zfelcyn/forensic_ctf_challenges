#!/usr/bin/env python3

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import random
import secrets
import socket
import struct
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

FLAG_DATA = {
    "carbon-offset": {
        "key": 37,
        "data": [99, 105, 100, 98, 94, 82, 86, 80, 122, 67, 87, 68, 81, 73, 64, 68, 65, 64, 87, 122, 70, 74, 75, 67, 76, 87, 72, 64, 65, 88],
    },
    "ledger-burn": {
        "key": 58,
        "data": [124, 118, 123, 125, 65, 86, 95, 94, 93, 95, 72, 101, 88, 79, 72, 84, 101, 91, 72, 89, 82, 83, 76, 95, 101, 78, 91, 83, 86, 71],
    },
    "template-bleed": {
        "key": 91,
        "data": [29, 23, 26, 28, 32, 47, 62, 54, 43, 55, 58, 47, 62, 4, 57, 55, 62, 62, 63, 4, 54, 62, 63, 50, 58, 4, 55, 62, 58, 48, 38],
    },
    "graveyard-transfer": {
        "key": 17,
        "data": [87, 93, 80, 86, 106, 118, 99, 112, 103, 116, 104, 112, 99, 117, 78, 101, 99, 112, 127, 98, 119, 116, 99, 78, 99, 116, 114, 126, 103, 116, 99, 116, 117, 108],
    },
    "marketkey-replay": {
        "key": 77,
        "data": [11, 1, 12, 10, 54, 32, 44, 36, 33, 47, 34, 53, 18, 44, 57, 57, 44, 46, 37, 32, 40, 35, 57, 18, 63, 40, 46, 34, 59, 40, 63, 40, 41, 48],
    },
}


def flag_for(challenge_id: str) -> str:
    secret = FLAG_DATA[challenge_id]
    key = secret["key"]
    return "".join(chr(value ^ key) for value in secret["data"])


def manifest_digest_for(challenge_id: str) -> str:
    return hashlib.sha256(flag_for(challenge_id).encode("utf-8")).hexdigest()


def parse_common_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output-dir", required=True, help="Directory to write generated challenge files into.")
    parser.add_argument("--seed", default=None, help="Optional bundle seed.")
    return parser.parse_args()


def seeded_rng(seed_text: str | None) -> tuple[str, random.Random]:
    seed = seed_text or secrets.token_hex(4)
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return seed, random.Random(int(digest[:16], 16))


def ensure_output_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def zip_bytes(entries: dict[str, str | bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries.items():
            archive.writestr(name, value if isinstance(value, bytes) else value.encode("utf-8"))
    return buffer.getvalue()


def gzip_bytes(text: str) -> bytes:
    return gzip.compress(text.encode("utf-8"))


def bundle_readme(title: str, summary: str, seed: str, tools: list[str], steps: list[str]) -> str:
    step_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    tool_line = ", ".join(tools)
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n\n"
        f"{summary}\n\n"
        f"Recommended tools: {tool_line}\n\n"
        f"Suggested workflow:\n{step_lines}\n"
    )


def poster_image_bytes(width: int, height: int, base_color: tuple[int, int, int], accent_color: tuple[int, int, int], label: str, fmt: str) -> bytes:
    image = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(image)

    for offset in range(0, height, 24):
        draw.line((0, offset, width, offset), fill=accent_color, width=1)
    for offset in range(0, width, 48):
        draw.line((offset, 0, offset, height), fill=(base_color[0] + 12, base_color[1] + 12, base_color[2] + 12), width=1)

    draw.rectangle((64, 64, width - 64, height - 64), outline=accent_color, width=4)
    draw.text((96, 96), label, fill=accent_color)
    draw.text((96, height - 140), "Internal use only", fill=(220, 220, 220))
    draw.text((96, height - 100), "Recovered from a seized workstation", fill=(220, 220, 220))

    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def minimal_docx(document_text: str, media_name: str, media_bytes: bytes) -> bytes:
    entries = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
""",
        "word/document.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>{document_text}</w:t></w:r></w:p>
    <w:p><w:r><w:t>See the embedded chart for the redacted timeline.</w:t></w:r></w:p>
    <w:p><w:r><w:drawing/></w:r></w:p>
    <w:sectPr/>
  </w:body>
</w:document>
""",
        "word/_rels/document.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>
</Relationships>
""",
        f"word/media/{media_name}": media_bytes,
    }
    return zip_bytes(entries)


def ip_to_bytes(ip: str) -> bytes:
    return socket.inet_aton(ip)


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    total = (total >> 16) + (total & 0xFFFF)
    total += total >> 16
    return (~total) & 0xFFFF


def tcp_frame(
    src_mac: bytes,
    dst_mac: bytes,
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    seq: int,
    ack: int,
    flags: int,
    payload: bytes = b"",
) -> bytes:
    ethernet = dst_mac + src_mac + struct.pack("!H", 0x0800)

    total_length = 20 + 20 + len(payload)
    ip_header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        total_length,
        0,
        0x4000,
        64,
        6,
        0,
        ip_to_bytes(src_ip),
        ip_to_bytes(dst_ip),
    )
    ip_header = ip_header[:10] + struct.pack("!H", checksum(ip_header)) + ip_header[12:]

    offset_reserved_flags = (5 << 12) | flags
    tcp_header = struct.pack("!HHLLHHHH", src_port, dst_port, seq, ack, offset_reserved_flags, 65535, 0, 0)
    pseudo_header = struct.pack(
        "!4s4sBBH",
        ip_to_bytes(src_ip),
        ip_to_bytes(dst_ip),
        0,
        6,
        len(tcp_header) + len(payload),
    )
    tcp_checksum = checksum(pseudo_header + tcp_header + payload)
    tcp_header = struct.pack("!HHLLHHHH", src_port, dst_port, seq, ack, offset_reserved_flags, 65535, tcp_checksum, 0)
    return ethernet + ip_header + tcp_header + payload


class TcpConversation:
    def __init__(
        self,
        packets: list[tuple[float, bytes]],
        client_ip: str,
        server_ip: str,
        client_port: int,
        server_port: int,
        rng: random.Random,
        timestamp_start: float,
        src_mac: bytes,
        dst_mac: bytes,
    ) -> None:
        self.packets = packets
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.client_port = client_port
        self.server_port = server_port
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.timestamp = timestamp_start
        self.client_seq = rng.randrange(100000, 800000)
        self.server_seq = rng.randrange(200000, 900000)
        self._handshake()

    def _append(self, frame: bytes, delta: float = 0.06) -> None:
        self.timestamp += delta
        self.packets.append((self.timestamp, frame))

    def _handshake(self) -> None:
        syn = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq, 0, 0x02)
        self._append(syn)
        syn_ack = tcp_frame(self.dst_mac, self.src_mac, self.server_ip, self.client_ip, self.server_port, self.client_port, self.server_seq, self.client_seq + 1, 0x12)
        self._append(syn_ack)
        ack = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq + 1, self.server_seq + 1, 0x10)
        self._append(ack)
        self.client_seq += 1
        self.server_seq += 1

    def client_send(self, payload: bytes) -> None:
        frame = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq, self.server_seq, 0x18, payload)
        self._append(frame)
        self.client_seq += len(payload)
        ack = tcp_frame(self.dst_mac, self.src_mac, self.server_ip, self.client_ip, self.server_port, self.client_port, self.server_seq, self.client_seq, 0x10)
        self._append(ack)

    def server_send(self, payload: bytes, chunk_size: int = 0) -> None:
        if chunk_size and len(payload) > chunk_size:
            for index in range(0, len(payload), chunk_size):
                self.server_send(payload[index:index + chunk_size], chunk_size=0)
            return

        frame = tcp_frame(self.dst_mac, self.src_mac, self.server_ip, self.client_ip, self.server_port, self.client_port, self.server_seq, self.client_seq, 0x18, payload)
        self._append(frame)
        self.server_seq += len(payload)
        ack = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq, self.server_seq, 0x10)
        self._append(ack)

    def close(self) -> None:
        fin = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq, self.server_seq, 0x11)
        self._append(fin)
        self.client_seq += 1
        fin_ack = tcp_frame(self.dst_mac, self.src_mac, self.server_ip, self.client_ip, self.server_port, self.client_port, self.server_seq, self.client_seq, 0x11)
        self._append(fin_ack)
        self.server_seq += 1
        last_ack = tcp_frame(self.src_mac, self.dst_mac, self.client_ip, self.server_ip, self.client_port, self.server_port, self.client_seq, self.server_seq, 0x10)
        self._append(last_ack)


def pcap_bytes(packets: list[tuple[float, bytes]]) -> bytes:
    buffer = io.BytesIO()
    buffer.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for timestamp, frame in packets:
        seconds = int(timestamp)
        microseconds = int((timestamp - seconds) * 1_000_000)
        buffer.write(struct.pack("<IIII", seconds, microseconds, len(frame), len(frame)))
        buffer.write(frame)
    return buffer.getvalue()


def ftp_retr_pcap(zip_name: str, zip_payload: bytes, username: str, password: str, rng: random.Random) -> bytes:
    packets: list[tuple[float, bytes]] = []
    src_mac = b"\x00\x16\x3e\x10\x13\x37"
    dst_mac = b"\x00\x16\x3e\x20\x21\x42"
    client_ip = "10.13.37.10"
    server_ip = "10.13.37.20"
    control_port = rng.randrange(41000, 43000)
    data_client_port = rng.randrange(43001, 45000)
    data_server_port = rng.randrange(50000, 52000)

    control = TcpConversation(packets, client_ip, server_ip, control_port, 21, rng, 1712058000.0, src_mac, dst_mac)
    control.server_send(b"220 secure-archive FTP service ready\r\n")
    control.client_send(f"USER {username}\r\n".encode("utf-8"))
    control.server_send(b"331 Password required\r\n")
    control.client_send(f"PASS {password}\r\n".encode("utf-8"))
    control.server_send(b"230 User logged in\r\n")
    control.client_send(b"TYPE I\r\n")
    control.server_send(b"200 Type set to I\r\n")
    control.client_send(b"PASV\r\n")
    high, low = divmod(data_server_port, 256)
    control.server_send(f"227 Entering Passive Mode (10,13,37,20,{high},{low})\r\n".encode("utf-8"))
    control.client_send(f"RETR {zip_name}\r\n".encode("utf-8"))
    control.server_send(b"150 Opening BINARY mode data connection\r\n")

    data_stream = TcpConversation(packets, client_ip, server_ip, data_client_port, data_server_port, rng, control.timestamp + 0.2, src_mac, dst_mac)
    data_stream.server_send(zip_payload, chunk_size=240)
    data_stream.close()

    control.server_send(b"226 Transfer complete\r\n")
    control.close()
    return pcap_bytes(packets)
