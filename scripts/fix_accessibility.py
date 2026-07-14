from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script src="accessibility.js" defer></script>'
SKIP_LINK = '<a class="skip-link" href="#main-content">Skip to main content</a>'
changed = []

for path in [*sorted(ROOT.glob("*.html")), ROOT / "scripts" / "generate_expansion.py"]:
    source = path.read_text(encoding="utf-8")
    original = source

    if SCRIPT_TAG not in source and "</body>" in source:
        source = source.replace("</body>", SCRIPT_TAG + "</body>")

    if path.suffix == ".html" and SKIP_LINK not in source:
        source = re.sub(r"(<body\b[^>]*>)", r"\1" + SKIP_LINK, source, count=1, flags=re.IGNORECASE)

    if path.suffix == ".html" and 'id="main-content"' not in source:
        if re.search(r"<main\b", source, re.IGNORECASE):
            source = re.sub(r"<main\b", '<main id="main-content" tabindex="-1"', source, count=1, flags=re.IGNORECASE)
        else:
            source, count = re.subn(
                r'<(div|article)\s+class="([^"]*(?:calc-page|category-page|article-page)[^"]*)"',
                r'<\1 class="\2" id="main-content" role="main" tabindex="-1"',
                source,
                count=1,
                flags=re.IGNORECASE,
            )
            if count != 1:
                nav_end = source.lower().find("</nav>")
                if nav_end >= 0:
                    remainder = source[nav_end:]
                    updated, count = re.subn(
                        r'<div\s+class="site-wrapper"',
                        '<div class="site-wrapper" id="main-content" role="main" tabindex="-1"',
                        remainder,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    source = source[:nav_end] + updated
                if count != 1:
                    raise RuntimeError(f"Could not add a main-content target to {path.name}")

    if path.suffix == ".html" and 'id="globalSearch"' in source and 'for="globalSearch"' not in source:
        source = re.sub(
            r'(<input\b[^>]*\bid="globalSearch"[^>]*>)',
            r'<label class="sr-only" for="globalSearch">Search calculators</label>\1',
            source,
            count=1,
            flags=re.IGNORECASE,
        )

    if path.suffix == ".html" and '<div class="faq-item">' not in source and 'class="faq-question"' in source:
        source = re.sub(
            r'(<button\s+class="faq-question">.*?</button>\s*<div\s+class="faq-answer"><div\s+class="faq-answer-inner">.*?</div></div>)',
            r'<div class="faq-item">\1</div>',
            source,
            flags=re.IGNORECASE | re.DOTALL,
        )

    if path.name == "password-generator.html":
        source = source.replace('<label><input type="checkbox" id="symbols"', '<label for="symbols"><input type="checkbox" id="symbols"', 1)

    if path.name == "time-calculator.html":
        source = source.replace(
            '<div class="tc-tabs">\n        <div class="tc-tab active" onclick="showTab(0)">Add/Subtract</div>\n        <div class="tc-tab" onclick="showTab(1)">Time from Date</div>\n        <div class="tc-tab" onclick="showTab(2)">Expression</div>\n      </div>',
            '<div class="tc-tabs" role="tablist" aria-label="Time calculator modes">\n        <button type="button" id="timeTab0" class="tc-tab active" role="tab" aria-selected="true" aria-controls="panel0" onclick="showTab(0)">Add/Subtract</button>\n        <button type="button" id="timeTab1" class="tc-tab" role="tab" aria-selected="false" aria-controls="panel1" onclick="showTab(1)">Time from Date</button>\n        <button type="button" id="timeTab2" class="tc-tab" role="tab" aria-selected="false" aria-controls="panel2" onclick="showTab(2)">Expression</button>\n      </div>',
            1,
        )
        source = source.replace('<div id="panel0" class="tc-panel active">', '<div id="panel0" class="tc-panel active" role="tabpanel" aria-labelledby="timeTab0">', 1)
        source = source.replace('<div id="panel1" class="tc-panel">', '<div id="panel1" class="tc-panel" role="tabpanel" aria-labelledby="timeTab1" hidden>', 1)
        source = source.replace('<div id="panel2" class="tc-panel">', '<div id="panel2" class="tc-panel" role="tabpanel" aria-labelledby="timeTab2" hidden>', 1)
        for control_id, label in {
            "td1":"Days", "th1":"Hours", "tm1":"Mins", "ts1":"Secs",
            "td2":"Days", "th2":"Hours", "tm2":"Mins", "ts2":"Secs",
            "tdd":"Days", "tdh":"Hours", "tdm":"Mins", "tds":"Secs",
            "tDateTimeStart":"Start Date & Time", "topDate":"Operation", "tExprInput":"Expression (e.g. 1d 2h + 30m - 5s)",
        }.items():
            source = source.replace(f'<label>{label}</label>', f'<label for="{control_id}">{label}</label>', 1)
        source = source.replace('<select id="top1"', '<label class="sr-only" for="top1">Operation</label><select id="top1"', 1)
        source = source.replace(
            "document.querySelectorAll('.tc-tab').forEach((t, i) => t.classList.toggle('active', i === n));",
            "document.querySelectorAll('.tc-tab').forEach((t, i) => { const active=i===n; t.classList.toggle('active', active); t.setAttribute('aria-selected', String(active)); });",
            1,
        )
        source = source.replace(
            "document.querySelectorAll('.tc-panel').forEach((p, i) => p.classList.toggle('active', i === n));",
            "document.querySelectorAll('.tc-panel').forEach((p, i) => { const active=i===n; p.classList.toggle('active', active); p.hidden=!active; });",
            1,
        )

    if path.name == "unit-converter.html":
        source = source.replace('<label>Category</label>', '<label for="ucCat">Category</label>', 1)
        source = source.replace('<label>From</label>\n          <input type="number" id="ucIn"', '<label for="ucIn">Value to convert</label>\n          <input type="number" id="ucIn"', 1)
        source = source.replace('<select id="ucFrom"', '<label class="sr-only" for="ucFrom">From unit</label>\n          <select id="ucFrom"', 1)
        source = source.replace('<label>To</label>\n          <input type="number" id="ucOut"', '<label for="ucOut">Converted value</label>\n          <input type="number" id="ucOut"', 1)
        source = source.replace('<select id="ucTo"', '<label class="sr-only" for="ucTo">To unit</label>\n          <select id="ucTo"', 1)

    if path.name == "recipe-nutrition-calculator.html":
        for index, placeholder in ((1, "e.g. 2 eggs"), (2, "e.g. 100g chicken breast")):
            source = source.replace(
                f'<input type="text" placeholder="{placeholder}" class="ing-input"',
                f'<label class="sr-only" for="ingredient-{index}">Ingredient {index}</label><input type="text" id="ingredient-{index}" placeholder="{placeholder}" class="ing-input"',
                1,
            )

    if source != original:
        path.write_text(source, encoding="utf-8")
        changed.append(path.relative_to(ROOT))

print(f"Applied static accessibility foundations to {len(changed)} files.")
