from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script src="share-links.js" defer></script>'

changed = []
targets = [*sorted(ROOT.glob("*.html")), ROOT / "scripts" / "generate_expansion.py"]
for path in targets:
    source = path.read_text(encoding="utf-8")
    if 'class="calc-form"' not in source or SCRIPT_TAG in source:
        continue
    if "</body>" not in source:
        raise RuntimeError(f"No closing body tag in {path.relative_to(ROOT)}")
    updated = source.replace("</body>", SCRIPT_TAG + "</body>")
    path.write_text(updated, encoding="utf-8")
    changed.append(path.relative_to(ROOT))

print(f"Enabled shareable URLs on {len(changed)} files.")
