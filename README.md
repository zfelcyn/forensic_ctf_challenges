# forensic_ctf_challenges

Creating Capture The Flag (CTF) challenges for classmates in CPTS 425.

## Portal

Run the portal:

```bash
docker compose up --build
```

Open `http://localhost:8080`.

Add or swap challenges under `portal/challenges/`, then rebuild the registry:

```bash
python3 portal/scripts/build_registry.py
docker compose up --build
```

Downloadable challenge bundles are generated on demand by each challenge folder's `generate.py`.

Challenge handoff instructions live in `portal/docs/ADD_CHALLENGE_FOR_LLM.md`.
