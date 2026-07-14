from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ENTERTAINMENT_SLUGS = {'zodiac-matcher', 'life-expectancy', 'baby-name-meaning', 'lucky-numbers', 'numerology-calculator', 'love-calculator', 'friendship-compatibility'}


class CalculatorContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = []
        self.questions = []
        self.answers = []
        self._in_h1 = False
        self._in_question = False
        self._answer_depth = 0
        self._question = []
        self._answer = []

    @staticmethod
    def classes(attrs):
        return dict(attrs).get("class", "").split()

    def handle_starttag(self, tag, attrs):
        classes = self.classes(attrs)
        if tag == "h1":
            self._in_h1 = True
        if tag == "button" and "faq-question" in classes:
            self._in_question = True
            self._question = []
        if "faq-answer" in classes:
            self._answer_depth = 1
            self._answer = []
        elif self._answer_depth:
            self._answer_depth += 1

    def handle_endtag(self, tag):
        if tag == "h1":
            self._in_h1 = False
        if tag == "button" and self._in_question:
            question = clean_text(" ".join(self._question))
            question = re.sub(r"\s*\+\s*$", "", question)
            if question:
                self.questions.append(question)
            self._in_question = False
        if self._answer_depth:
            self._answer_depth -= 1
            if self._answer_depth == 0:
                answer = clean_text(" ".join(self._answer))
                if answer:
                    self.answers.append(answer)

    def handle_data(self, data):
        if self._in_h1:
            self.heading.append(data)
        if self._in_question:
            self._question.append(data)
        if self._answer_depth:
            self._answer.append(data)


def clean_text(value):
    return re.sub(r"\s+", " ", unescape(value)).strip()


schema_pattern = re.compile(
    r'<script\s+type="application/ld\+json">.*?</script>', re.IGNORECASE | re.DOTALL
)
changed = []

for path in sorted(ROOT.glob("*.html")):
    source = path.read_text(encoding="utf-8")
    if 'class="calc-form"' not in source:
        continue

    parser = CalculatorContentParser()
    parser.feed(source)
    faqs = list(zip(parser.questions, parser.answers))
    if len(parser.questions) != len(parser.answers):
        raise RuntimeError(
            f"Could not extract complete FAQs from {path.name}: "
            f"{len(parser.questions)} questions, {len(parser.answers)} answers"
        )

    heading = clean_text(" ".join(parser.heading))
    heading = re.sub(r"^[^A-Za-z0-9]+", "", heading)
    description_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', source, re.IGNORECASE)
    canonical_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', source, re.IGNORECASE)
    if not heading or not description_match or not canonical_match:
        raise RuntimeError(f"Missing heading, description, or canonical in {path.name}")

    description = clean_text(description_match.group(1))
    url = canonical_match.group(1)

    if len(faqs) < 3:
        additions = [
            (
                f"How does the {heading} work?",
                f"The calculator applies the formula and assumptions explained on this page to the values you enter. {description}",
            ),
            (
                f"How accurate is the {heading}?",
                "The arithmetic follows the displayed method, but accuracy depends on your inputs, units, assumptions, and rounding. Confirm important decisions with an authoritative source or qualified professional.",
            ),
            (
                f"Does the {heading} save my inputs?",
                "No. The calculation runs in your browser and does not require an account. Avoid sharing a prefilled result link if its inputs are sensitive.",
            ),
        ]
        existing = {question.casefold() for question, _ in faqs}
        added = []
        for question, answer in additions:
            if len(faqs) + len(added) >= 3:
                break
            if question.casefold() in existing:
                continue
            added.append((question, answer))
            existing.add(question.casefold())
        if len(faqs) + len(added) < 3:
            raise RuntimeError(f"Could not create three unique FAQs for {path.name}")

        related_index = source.find('<div class="related-section"')
        faq_close_index = source.rfind("</div>", 0, related_index)
        if related_index < 0 or faq_close_index < 0:
            raise RuntimeError(f"Could not find the visible FAQ insertion point in {path.name}")
        visible_faqs = "\n".join(
            '      <button class="faq-question">'
            + escape(question)
            + '<span class="icon">+</span></button>\n'
            + '      <div class="faq-answer"><div class="faq-answer-inner">'
            + escape(answer)
            + "</div></div>"
            for question, answer in added
        )
        source = source[:faq_close_index] + visible_faqs + "\n    " + source[faq_close_index:]
        faqs.extend(added)

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "@id": url + "#application",
                "name": heading,
                "description": description,
                "applicationCategory": "EntertainmentApplication" if path.stem in ENTERTAINMENT_SLUGS else "UtilityApplication",
                "operatingSystem": "Any",
                "url": url,
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            {
                "@type": "FAQPage",
                "@id": url + "#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in faqs
                ],
            },
        ],
    }
    script = '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + "</script>"
    updated, count = schema_pattern.subn(script, source, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one JSON-LD block in {path.name}")
    path.write_text(updated, encoding="utf-8")
    changed.append(path.relative_to(ROOT))

print(f"Completed SoftwareApplication and FAQPage schema on {len(changed)} calculator pages.")
