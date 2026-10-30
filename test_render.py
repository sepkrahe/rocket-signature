"""Render the signature under simulated email-client conditions.

Usage: python3 test_render.py dist/signatur-mit-adresse.html [out_dir]

Writes one screenshot per scenario plus an overview (out_dir/overview.png).
Uses Playwright (Chromium and WebKit) when installed:
    pip install playwright pillow && python3 -m playwright install chromium webkit
and falls back to wkhtmltoimage otherwise.

These are simulations. They catch layout, sizing, missing-image and dark-mode
problems early; the final check is always a real test email (see SKILL.md).
"""
import os, re, shutil, subprocess, sys, tempfile

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "dist/tests"
os.makedirs(OUT, exist_ok=True)
base = open(SRC, encoding="utf-8").read()


def blocked(html):
    """Images blocked: each <img> becomes a box showing its alt text."""
    return re.sub(
        r'<img src="[^"]+" width="(\d+)" height="(\d+)" alt="([^"]*)"[^>]*>',
        lambda m: (f'<span style="display:inline-block;width:{m.group(1)}px;height:{m.group(2)}px;'
                   f'border:1px solid #bbb;font-size:8px;line-height:9px;color:#555;overflow:hidden;">{m.group(3)}</span>'),
        html)


def body_style(html, extra):
    return re.sub(r'<body style="', f'<body style="{extra}', html, count=1)


# name: (html, viewport width, engine)
SCENARIOS = {
    "1-apple-mail-webkit": (base, 600, "webkit"),
    "2-gmail-web-chromium": (base, 600, "chromium"),
    "3-outlook-desktop": (re.sub(r"border-radius:[^;]+;", "", base)
                          .replace("width:100%;max-width:460px;", "width:460px;"), 600, "chromium"),
    "4-images-blocked": (blocked(base), 600, "chromium"),
    "5-dark-mode-inverted": (body_style(base, "filter:invert(1) hue-rotate(180deg);"), 600, "chromium"),
    "6-dark-mode-background": (base.replace("background:#ffffff", "background:#1e1e1e"), 600, "webkit"),
    "7-phone-360px": (base, 360, "webkit"),
}

tmp = tempfile.mkdtemp()
pages = {}
for name, (html, width, engine) in SCENARIOS.items():
    path = os.path.join(tmp, name + ".html")
    open(path, "w", encoding="utf-8").write(html)
    pages[name] = (path, width, engine)


def with_playwright():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browsers = {}
        for name, (path, width, engine) in pages.items():
            if engine not in browsers:
                browsers[engine] = getattr(p, engine).launch()
            page = browsers[engine].new_page(viewport={"width": width, "height": 400}, device_scale_factor=2)
            page.goto("file://" + os.path.abspath(path))
            page.wait_for_load_state("networkidle")
            # every <img> must have loaded (catches dead image URLs)
            broken = page.evaluate("[...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src)")
            if broken and name != "4-images-blocked":
                print(f"FAIL {name}: images did not load: {broken}")
            page.screenshot(path=os.path.join(OUT, name + ".png"), full_page=True)
            page.close()
        for b in browsers.values():
            b.close()


def with_wkhtmltoimage():
    exe = shutil.which("wkhtmltoimage")
    if not exe:
        sys.exit("Neither Playwright nor wkhtmltoimage is available; install one (see the docstring).")
    for name, (path, width, _engine) in pages.items():
        subprocess.run([exe, "--enable-local-file-access", "--width", str(width), "-q", path,
                        os.path.join(OUT, name + ".png")], check=False, capture_output=True)


try:
    with_playwright()
    engine_used = "Playwright"
except Exception as e:  # not installed, or browsers missing
    print(f"Playwright unavailable ({type(e).__name__}); falling back to wkhtmltoimage.")
    with_wkhtmltoimage()
    engine_used = "wkhtmltoimage"

# overview image
try:
    from PIL import Image, ImageDraw
    shots = [(n, Image.open(os.path.join(OUT, n + ".png")).convert("RGB")) for n in SCENARIOS]
    w = max(i.width for _, i in shots) + 40
    h = sum(i.height + 40 for _, i in shots) + 20
    sheet = Image.new("RGB", (w, h), (225, 229, 231))
    d = ImageDraw.Draw(sheet)
    y = 10
    for n, i in shots:
        d.text((20, y), n, fill=(30, 30, 30))
        y += 20
        sheet.paste(i, (20, y))
        y += i.height + 20
    sheet.save(os.path.join(OUT, "overview.png"))
except ImportError:
    pass

print(f"Rendered {len(SCENARIOS)} scenarios with {engine_used} into {OUT}/")
