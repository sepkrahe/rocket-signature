---
name: email-signature
description: Build, change, test and install an HTML email signature that works in Apple Mail, Gmail, Outlook and phone mail apps. Use when creating or editing the signature in this repository, adding a variant, changing its images, or when a signature shows broken images, lost layout or "?" boxes.
---

# Email signature: build, test, install

This repository holds Adriane Krahe's email signature for Apple Mail. It
follows the current best practices for email-client compatibility. Read this
whole file before changing anything. Its sibling `sepkrahe/coach-signature`
(Thomas Stiegler, Executive Coachings design system) follows the same rules
and tooling; keep the two in step.

## What lives where

| Path | Public? | What |
|---|---|---|
| `bilder/` | yes (GitHub Pages) | Logo and icons as PNG at 2x display size |
| `build.py` | yes | Builds the signature from a template |
| `lint.py` | yes | Compatibility checks (12 rules) |
| `test_render.py` | yes | Renders 7 simulated client scenarios |
| `daten.example.json` | yes | Placeholder contact data |
| `daten.json` | **no** (gitignored) | The real contact data |
| `dist/` | **no** (gitignored) | Generated signatures |

Images are served at `https://signatur.positive-leadership-coach.com/bilder/`
(GitHub Pages with a custom domain; DNS CNAME `signatur` →
`sepkrahe.github.io` at Squarespace).

**Privacy rule:** the repository is public. Never commit phone numbers,
email addresses, postal addresses or generated signatures. Before every
commit, run:
`git grep -nE "@[a-z0-9-]+\.[a-z]|\+49|[0-9]{5} [A-Z]" -- . ':!daten.example.json'`
and stop if it finds real data. Commit as
`sepkrahe <sepkrahe@users.noreply.github.com>`.

## The rules (from research; each one fixes a real failure)

1. **Host images; never embed them.** Gmail does not display base64 /
   `data:` images, and some spam filters flag such mail. Images are PNG
   (or JPG/GIF) at an `https://` URL. No SVG: most clients don't show it.
2. **Images at display size, 2x pixels, with `width` and `height`
   attributes** on every `<img>`. Without the attributes, Outlook and
   Apple Mail's paste show images at full pixel size.
3. **Tables for layout, inline styles only.** No `<style>`, no classes,
   no `div` layout, no flexbox, grid, `position`, `float` or
   `background-image`.
4. **Background colours twice:** `bgcolor` attribute and inline
   `background-color` (Outlook Desktop reads the attribute).
5. **Width:** 320–600px; this signature is 460px with `width="460"` and
   `style="width:100%;max-width:460px"`: fixed in Outlook, fluid on phones.
   Stack contacts in one column; a two-column grid gets cut off on phones.
6. **Fonts:** `Helvetica, Arial, sans-serif`. Email clients don't load
   web fonts such as Inter.
7. **Rounded corners** are fine but degrade to square in Outlook Desktop;
   design so square still looks clean.
8. **Alt text:** the logo gets descriptive alt text; icons next to text
   are decorative, `alt=""`.
9. **Dark mode:** use explicit background colours on every cell. Check
   both a full colour inversion (Outlook.com, Gmail app) and a dark page
   behind a light card (Apple Mail).
