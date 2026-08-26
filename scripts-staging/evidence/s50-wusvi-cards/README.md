# S50 — WUSVI static-card rulings (PR-C)

Base origin/main `1ba27aa` (PR #148 squash). Stamped `2026-08-26T00:38:09.492Z`.

## Cards (12 ruled; 10 edited, 98818 + 274478 cards stand — true figures, no unit ruled)

| file:line (origin/main) | before | after |
|---|---|---|
| st-thomas.html:214 | `<div class="tour-price">From $140</div>` | `<div class="tour-price">From $140<small>per jet ski</small></div>` |
| st-thomas.html:370 | `<div class="tour-price">From $1495</div>` | `<div class="tour-price">From $1495<small>private boat</small></div>` |
| st-thomas.html:394 | `<div class="tour-price">From $75</div>` | `<div class="tour-price">Check availability</div>` |
| st-john.html:238 | `<div class="tour-price">$3500</div>` | `<div class="tour-price">$3500<small>per boat · Go Fast Full Day BVI Cruise</small></div>` |
| st-john.html:250 | `<div class="tour-price">$1300</div>` | `<div class="tour-price">$995</div>` |
| st-john.html:286 | `<div class="tour-price">From $1250</div>` | `<div class="tour-price">From $1250<small>per rental</small></div>` |
| st-john.html:346 | `<div class="tour-price">From $79</div>` | `<div class="tour-price">From $69</div>` |
| st-john.html:370 | `<div class="tour-price">From $325</div>` | `<div class="tour-price">From $325<small>per jeep · up to 4 people</small></div>` |
| st-croix.html:315 | `<div class="tour-price">From $50</div>` | `<div class="tour-price">Check availability</div>` |
| st-croix.html:327 | `<div class="tour-price">From $50</div>` | `<div class="tour-price">Check availability</div>` |

Line numbers are pre-edit; each island page also gains the `.tour-price small` rule (inline CSS, mirrors styles.css from #147) so the unit badge styles.
Static figures vs live cents (s50 batch/side probe, 4/4 dates): agree = True. Price elements per page unchanged: st-thomas.html 21→21, st-john.html 18→18, st-croix.html 18→18.

## Row corrections (2, full dated stamp `priceSource=s50-wusvi-cards`)

| pk | before | after | unit | basis |
|---|---|---|---|---|
| 411764 | null | $325 `Private Tour` high | per jeep, up to 4 people | 4/4 dated readings + tier object (row-corrections-tiers.json); non-vessel → gate renders "Price on request" + unit, never a seat price |
| 274478 | null | $75.68 `Half Day Stand Up Paddleboard` high | — | 4/4 dated readings + tier object; rental unit, label verbatim, gate does not render as seat price |

Rows outside these two: byte-identical (per-row sha asserted at apply). tours-data.json sha256 `51d698d7f74af235…` → `e2a4c91d3f1786ef…`.

## Dynamic render (node vm, both paths, data before/after)

per adult 123→123, private boat 112→112, Price on request 202→204, unit badges 23→24, Offer.price 123→123; activity strips unchanged.
