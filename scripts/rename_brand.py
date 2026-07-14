from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_BRAND = "Calc" + "Smart"
NEW_BRAND = "TrueCalco"
TEXT_EXTENSIONS = {".html", ".js", ".json", ".md", ".py", ".txt", ".xml"}

changed = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
        continue
    if path == Path(__file__).resolve() or ".git" in path.parts:
        continue
    source = path.read_text(encoding="utf-8")
    updated = source.replace(OLD_BRAND, NEW_BRAND)
    if updated != source:
        path.write_text(updated, encoding="utf-8")
        changed.append(path.relative_to(ROOT))

print(f"Renamed {OLD_BRAND} to {NEW_BRAND} in {len(changed)} files.")
