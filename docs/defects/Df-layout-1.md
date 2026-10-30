---
id: Df-layout-1
title: Website address breaks at a hyphen on 360px phone screens
kind: Df
state: open
severity: low
area: layout
gate: next design change to the signature, or when Adriane asks
source: 2026-10-30 render tests (7-phone-360px)
opened: 2026-10-30
---

At 360px viewport width test_render.py scenario 7-phone-360px shows the website line wrapping as 'positive-leadership-' / 'coach.com': the label is wider than the left contact column on a phone. Options: shorter display label, smaller logo column, or 12px contact text; each changes Adriane's design, so she or Sep decides. Done when scenario 7 shows the website address on one line and the other 6 scenarios are unchanged.
