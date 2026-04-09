#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHALLENGES_DIR = ROOT / "challenges"
OUTPUT_FILE = ROOT / "public" / "data" / "challenges.json"

REQUIRED_FIELDS = (
    "id",
    "title",
    "status",
    "category",
    "difficulty",
    "points",
    "summary",
    "scenario",
    "recommendedTools",
    "learningObjectives",
    "artifacts",
    "hints",
    "sourceNotes",
    "deployment",
    "flagValidation",
)

DIFFICULTY_STARS = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
    "Bonus": 4,
}

VALID_STATUSES = {
    "concept",
    "draft",
    "ready",
    "live",
    "archived",
}


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise ValueError(f"{path}: missing required fields: {', '.join(missing)}")

    difficulty = data["difficulty"]
    if difficulty not in DIFFICULTY_STARS:
        raise ValueError(f"{path}: invalid difficulty '{difficulty}'")

    status = data["status"]
    if status not in VALID_STATUSES:
        raise ValueError(f"{path}: invalid status '{status}'")

    challenge_id = data["id"]
    folder_name = path.parent.name
    if challenge_id != folder_name:
        raise ValueError(
            f"{path}: id '{challenge_id}' must match challenge folder name '{folder_name}'"
        )

    points = data["points"]
    if not isinstance(points, int) or points <= 0:
        raise ValueError(f"{path}: points must be a positive integer")

    validation = data["flagValidation"]
    if not isinstance(validation, dict):
        raise ValueError(f"{path}: flagValidation must be an object")

    digest = validation.get("sha256", "")
    if not isinstance(digest, str) or len(digest) != 64 or any(
        char not in "0123456789abcdef" for char in digest
    ):
        raise ValueError(f"{path}: flagValidation.sha256 must be a 64-character lowercase hex digest")

    generator_script = path.parent / "generate.py"
    if not generator_script.exists():
        raise ValueError(f"{path}: missing generator script at {generator_script}")

    data["difficultyStars"] = DIFFICULTY_STARS[difficulty]
    data["paths"] = {
        "folder": path.parent.relative_to(ROOT).as_posix(),
        "manifest": path.relative_to(ROOT).as_posix(),
        "generator": generator_script.relative_to(ROOT).as_posix(),
    }
    data["downloadPath"] = f"/api/challenges/{data['id']}/download"
    return data


def build_registry() -> dict[str, Any]:
    challenges: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for manifest_path in sorted(CHALLENGES_DIR.glob("*/challenge.json")):
        if manifest_path.parent.name.startswith("_"):
            continue

        challenge = load_manifest(manifest_path)
        challenge_id = challenge["id"]
        if challenge_id in seen_ids:
            raise ValueError(f"Duplicate challenge id found: {challenge_id}")
        seen_ids.add(challenge_id)
        challenges.append(challenge)

    challenges.sort(key=lambda item: (item.get("sortOrder", 9999), item["title"].lower()))

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "challengeCount": len(challenges),
        "categories": sorted({item["category"] for item in challenges}),
        "challenges": challenges,
    }


def main() -> int:
    registry = build_registry()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {registry['challengeCount']} challenges to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
