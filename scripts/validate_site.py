from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import re, sys

ROOT=Path(__file__).resolve().parents[1]
BASE="https://all-in-one-calculators.pages.dev/"

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=[]; self.in_title=False; self.h1=0; self.links=[]; self.canonical=[]; self.description=[]; self.scripts=[]; self.in_script=False; self.script_type=""; self.buf=[]
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
            if not self.script_type or "javascript" in self.script_type: self.scripts.append("".join(self.buf))
            self.in_script=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if self.in_script:self.buf.append(data)

errors=[]; titles={}; canonicals={}; htmls=list(ROOT.glob("*.html"))
for f in htmls:
    p=P(); p.feed(f.read_text(encoding="utf-8"))
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
        if not c.startswith(BASE): errors.append(f"{f.name}: wrong canonical host {c}")
        if c in canonicals: errors.append(f"{f.name}: duplicate canonical with {canonicals[c]}")
        canonicals[c]=f.name
    for href in p.links:
        if href.startswith(("http://","https://","mailto:","tel:","#","javascript:")): continue
        target=href.split("#")[0].split("?")[0]
        if target and not (ROOT/target).exists(): errors.append(f"{f.name}: broken link {href}")

sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
listed=set(re.findall(r"<loc>(.*?)</loc>",sitemap))
expected={BASE if f.name=="index.html" else BASE+f.name for f in htmls if f.name!="404.html"}
for u in sorted(expected-listed): errors.append(f"sitemap missing {u}")
for u in sorted(listed-expected): errors.append(f"sitemap extra {u}")
for f in ROOT.glob("*.*"):
    if f.suffix.lower() in {".html",".xml",".txt",".js"} and "all-in-one-calculators.vercel.app" in f.read_text(encoding="utf-8",errors="ignore"):
        errors.append(f"{f.name}: contains old Vercel host")

new_pages=[f for f in htmls if 'expansion-calculators.js' in f.read_text(encoding='utf-8') and 'data-calculator=' in f.read_text(encoding='utf-8')]
if len(new_pages)!=34: errors.append(f"expected 34 expansion calculators, found {len(new_pages)}")

if errors:
    print("VALIDATION FAILED")
    print("\n".join(errors)); sys.exit(1)
print(f"PASS: {len(htmls)} HTML pages, {len(listed)} sitemap URLs, {len(new_pages)} new calculators, no broken internal links.")
