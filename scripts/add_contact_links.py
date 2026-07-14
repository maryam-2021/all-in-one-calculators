from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTACT_LINK = '<li><a href="contact">Contact</a></li>'
PRIVACY_LINK = '<li><a href="privacy">Privacy</a></li>'

changed = []
for path in [*sorted(ROOT.glob("*.html")), ROOT / "scripts" / "generate_expansion.py"]:
    source = path.read_text(encoding="utf-8")
    if CONTACT_LINK in source or PRIVACY_LINK not in source:
        continue
    updated = source.replace(PRIVACY_LINK, CONTACT_LINK + PRIVACY_LINK)
    path.write_text(updated, encoding="utf-8")
    changed.append(path.relative_to(ROOT))

print(f"Added the Contact footer link to {len(changed)} files.")
