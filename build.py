"""Build the email signature HTML following email-client best practices.

Colors come from the "Lift Off" design system, component EmailSignature
(https://claude.ai/artifact/FoMxEKirugrEcs4n5GvtgH).

Usage: python3 build.py <image_base_url> <out_dir>
"""
import sys, os

BASE = sys.argv[1].rstrip("/")
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

FONT = "Helvetica, Arial, sans-serif"
DARK = "#343A40"
TEAL = "#4D9D9D"
CARD = "#F3F6F6"
MUTED = "#6B747A"

import json
_d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "daten.json")))
NAME = _d["name"]
LINKS = {
    "phone": (_d.get("telefon_link", ""), _d.get("telefon", ""), "Telefon"),
    "mail": ("mailto:" + _d["email"], _d["email"], "E-Mail"),
    "web": (_d["website_link"], _d["website"], "Website"),
    "linkedin": (_d["linkedin_link"], "LinkedIn", "LinkedIn"),
}

def keep_parts(text):
    """Give an "A &middot; B &middot; C" line one break point, after its first
    half, so a phone shows two balanced lines and never a lone last word."""
    parts = [p.strip().replace(" ", "&nbsp;") for p in text.split("&middot;")]
    k = max(1, len(parts) // 2)
    return " ".join(["&nbsp;&middot;&nbsp;".join(parts[:k]) + "&nbsp;&middot;",
                     "&nbsp;&middot;&nbsp;".join(parts[k:])]) if len(parts) > 1 else parts[0]


ADDRESS = keep_parts(_d["adresse"])
TAGLINE = _d["tagline"]
ROLES = keep_parts(_d["rollen"])


def icon(name, alt):
    return (f'<img src="{BASE}/sig-{name}.png" width="22" height="22" alt="" '
            f'style="display:block;width:22px;height:22px;border:0;outline:none;">')


def contact(name, pad_bottom):
    href, label, alt = LINKS[name]
    # The gap is padding, not cell width, so it survives when a phone squeezes the table.
    return (
        f'<tr><td width="22" valign="middle" style="padding:0 8px {pad_bottom}px 0;width:22px;">{icon(name, alt)}</td>'
        f'<td valign="middle" style="padding:0 0 {pad_bottom}px 0;font-family:{FONT};font-size:13px;line-height:18px;color:{DARK};">'
        f'<a href="{href}" style="color:{DARK};text-decoration:none;">{label}</a></td></tr>'
    )


def column(names):
    rows = "".join(contact(n, 8) for n in names)
    return f'<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;">{rows}</table>'


# Contacts side by side on desktop, stacked on phones ("hybrid" columns):
# inline-block divs wrap when the screen is too narrow; Outlook Desktop,
# which ignores max-width on divs, gets a fixed two-column table instead.
COL1_W, COL2_W = 244, 170


def contacts():
    # The phone row is optional: it is left out when daten.json has no number.
    if LINKS["phone"][1]:
        left, right = ["phone", "web"], ["mail", "linkedin"]
    else:  # no phone: email moves up so the left column has no gap at the top
        left, right = ["mail", "web"], ["linkedin"]
    return (
        f'<tr><td colspan="2" style="font-size:0;line-height:0;">'
        f'<!--[if mso]><table cellpadding="0" cellspacing="0" border="0" role="presentation"><tr><td width="{COL1_W}" valign="top"><![endif]-->'
        f'<div style="display:inline-block;width:100%;max-width:{COL1_W}px;vertical-align:top;">{column(left)}</div>'
        f'<!--[if mso]></td><td width="{COL2_W}" valign="top"><![endif]-->'
        f'<div style="display:inline-block;width:100%;max-width:{COL2_W}px;vertical-align:top;">{column(right)}</div>'
        f'<!--[if mso]></td></tr></table><![endif]-->'
        f'</td></tr>'
    )


def build(with_address):
    address = (
        f'<tr><td colspan="2" style="padding:4px 0 0 0;font-family:{FONT};font-size:12px;line-height:16px;color:{MUTED};">{ADDRESS}</td></tr>'
        if with_address else ""
    )
    return f'''<table cellpadding="0" cellspacing="0" border="0" role="presentation" width="540" style="border-collapse:separate;width:100%;max-width:540px;font-family:{FONT};">
<tr><td bgcolor="{CARD}" style="background-color:{CARD};border-radius:12px 12px 0 0;padding:20px 20px;">
<table cellpadding="0" cellspacing="0" border="0" role="presentation" width="100%" style="border-collapse:collapse;width:100%;">
<tr>
<td width="78" valign="top" style="padding:0 18px 0 0;width:60px;"><a href="{LINKS["web"][0]}" style="text-decoration:none;"><img src="{BASE}/sig-logo.png" width="60" height="78" alt="Positive Leadership Coach" style="display:block;width:60px;height:78px;border:0;outline:none;"></a></td>
<td valign="top" width="100%">
<table cellpadding="0" cellspacing="0" border="0" role="presentation" width="100%" style="border-collapse:collapse;width:100%;">
<tr><td colspan="2" style="font-family:{FONT};font-size:20px;line-height:26px;font-weight:bold;color:{DARK};">{NAME}</td></tr>
<tr><td colspan="2" style="padding:2px 0 14px 0;font-family:{FONT};font-size:11px;line-height:16px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:{TEAL};">{ROLES}</td></tr>
{contacts()}
{address}
</table>
</td>
</tr>
</table>
</td></tr>
<tr><td bgcolor="{DARK}" style="background-color:{DARK};border-radius:0 0 12px 12px;padding:11px 22px;">
<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="border-collapse:collapse;"><tr>
<td width="24" valign="middle" style="padding:0 10px 0 0;width:14px;"><img src="{BASE}/sig-logo-klein.png" width="14" height="18" alt="" style="display:block;width:14px;height:18px;border:0;outline:none;"></td>
<td valign="middle" style="font-family:{FONT};font-size:12px;line-height:16px;color:#FFFFFF;">{TAGLINE}</td>
</tr></table>
</td></tr>
</table>'''


HEADER = ("Content-Transfer-Encoding: 7bit\n"
          "Content-Type: text/html;\n\tcharset=us-ascii\n"
          "Mime-Version: 1.0 (Mac OS X Mail 16.0)\n\n")

for with_address, slug in [(True, "mit-adresse"), (False, "ohne-adresse")]:
    sig = build(with_address)
    assert all(ord(c) < 128 for c in sig), "non-ASCII character in signature"
    # 1) Standalone HTML page (preview / Safari)
    with open(f"{OUT}/signatur-{slug}.html", "w") as f:
        f.write('<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<title>Signatur {NAME}</title></head><body style="margin:0;padding:24px;background:#ffffff;">{sig}</body></html>\n')
    # 2) Apple Mail .mailsignature content
    with open(f"{OUT}/apple-mail-{slug}.txt", "w") as f:
        f.write(HEADER + '<body style="word-wrap: break-word; -webkit-nbsp-mode: space; line-break: after-white-space;">'
                f'<div><br></div>{sig}</body>\n')
    # 3) Bare snippet (Gmail / Outlook / other tools)
    with open(f"{OUT}/snippet-{slug}.html", "w") as f:
        f.write(sig + "\n")
print("built", OUT)
