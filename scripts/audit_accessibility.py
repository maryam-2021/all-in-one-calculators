from html.parser import HTMLParser
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.labels = set()
        self.controls = []
        self.bad_images = 0
        self.bad_click_targets = 0
        self.in_button = False
        self.button_attrs = {}
        self.button_text = []
        self.unnamed_buttons = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "label" and values.get("for"):
            self.labels.add(values["for"])
        if tag in {"input", "select", "textarea"} and values.get("type") != "hidden":
            self.controls.append((tag, values))
        if tag == "img" and "alt" not in values:
            self.bad_images += 1
        if tag in {"div", "span", "li", "img"} and "onclick" in values:
            self.bad_click_targets += 1
        if tag == "button":
            self.in_button = True
            self.button_attrs = values
            self.button_text = []

    def handle_data(self, data):
        if self.in_button:
            self.button_text.append(data)

    def handle_endtag(self, tag):
        if tag == "button" and self.in_button:
            name = " ".join(self.button_text).strip() or self.button_attrs.get("aria-label") or self.button_attrs.get("title")
            if not name:
                self.unnamed_buttons += 1
            self.in_button = False


errors = []
htmls = sorted(ROOT.glob("*.html"))
for path in htmls:
    source = path.read_text(encoding="utf-8")
    parser = AuditParser()
    parser.feed(source)
    if '<html' not in source or not re.search(r'<html\b[^>]*\blang="[^"]+"', source, re.I):
        errors.append(f"{path.name}: missing document language")
    if 'class="skip-link"' not in source or 'id="main-content"' not in source:
        errors.append(f"{path.name}: missing skip link or main target")
    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        errors.append(f"{path.name}: duplicate IDs {', '.join(duplicates)}")
    for tag, attrs in parser.controls:
        control_id = attrs.get("id")
        if not control_id:
            errors.append(f"{path.name}: {tag} has no ID")
        elif control_id not in parser.labels:
            errors.append(f"{path.name}: {tag}#{control_id} has no explicit label")
    if parser.bad_images:
        errors.append(f"{path.name}: {parser.bad_images} images lack alt text")
    if parser.bad_click_targets:
        errors.append(f"{path.name}: {parser.bad_click_targets} non-semantic click targets")
    if parser.unnamed_buttons:
        errors.append(f"{path.name}: {parser.unnamed_buttons} buttons lack accessible names")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
for token in (":focus-visible", "prefers-reduced-motion", ".sr-only"):
    if token not in css:
        errors.append(f"styles.css: missing {token} accessibility rule")

if errors:
    print("ACCESSIBILITY AUDIT FAILED")
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(htmls)} pages have explicit labels, skip navigation, semantic controls, named buttons, image alternatives, and keyboard focus foundations.")
