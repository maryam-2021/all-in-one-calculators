from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json, re, sys

ROOT=Path(__file__).resolve().parents[1]
BASE="https://truecalco.com/"
ENTERTAINMENT={"love-calculator","friendship-compatibility","zodiac-matcher","numerology-calculator","lucky-numbers","baby-name-meaning","life-expectancy"}

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=[]; self.in_title=False; self.h1=0; self.links=[]; self.canonical=[]; self.description=[]; self.scripts=[]; self.json_ld=[]; self.in_script=False; self.script_type=""; self.buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="title": self.in_title=True
        if tag=="h1": self.h1+=1
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="link" and a.get("rel")=="canonical": self.canonical.append(a.get("href",""))
        if tag=="meta" and a.get("name")=="description": self.description.append(a.get("content",""))
        if tag=="script": self.in_script=True; self.script_type=a.get("type",""); self.buf=[]
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
        if tag=="script":
            script="".join(self.buf)
            if self.script_type=="application/ld+json": self.json_ld.append(script)
            elif not self.script_type or "javascript" in self.script_type: self.scripts.append(script)
            self.in_script=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if self.in_script:self.buf.append(data)

errors=[]; titles={}; canonicals={}; htmls=list(ROOT.glob("*.html"))
for f in htmls:
    source=f.read_text(encoding="utf-8"); p=P(); p.feed(source)
    title="".join(p.title).strip()
    if not title: errors.append(f"{f.name}: missing title")
    elif title in titles: errors.append(f"{f.name}: duplicate title with {titles[title]}")
    else: titles[title]=f.name
    if p.h1 != 1: errors.append(f"{f.name}: expected one h1, found {p.h1}")
    if not p.description or len(p.description[0])<50: errors.append(f"{f.name}: missing/short description")
    if f.name == "404.html":
        continue
    if len(p.canonical)!=1: errors.append(f"{f.name}: expected one canonical")
    else:
        c=p.canonical[0]
        expected_canonical = BASE if f.name == "index.html" else BASE + f.stem
        if c != expected_canonical: errors.append(f"{f.name}: wrong canonical {c}; expected {expected_canonical}")
        if c in canonicals: errors.append(f"{f.name}: duplicate canonical with {canonicals[c]}")
        canonicals[c]=f.name
    if 'class="calc-form"' in source:
        if 'src="share-links.js"' not in source: errors.append(f"{f.name}: missing shareable URL support")
        try:
            schemas=[json.loads(value) for value in p.json_ld]
        except json.JSONDecodeError as exc:
            errors.append(f"{f.name}: invalid JSON-LD: {exc}")
            schemas=[]
        nodes=[]
        for schema in schemas:
            nodes.extend(schema.get("@graph",[schema]))
        apps=[node for node in nodes if node.get("@type")=="SoftwareApplication"]
        faqs=[node for node in nodes if node.get("@type")=="FAQPage"]
        if len(apps)!=1: errors.append(f"{f.name}: expected one SoftwareApplication schema, found {len(apps)}")
        elif apps[0].get("url")!=expected_canonical: errors.append(f"{f.name}: SoftwareApplication URL does not match canonical")
        if f.stem in ENTERTAINMENT:
            if 'data-content-type="entertainment"' not in source: errors.append(f"{f.name}: missing entertainment content type")
            if 'class="content-label entertainment-label"' not in source: errors.append(f"{f.name}: missing visible entertainment label")
            if 'class="formula-box"' not in source: errors.append(f"{f.name}: entertainment rule is not transparent")
            if len(apps)==1 and apps[0].get("applicationCategory")!="EntertainmentApplication": errors.append(f"{f.name}: wrong entertainment schema category")
        visible_faqs=len(re.findall(r'class="faq-question"',source,re.I))
        if visible_faqs < 3: errors.append(f"{f.name}: expected at least three visible FAQs, found {visible_faqs}")
        if len(faqs)!=1: errors.append(f"{f.name}: expected one FAQPage schema, found {len(faqs)}")
        elif len(faqs[0].get("mainEntity",[]))!=visible_faqs: errors.append(f"{f.name}: FAQ schema does not match visible FAQs")
    for href in p.links:
        if href.startswith(("http://","https://","mailto:","tel:","#","javascript:")): continue
        target=href.split("#")[0].split("?")[0]
        if not target: continue
        if target == "/": resolved = ROOT / "index.html"
        else:
            resolved = ROOT / target.lstrip("/")
            if not resolved.suffix: resolved = resolved.with_suffix(".html")
        if not resolved.exists(): errors.append(f"{f.name}: broken link {href}")

sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
listed=set(re.findall(r"<loc>(.*?)</loc>",sitemap))
expected={BASE if f.name=="index.html" else BASE+f.stem for f in htmls if f.name!="404.html"}
for u in sorted(expected-listed): errors.append(f"sitemap missing {u}")
for u in sorted(listed-expected): errors.append(f"sitemap extra {u}")
for f in ROOT.glob("*.*"):
    if f.suffix.lower() in {".html",".xml",".txt",".js"}:
        content=f.read_text(encoding="utf-8",errors="ignore")
        if "all-in-one-calculators.vercel.app" in content or "all-in-one-calculators.pages.dev" in content:
            errors.append(f"{f.name}: contains an old production host")
        if f.suffix.lower()==".html" and re.search(r'href=["\'][^"\':/]+\.html(?:[?#][^"\']*)?["\']',content,re.I):
            errors.append(f"{f.name}: contains redirecting .html internal links")

new_pages=[f for f in htmls if 'expansion-calculators.js' in f.read_text(encoding='utf-8') and 'data-calculator=' in f.read_text(encoding='utf-8')]
if len(new_pages)!=34: errors.append(f"expected 34 expansion calculators, found {len(new_pages)}")

contact=(ROOT/"contact.html").read_text(encoding="utf-8") if (ROOT/"contact.html").exists() else ""
if "mailto:hello@truecalco.com" not in contact: errors.append("contact.html: missing support email")
if "github.com/maryam-2021/all-in-one-calculators/issues" not in contact: errors.append("contact.html: missing GitHub issue link")
relationship=(ROOT/"relationship-calculators.html").read_text(encoding="utf-8")
lifestyle=(ROOT/"lifestyle-calculators.html").read_text(encoding="utf-8")
if relationship.count('class="card-badge"')!=5 or "category-entertainment-note" not in relationship: errors.append("relationship-calculators.html: incomplete entertainment labelling")
if lifestyle.count('class="card-badge"')!=2 or "category-mixed-note" not in lifestyle: errors.append("lifestyle-calculators.html: incomplete mixed-category labelling")

if errors:
    print("VALIDATION FAILED")
    print("\n".join(errors)); sys.exit(1)
print(f"PASS: {len(htmls)} HTML pages, {len(listed)} sitemap URLs, {len(new_pages)} new calculators, no broken internal links.")
