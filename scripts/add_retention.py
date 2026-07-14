from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script src="retention.js" defer></script>'
changed = []

for path in [*sorted(ROOT.glob("*.html")), ROOT / "scripts" / "generate_expansion.py"]:
    source = path.read_text(encoding="utf-8")
    if SCRIPT_TAG in source or "</body>" not in source:
        continue
    path.write_text(source.replace("</body>", SCRIPT_TAG + "</body>"), encoding="utf-8")
    changed.append(path.relative_to(ROOT))

print(f"Enabled private saved tools and bookmark guidance on {len(changed)} files.")
