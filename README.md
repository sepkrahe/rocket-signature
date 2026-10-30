# rocket-signature

Bilder und Vorlage für die E-Mail-Signatur von positive-leadership-coach.com.
Die Bilder werden über GitHub Pages unter `https://signatur.positive-leadership-coach.com/bilder/` ausgeliefert.

## Inhalt
- `bilder/` – Logo und Icons (PNG, doppelte Auflösung)
- `build.py` – erzeugt die Signatur: `python3 build.py https://signatur.positive-leadership-coach.com/bilder dist`
- `lint.py` – prüft die Signatur auf E-Mail-Kompatibilität
- `test_render.py` – rendert 7 simulierte E-Mail-Programme (Apple Mail, Gmail, Outlook, Bilder blockiert, Dark Mode, Smartphone)
- `.claude/skills/email-signature/SKILL.md` – Anleitung für Claude Code: Regeln, Bauen, Testen, Installieren
- `daten.example.json` – Vorlage für die Kontaktdaten. Die echten Daten liegen nur lokal in `daten.json` (nicht im Repository).

## Umgesetzte Best Practices
- Bilder über https gehostet statt eingebettet (Gmail blockiert Base64-Bilder)
- Tabellen-Layout, nur Inline-CSS, 460 px breit, auf Mobilgeräten fließend
- Hintergrundfarben zusätzlich als `bgcolor` (Outlook)
- Icons dekorativ (`alt=""`), Logo mit Alt-Text
- Unter 10.000 Zeichen (Gmail-Limit), nur ASCII

Kontaktdaten werden bewusst nicht veröffentlicht.
