#!/usr/bin/env python3

from __future__ import annotations

import argparse
import io
import json
import secrets
import subprocess
import tempfile
import zipfile
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
CHALLENGES_DIR = ROOT / "challenges"
REGISTRY_FILE = PUBLIC_DIR / "data" / "challenges.json"


def load_registry() -> dict:
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def zip_directory(directory: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(directory).as_posix())
    return buffer.getvalue()


class PortalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self) -> None:
        parsed = urlparse(self.path)
        if not (parsed.path.startswith("/api/challenges/") and parsed.path.endswith("/download")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/challenges/") and parsed.path.endswith("/download"):
            self.handle_download(parsed)
            return

        if parsed.path == "/healthz":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        super().do_GET()

    def handle_download(self, parsed) -> None:
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 4:
            self.send_error(HTTPStatus.NOT_FOUND, "Challenge download path not found")
            return

        challenge_id = parts[2]
        registry = load_registry()
        challenge = next((item for item in registry["challenges"] if item["id"] == challenge_id), None)
        if challenge is None:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown challenge")
            return

        query = parse_qs(parsed.query)
        seed = query.get("seed", [secrets.token_hex(4)])[0]
        generator_script = CHALLENGES_DIR / challenge_id / "generate.py"

        with tempfile.TemporaryDirectory(prefix=f"{challenge_id}-") as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            output_dir = temp_dir / "bundle"
            output_dir.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                [
                    "python3",
                    str(generator_script),
                    "--output-dir",
                    str(output_dir),
                    "--seed",
                    seed,
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                message = result.stderr or result.stdout or "Challenge generation failed."
                self.wfile.write(message.encode("utf-8", errors="replace"))
                return

            payload = zip_directory(output_dir)

        filename = f"{challenge_id}-{seed}.zip"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the forensic CTF portal.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), PortalHandler)
    print(f"Serving portal on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
