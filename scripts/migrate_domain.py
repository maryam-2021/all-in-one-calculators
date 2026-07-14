from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD_HOSTS = (
    "https://all-in-one-calculators.pages.dev",
    "https://all-in-one-calculators.vercel.app",
)
NEW_HOST = "https://truecalco.com"

html_files = sorted(ROOT.glob("*.html"))
routes = {
    path.name: ("/" if path.name == "index.html" else path.stem)
    for path in html_files
}

for path in html_files:
    source = path.read_text(encoding="utf-8")
    for host in OLD_HOSTS:
        source = source.replace(host, NEW_HOST)
    # Replace only known local HTML filenames, including canonicals, schema URLs,
    # hrefs, and the homepage's JavaScript search index.
    for filename, route in routes.items():
        source = source.replace(filename, route)
    path.write_text(source, encoding="utf-8")

urls = []
for path in html_files:
    if path.name == "404.html":
        continue
    url = NEW_HOST + ("/" if path.name == "index.html" else "/" + path.stem)
    urls.append(
        "  <url><loc>" + url + "</loc><lastmod>2026-07-14</lastmod></url>"
    )

(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(urls)
    + "\n</urlset>\n",
    encoding="utf-8",
)

(ROOT / "robots.txt").write_text(
    "User-agent: *\nAllow: /\n\nSitemap: https://truecalco.com/sitemap.xml\n",
    encoding="utf-8",
)

print(f"Migrated {len(html_files)} HTML files and {len(urls)} sitemap URLs to {NEW_HOST}.")