10. **Size:** under 10,000 characters (Gmail's signature limit), ASCII
    only (non-ASCII as HTML entities like `&middot;`), so Apple Mail's
    7-bit `.mailsignature` file stays valid.
11. **Links:** absolute only (`https://`, `mailto:`, `tel:`).
12. **Contrast:** text at least 4.5:1 against its background, icons
    3:1. The current roles line (#4D9D9D on #F3F6F6, 2.92:1), address
    (4.39:1) and white glyphs on #1ABC9C (2.41:1) are below target; they
    are kept as the owner chose them. Don't make it worse; propose
    `#0D7560` for the roles line if asked to fix contrast.

13. **Line breaks on phones:** lines made of parts ("A · B · C": roles,
    address) get one break point, after their first half; `build.py`
    (`keep_parts`) joins everything else with `&nbsp;`. Gaps between an
    icon and its text are padding, not cell width, so a phone cannot
    squeeze them away. An empty `telefon` in `daten.json` leaves the phone
    row out.

Design source: the **Lift Off** design system
(https://claude.ai/artifact/FoMxEKirugrEcs4n5GvtgH), component
`EmailSignature`, which has the tokens for every colour. Keep one accent
(the dark footer); no gradients, no `#54DCFC` (reserved decorative cyan),
no permanent call-to-action button.

## Build

```bash
cp daten.example.json daten.json   # first time only, then fill in real data
python3 build.py https://signatur.positive-leadership-coach.com/bilder dist
```

This writes, per variant (`mit-adresse`, `ohne-adresse`):
- `dist/signatur-*.html`: preview page
- `dist/apple-mail-*.txt`: complete `.mailsignature` content (headers included)
- `dist/snippet-*.html`: bare signature HTML for other programs

Change the design in `build.py` (the template), contact data in
`daten.json`. Never hand-edit files in `dist/`.

## Test (all three steps, every change)

1. **Lint:** `python3 lint.py dist/snippet-mit-adresse.html` and the same
   for `ohne-adresse`. Every line must say PASS.
2. **Render:** serve the images over http (WebKit refuses some `file://`
   images, which shows up as false "images did not load" failures), build
   a test copy against that server, and render both variants:
   ```bash
   python3 -m http.server 8765 --bind 127.0.0.1 &
   python3 build.py http://127.0.0.1:8765/bilder /tmp/sig-test
   for v in mit ohne; do
     uv run --no-project --with playwright==1.64.1 --with pillow \
       python test_render.py /tmp/sig-test/signatur-$v-adresse.html /tmp/sig-test/tests-$v
   done
   kill %1
   ```
   On kalahari, Playwright 1.64.1 matches the browsers already cached in
   `~/.cache/ms-playwright`; elsewhere run
   `python3 -m playwright install chromium webkit` once.
   Open each `overview.png` and look at every scenario:
   Apple Mail (WebKit), Gmail web (Chromium), Outlook Desktop (no rounded
   corners, fixed width), images blocked, dark mode inverted, dark page
   behind the card, phone at 360px. Check: nothing cut off, no awkward
   single-word line breaks, images the right size, text readable in dark
   mode. The script also reports images that fail to load.
3. **Real clients:** after installing, send a test email to a Gmail
   address and, if available, Outlook.com and an iPhone. Gmail may ask to
   show images first; that is normal. Simulations don't replace this.
   For a full matrix, Litmus or Email on Acid render in 90+ real clients
   (paid).

## Publish image changes

Images go live by pushing to `main`; GitHub Pages redeploys within a
minute or two. Keep file names stable: installed signatures load images
by name, so replacing `bilder/sig-logo.png` updates every signature
already sent or installed. A new image name means reinstalling.

## Install in Apple Mail (the only reliable way)

Copying the preview from Safari into Mail's signature editor breaks the
table layout and attaches the images to every mail. Instead:

1. Mail → Einstellungen → Signaturen: select the account that actually
   sends (a custom-domain address set up in iCloud+ sends through
   **iCloud**, not through its own account entry), click **+**,
   name the signature, type `XXX`. Quit Mail with ⌘Q.
2. Open `~/Library/Mail/V10/MailData/Signatures/` (the `V` number can
   differ; use the highest). Sort by date modified; the newest
   `.mailsignature` file is the new one.
3. If the file is locked: Get Info (Informationen) → uncheck Locked
   (Geschützt).
4. Replace the file's ENTIRE content with
   `dist/apple-mail-<variant>.txt` (it includes the right headers):
   `cp dist/apple-mail-mit-adresse.txt "<that file>"`.
5. Lock the file again (`chflags uchg "<file>"`, or Get Info → Locked),
   otherwise Mail overwrites it.
6. Open Mail, ⌘N, choose the signature in the Signature menu.

If the signature doesn't appear in a new mail's menu, it is assigned to
the wrong account: drag it from "Alle Signaturen" onto the account that
sends the mail, then set "Signatur auswählen" for that account.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Grey boxes instead of images in Gmail | base64 images | host images (rule 1) |
| "?" boxes in Apple Mail | image URL unreachable or changed | check the URL in a browser; keep file names stable |
| Huge logo and icons, layout broken | signature pasted through Mail's editor | install via the `.mailsignature` file |
| Signature missing from the menu | wrong account | assign it to the sending account (iCloud) |
| Images attached to every mail | images pasted into Mail's editor | install via the file, with hosted images |
| Square corners in Outlook | Outlook ignores `border-radius` | expected |
