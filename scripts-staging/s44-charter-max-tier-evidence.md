# S44 — max-tier charter sweep (priceLabel `charter`, Math.max branch)

Template: KWST #240 three-branch charter-unit template (D-574 as amended by
D-600 — only rows minted by the `extract-price-v5.2.js` Math.max branch, i.e.
`priceLabel: "charter"`). Probe: `s44-charter-max-tier-probe.js`, base
2026-08-24, 17 dates, `include_breakdown=yes`, 68 requests, 0 errors. Raw
readings: `s44-charter-max-tier-readings.json`. Ledger:
`s44-charter-max-tier-adjudicated.json`.

## Population delta — the finding

| | `charter` rows |
|---|---|
| f2e7179 (KWST recon) | **39** |
| 7c5f744 (after #144) | **8** |

#144 relabelled 31 of the 39 to `private boat` (all 31 were inside its
D-485 HOLD ∩ active population). The residual 8 were never in the D-485 set,
so none of them is among #144's 16 held-out rows (12 UNIT_NOT_VESSEL, 2 DROP,
2 INSUFFICIENT) — checked pk-by-pk; nothing to flag under the WHAW ruling.

## Classification (8 rows)

| pk | company / name | stored | live tiers ($, 17/17 stable) | class | new |
|---|---|---|---|---|---|
| 102402 | Stormy Pirates — Full Day Private Charter (42' Power Boat) | 1900 | 6h 1900 / 7h 2100 / 8h 2400 / 8h-BVI 2550 | correct-by-construction | 1900 (label+conf+breakdown only) |
| 113436 | Stormy Pirates — Full Day (6 or 8 hours) … Luxury Sailing Catamaran | null | 6h 1900 / 8h 2200 / 8h-BVI 2600 (14/17) | duration-matched (D-601) | **1900** |
| 414246 | Local Legend — BVI Private | 600 | Includes Up To 6 Guests 1799.99 (+Fees); Additional Passenger 75 (ancillary, excluded) | stale-single-tier (FST) — $600 on no live tier | **1799.99** |
| 494820 | Stormy Pirates — Private Charter - Gorda Pirate | 7000 | 6h 6000 / 8h 7000 / 8h-BVI 8500 | max-tier→floor (D-597); stored was the 8h tier, ladder max is 8500 | **6000** |
| 623831 | Drift Charters — USVI Half Day Charter | 975 | Private Charter: 1-6 people 875 / 7-12 people 975 | max-tier→floor (D-597) | **875** |
| 624217 | Drift Charters — USVI Full Day Charter | 1500 | Private Charter: 1-6 people 1400 / 7-12 people 1500 | max-tier→floor (D-597) | **1400** |
| 484583 | Summerwind — Multi-night Sailing USVI/BVI | 11770 | none — `items: []` on all 17 dates | **INSUFFICIENT** | unchanged |
| 487208 | Summerwind — Multi-night Sailing St. Augustine (FL) | 6995 | none — `items: []` on all 17 dates | **INSUFFICIENT** | unchanged |

Vessel assertions (D-596): 102402 row name "42' Power Boat"; 113436 row name
"Luxury Sailing Catamaran"; 414246 description "powerboat"/"vessel"; 494820
named vessel "Gorda Pirate" + description "Catamaran"; 623831/624217
description "boat"/"captain", company Drift Charters. No PARTY_BARE-prefixed
tier labels in this population — the Drift bands sit in the tier *note* under
the unit tier name "Private Charter".

Discards: no $0 tiers appeared (zeroOnlyDates = [] for all 6); no gratuity
tiers appeared; 414246's "Additional Passenger — Priced per person" excluded
as a per-person add-on (D-483/D-494). Date validity: 55 of 102 readings fell
on the requested date; every tier price was identical across all 17 readings.

INSUFFICIENT detail (wrong-shortname rule applied first): `summerwindadventures`
answers HTTP 200 with the company found; `summerwind`, `summerwindsailing`,
`summerwindcharters` are 400 "not found". `/api/v1/companies/…/items/{pk}/`
reports both items `is_archived=false, is_private=false, is_unlisted=false`
— live products with no priced availability published; not a dead call.
Side note (out of scope): 487208 is a Florida itinerary stored as
`island: st-thomas`.

## Static-card sweep (56 cards: st-croix 17 / st-john 18 / st-thomas 21)

- `st-thomas.html:298` — 113436's card reads "From $1900"; equals the new
  live floor. Names a corrected pk, figure already correct → no edit.
- `st-croix.html:363` — "$1400" is Top Shot's Full Day Charter, not a
  corrected pk → no edit.
No other corrected figure (600, 7000, 975, 1500, 875, 6000, 1799.99) appears
in any html/partial.

## Write

`apply-s44-charter-max-tier.py` (Python, D-599 byte round-trip: sha256 of a
no-op re-serialise equals the committed file). Four fields per row (#247):
price, priceLabel `private boat`, priceConfidence `high`, priceBreakdown.
634 rows before and after; 6 rows differ; `charter` population 8 → 2.
