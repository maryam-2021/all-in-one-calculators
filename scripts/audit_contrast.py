from pathlib import Path
import re
import sys


CSS = (Path(__file__).resolve().parents[1] / "styles.css").read_text(encoding="utf-8")


def luminance(color):
    values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    values = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]


def contrast(first, second):
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


root = re.search(r":root\s*{(.*?)}", CSS, re.S).group(1)
light = re.search(r"body\.light-mode\s*{(.*?)}", CSS, re.S).group(1)


def variables(block):
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block))


dark_values = variables(root)
light_values = {**dark_values, **variables(light)}
checks = []
for theme, values in (("dark", dark_values), ("light", light_values)):
    background = values["bg-base"]
    for token in ("text-primary", "text-secondary", "text-muted"):
        checks.append((f"{theme} {token}", values[token], background, 4.5))
    checks.append((f"{theme} accent link", values["accent-blue"], background, 4.5))

button_rule = re.findall(r"\.calc-btn\s*{[^}]*background:\s*linear-gradient\([^#]*(#[0-9a-fA-F]{6})\s*,\s*(#[0-9a-fA-F]{6})", CSS, re.S)[-1]
for index, color in enumerate(button_rule, 1):
    checks.append((f"button gradient stop {index}", "#ffffff", color, 4.5))

focus_color = re.findall(r":focus-visible\s*{[^}]*outline:\s*3px solid (#[0-9a-fA-F]{6})", CSS, re.S)[-1]
checks.append(("dark focus indicator", focus_color, dark_values["bg-base"], 3.0))
checks.append(("light focus indicator", focus_color, light_values["bg-base"], 3.0))

failures = []
for label, foreground, background, minimum in checks:
    score = contrast(foreground, background)
    if score < minimum:
        failures.append(f"{label}: {score:.2f}:1, expected {minimum:.1f}:1")

if failures:
    print("CONTRAST AUDIT FAILED")
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS: {len(checks)} critical text, link, button, and focus color pairs meet WCAG AA contrast thresholds.")
