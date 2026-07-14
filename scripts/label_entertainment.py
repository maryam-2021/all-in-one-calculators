from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTERTAINMENT = {
    "love-calculator",
    "friendship-compatibility",
    "zodiac-matcher",
    "numerology-calculator",
    "lucky-numbers",
    "baby-name-meaning",
    "life-expectancy",
}
LABEL = (
    '<aside class="content-label entertainment-label" role="note">'
    '<strong>Entertainment only</strong>'
    '<span>This tool shows its deterministic rules for transparency, but its result is not a scientific assessment or prediction. Do not use it for medical, financial, relationship, or other important decisions.</span>'
    '</aside>'
)

for slug in sorted(ENTERTAINMENT):
    path = ROOT / f"{slug}.html"
    source = path.read_text(encoding="utf-8")
    if "entertainment-label" not in source:
        source = source.replace('<div class="calc-header">', LABEL + '\n    <div class="calc-header">', 1)
    if 'data-content-type="entertainment"' not in source:
        source = source.replace("<body>", '<body data-content-type="entertainment">', 1)
    source = source.replace('"applicationCategory":"UtilityApplication"', '"applicationCategory":"EntertainmentApplication"', 1)
    path.write_text(source, encoding="utf-8")

relationship = ROOT / "relationship-calculators.html"
source = relationship.read_text(encoding="utf-8")
source = source.replace("Relationship Tools", "Entertainment &amp; Relationship Tools")
source = source.replace("Entertainment &amp;amp; Relationship Tools", "Entertainment &amp; Relationship Tools")
if "category-entertainment-note" not in source:
    note = '<aside class="content-label category-entertainment-note" role="note"><strong>Entertainment category</strong><span>These tools use visible, deterministic rules for recreation. They are not scientific compatibility, personality, or predictive assessments.</span></aside>'
    source = source.replace('<div class="tools-grid" style="margin-top:36px">', note + '\n    <div class="tools-grid" style="margin-top:36px">', 1)
for title in ("Love Calculator", "Friendship Tester", "Zodiac Matcher", "Numerology Life Path", "Lucky Number Generator"):
    source = source.replace(f"<h3>{title}</h3>", f'<span class="card-badge">Entertainment</span><h3>{title}</h3>')
relationship.write_text(source, encoding="utf-8")

lifestyle = ROOT / "lifestyle-calculators.html"
source = lifestyle.read_text(encoding="utf-8")
if "category-mixed-note" not in source:
    note = '<aside class="content-label category-mixed-note" role="note"><strong>Planning and entertainment</strong><span>Budget, pet-age, and habit tools are planning aids. Baby-name and life-expectancy tools are clearly labelled entertainment.</span></aside>'
    source = source.replace('<div class="tools-grid" style="margin-top:36px">', note + '\n    <div class="tools-grid" style="margin-top:36px">', 1)
for title in ("Baby Name Meanings", "Life Expectancy (Fun)"):
    source = source.replace(f"<h3>{title}</h3>", f'<span class="card-badge">Entertainment</span><h3>{title}</h3>')
lifestyle.write_text(source, encoding="utf-8")

generator = ROOT / "scripts" / "complete_calculator_schema.py"
source = generator.read_text(encoding="utf-8")
if "ENTERTAINMENT_SLUGS" not in source:
    source = source.replace(
        'ROOT = Path(__file__).resolve().parents[1]\n',
        'ROOT = Path(__file__).resolve().parents[1]\nENTERTAINMENT_SLUGS = ' + repr(ENTERTAINMENT) + '\n',
        1,
    )
    source = source.replace(
        '"applicationCategory": "UtilityApplication",',
        '"applicationCategory": "EntertainmentApplication" if path.stem in ENTERTAINMENT_SLUGS else "UtilityApplication",',
        1,
    )
generator.write_text(source, encoding="utf-8")

print(f"Labelled {len(ENTERTAINMENT)} entertainment tools and clarified both mixed categories.")
