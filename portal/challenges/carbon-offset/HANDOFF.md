# Carbon Offset Handoff

Scope: Implement only this folder.

Build target:
1. Generate one believable JPEG.
2. Append a hidden compressed payload after the real JPEG end marker.
3. Keep the solve path focused on byte inspection and carving, not image-viewer tricks.

Keep unchanged:
- `challenge.json` id and folder name
- Portal-wide frontend files
