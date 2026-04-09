## Team Hackstreet Boys: Group 1

Members:
- Zachary Felcyn
- Kyan Kotschevar-Smead
- Noah Manuel
- James Richards-Perhatch

# forensic_ctf_challenges

Creating Capture The Flag (CTF) challenges for classmates in CPTS 425.

## Portal

Run the portal:

```bash
docker compose up -d --build
```

Open `http://localhost:8080`.

When you're done, stop it with:

```bash
docker compose down
```

Add or swap challenges under `portal/challenges/`, then rebuild the registry:

```bash
python3 portal/scripts/build_registry.py
docker compose up -d --build
```

Downloadable challenge bundles are generated on demand by each challenge folder's `generate.py`.
