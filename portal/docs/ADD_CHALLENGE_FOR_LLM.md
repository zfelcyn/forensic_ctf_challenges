# Add A Challenge To The Portal

## Goal
Add one self-contained challenge folder under `portal/challenges/` so the portal can list it without hand-editing frontend code.

## Required Folder Layout
```text
portal/challenges/<slug>/
  challenge.json
  generate.py
  README.md
  HANDOFF.md
  assets/
  solution/
  deploy/
```

## Rules
1. Keep the challenge self-contained. Do not make one challenge depend on another challenge folder.
2. Put any source assets used by the generator in `assets/`.
3. Put internal solution notes in `solution/`.
4. Put service-specific Docker files in `deploy/` only if the challenge needs a running container.
5. `generate.py` must create the solver-facing files inside the provided output directory.
6. Do not edit frontend source to register the challenge. The registry script discovers folders automatically.

## Required `challenge.json` Fields
```json
{
  "id": "unique-slug",
  "sortOrder": 10,
  "title": "Challenge Title",
  "status": "concept",
  "category": "Steganography",
  "difficulty": "Medium",
  "points": 200,
  "summary": "One sentence for the catalog card.",
  "scenario": "Two to four sentences describing the challenge story and expected investigation path.",
  "recommendedTools": ["tool1", "tool2"],
  "learningObjectives": ["objective 1", "objective 2"],
  "artifacts": [
    {
      "name": "artifact-name",
      "purpose": "Why the artifact exists"
    }
  ],
  "hints": ["hint 1", "hint 2"],
  "sourceNotes": ["Notes_CyberForensics/path/to/note.md"],
  "deployment": {
    "kind": "file-drop",
    "composeFile": null,
    "launchUrl": null
  },
  "flagValidation": {
    "sha256": "paste-the-64-character-sha256-digest-here"
  },
  "llmHandoff": {
    "scope": "What another model is allowed to change inside this folder.",
    "implementNext": "What should be built next inside this folder.",
    "doNotDoYet": "What should stay untouched or deferred."
  }
}
```

## Process
1. Copy `portal/challenges/_template/` to `portal/challenges/<slug>/`.
2. Fill in `challenge.json`.
3. Implement `generate.py` so it writes only solver-facing files to the provided output directory.
4. Replace placeholder text in `README.md` and `HANDOFF.md`.
5. Add source assets, solution notes, and optional deploy files inside that same folder.
6. Generate the flag digest with `python3 portal/scripts/hash_flag.py 'FLAG{example}'`.
7. Paste the digest into `challenge.json`.
8. Run `python3 portal/scripts/build_registry.py`.
9. Rebuild or restart the portal with `docker compose up --build`.

## Frontend Behavior
- The portal reads only `portal/public/data/challenges.json`.
- That file is generated from the challenge folders.
- If the new challenge has a valid `challenge.json`, it will appear automatically after the registry is rebuilt.
- Solved state is stored in browser local storage. Points unlock when the submitted flag hash matches `flagValidation.sha256`.
- Download links call the server-side generator for that challenge and return a ZIP built from the generator output.

## If Handing One Challenge To Another LLM
Give it only:
1. `portal/challenges/<slug>/`
2. `portal/docs/ADD_CHALLENGE_FOR_LLM.md`

That is the full local context it needs.
