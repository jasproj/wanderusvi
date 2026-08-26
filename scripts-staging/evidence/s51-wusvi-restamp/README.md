# S51 — WUSVI dated re-stamp of the 282 rows ruled before the stamp convention

| | |
|---|---|
| Base | origin/main `6b22b35` (PR #150 squash) |
| Stamped | `2026-08-26T16:42:10.068Z` |
| Population | 282 (frozen in population.json): live rows with no s50 stamp = 551 live − 269 stamped; re-derived at open, **delta 0** vs the s50 close figure. 177 carry a git price-field edit from #135–#145, 1 an island-only edit (#137), 104 are s40 297-sweep HOLD rows never edited |
| Rulings ledger | rulings.json — per row: ruled figure, named tier, label, unit, source (s44 #145 6 · s43 #144 94 · s40 #138 52 · #135 9 published + 14 nulled · #139 2 nulled · s42 BCVI 1) — latest ruling wins |
| Probe | price-preview/per-item/v2, include_breakdown=yes, dates 2026-09-05, 2026-09-19, 2026-10-03, 2026-10-24, ≤20 pks/req, 1 req/s, 216 requests, 0 retries, reconcile 282/282. Chrome DARK — labelled substitution: node fetch (same UA/endpoint as s50), not a browser session |
| Rows changed | 282 / 282; 0 reported-not-written (byte-identical, sha-asserted); 0 outside population; stale `_unknownFields.priceSource` residue removed on 63 |
| tours-data.json sha256 (Python hashlib) | before `479f7e4eb855b970…` → after `fc5cc2e51add6160…` |

## Rule set applied

s50 apply machinery (D-624 anchor, D-482 consensus gate, D-484 asserted unit, D-614/D-621 whole-unit, s48-R1, UNIT_NOT_VESSEL gate vocabulary, cross-date agreement, add-on abort) with: **G1** both s50 classifier guards (bare-pp note trap; D-625 promotion → base_implicit → D-484 hold), **G2** never-anchor on unicode-normalised labels (NFKD-stripped, NFKC, quote-folded, casefolded), **G3** adjective-head guard ("Standard Full Day … Cruise" is a whole-unit tier, not a seat; `cruise` joins the whole-unit tokens), the four s50 R-rules (**R-zero-base** closed-date $0 readings excluded, **R-passenger**, **R-omitted**, **R-season** cross-date floor over open dates), **P-floor** (≤ $1 is a placeholder). Ruling-honour branch: named tier looked up by name on every reading — match → restamp unchanged (ruled confidence retained), drift → live figure, tier renamed with identical figure → re-anchor (s51 packet); unsampled → low dated stamp; $0 on every date → reported.

## Dispositions

| disposition | n |
|---|---|
| honoured:unchanged | 150 |
| D-621:unchanged | 32 |
| D-614:repriced | 19 |
| HELD:d482_ambiguous | 15 |
| D-614:unchanged | 13 |
| D-621:repriced | 9 |
| HELD:d484_no_unit | 9 |
| zero_price | 7 |
| UNSAMPLED | 6 |
| renamed-tier:unchanged | 5 |
| HELD:unit_underivable | 3 |
| D-624:unchanged | 3 |
| HELD:implausible_floor | 3 |
| live-unit:unchanged | 2 |
| HELD:no_base_tier | 2 |
| HELD:mixed_verdict | 2 |
| D-624:repriced | 1 |
| HELD:d484_unit_conflict | 1 |

## Honoured rulings (figure rows)

150 rows: ruled tier present by name on every open reading, live figure == ruled figure on all of them → fresh dated stamp, figure/label/unit/confidence unchanged. **0 drifted.** Classifier concordance: 143 agree, 7 disagree (listed below; ruling wins).

11 of them read $0 on some dates (closed dates, R-zero-base): 98822 (1/4), 710999 (1/4), 665469 (3/4), 665505 (3/4), 665503 (3/4), 688793 (1/4), 688794 (1/4), 662884 (1/4), 642301 (1/4), 642304 (1/4), 688795 (1/4)

### Classifier disagreements (ruling honoured, listed for visibility)

| pk | name | ruled tier / figure | source | classifier |
|---|---|---|---|---|
| 135450 | Half Day Private Charter Aboard M/V Aquarius | `Private Charter` $895 | s43 #144 | HELD:d484_unit_conflict |
| 135444 | Full Day Private Charter Aboard M/V Aquarius | USV | `Private Charter` $1495 | s43 #144 | HELD:d484_unit_conflict |
| 171331 | Half Day Aboard MV Poseidon | USVI Beach & Snorkel | `Half Day Charter` $995 | s43 #144 | HELD:d484_unit_conflict |
| 185836 | Half Day 50' Private Sailing Catamaran | Luxury, B | `Half Day Charter` $1495 | s43 #144 | HELD:d484_unit_conflict |
| 185842 | Full Day 50' Private Sailing Catamaran | Luxury, B | `Full Day Charter Up to 12 Guests` $2195 | s43 #144 | HELD:d484_unit_conflict |
| 184337 | Full Day Aboard MV Poseidon | USVI Beach & Snorkel | `Full Day Charter Up to 12 Guests` $1595 | s43 #144 | HELD:d484_unit_conflict |
| 569248 | Second Chance-USVI Sunset Trip | `Private Charter` $900 | s42 BCVI adjudication | HELD:d482_ambiguous |

## The 12 rows first reported-not-written — ruled 2026-08-26 (s51 packet), now written

| pk | name | first pass | ruling outcome | after | label | unit | conf |
|---|---|---|---|---|---|---|---|
| 712904 | VIRGIN GORDA BVI – THE BATHS & BEYOND | TIER_GONE | renamed-tier:unchanged ← 8-Hour BVI Charter | $1645 | private boat | Flying Tiger II - Private Charter | high |
| 712877 | JOST VAN DYKE BVI (Soggy Dollar • Foxy’s | TIER_GONE | renamed-tier:unchanged ← 8-Hour BVI Charter | $1645 | private boat | Flying Tiger II - Private Charter | high |
| 712879 | NORMAN ISLAND & JOST VAN DYKE BVI (Willy | TIER_GONE | renamed-tier:unchanged ← 8-Hour BVI Charter | $1645 | private boat | Flying Tiger II - Private Charter | high |
| 662207 | CIRCLE SAINT JOHN + LIME OUT TACO BOAT | TIER_GONE | renamed-tier:unchanged ← 7-Hour USVI Charter | $1445 | private boat | Flying Tiger II - Private Charter | high |
| 666565 | FULL DAY FREESTYLE | TIER_GONE | renamed-tier:unchanged ← 7-Hour USVI Charter | $1445 | private boat | Flying Tiger II - Private Charter | high |
| 536583 | Pizza Pi - Jet Ski | UNNAMED_TIER | live-unit:unchanged · tier label quoted: "Yamaha Jet Ski" | $175 | Yamaha Jet Ski | per jet ski | high |
| 112436 | Parasailing (Departs from Christiansted, | UNNAMED_TIER | HELD · unit_underivable | $95 | Parasailor - Depart from St. Croix |  | low |
| 45210 | Parasailing (Departs from Cruz Bay, St.  | UNNAMED_TIER | HELD · unit_underivable | $130 | Parasailor - Depart from St. John |  | low |
| 45207 | Parasailing (Departs from Havensight Cru | UNNAMED_TIER | HELD · unit_underivable | $120 | Parasailor - Depart from St. Thomas |  | low |
| 564312 | Guided Paddle Board Tour from Elysian | UNNAMED_TIER | live-unit:unchanged · product name quoted: "Paddle Board" | $40 | Water Sports | per paddle board | high |
| 172285 | Open Water Dive Referral Course | UNSAMPLED | UNSAMPLED | $598.8 |  |  | low |
| 170675 | Scuba Tune-up | UNSAMPLED | UNSAMPLED | $210 |  |  | low |

TIER_GONE ×5 (Flying Tiger) — ruled 2026-08-26: the live tier label `Flying Tiger II - Private Charter` contains the unit (whole-boat shape, D-621); identical figure on every open date (712904/712877/712879 read $0 on 2026-10-24 — closed date, excluded) → re-anchored as **private boat** (gate vocabulary), unit = the label quoted verbatim, anchors unchanged ($1645 ×3, $1445 ×2), high. UNNAMED_TIER ×5: 536583 unit from the tier label (`Yamaha Jet Ski` → per jet ski); 564312 unit from the product name (`Guided Paddle Board Tour…` → per paddle board — the weakest link, sanctioned); the 3 parasail rows (`Parasailor - Depart from …`) yield nothing from label, description or name → **HELD `unit_underivable`, named**. UNSAMPLED ×2: standard low dated stamp, stored figure retained unpublished.

## $1 pickup-location stubs — HELD permanently (s51 packet): a $1 stub is not a fare and never anchors

| pk | name | hold | floor stamped | ladder |
|---|---|---|---|---|
| 702972 | Elysian Beach Hut Location | implausible_floor | $1 `Adult` | Adult $1 |
| 702974 | Margaritaville Lobby | implausible_floor | $1 `Adult` | Adult $1 |
| 700689 | Margaritaville Store Location | implausible_floor | $1 `Adult` | Adult $1 |

## Former s40 HOLD rows released under the settled rule set (64) — ACCEPTED as settled (s51 packet): the s40 thing-token holds are retired

| rule | outcome | n |
|---|---|---|
| D-621 | badge only | 26 |
| D-614 | badge only | 16 |
| D-621 | renders | 13 |
| D-614 | renders | 5 |
| D-624 | renders | 4 |

| pk | name | s40 hold | stored → live | label | unit |
|---|---|---|---|---|---|
| 173310 | Snorkeling Adventures | D-482 ambiguous full-fare set (2 disti | $85 → **$85** | per adult |  |
| 235969 | Private - Sunset Sail & Snorkel (Sailing | D-485 group/charter unit (catamaran) | $1400 → **$1500** | private boat | Sunset Sail - 41' Catamaran |
| 352458 | Slumber Experience  by the Sea at Coral  | D-482 ambiguous full-fare set (2 disti | $150 → **$175** | per adult |  |
| 452820 | Sunset Cruise USVI | D-484 no asserted person unit (thing-t | $1000 → **$1000** | private boat | Sunset Cruise |
| 452821 | Sunset Cruise USVI | D-484 no asserted person unit (thing-t | $600 → **$600** | private boat | Sunset Cruise |
| 464992 | Half Day USVI Adventure | D-482 ambiguous full-fare set (2 disti | $995 → **$895** | private boat | 32'  Intrepid Boat (32 ft.) |
| 492776 | BVI Full Day with Captain - Private Your | D-482 ambiguous full-fare set (3 disti | $1000 → **$1000** | private boat | Jost Van Dyke Trip |
| 599942 | Champagne and Charcuterie Sunset | D-484 no asserted person unit (thing-t | $50 → **$1400** | private boat | Sunset Cruise |
| 630355 | Island Hopping Boat Charter | D-484 duration ladder (half day) | $1200 → **$1200** | private boat | Half Day |
| 630359 | Island Hopping Yacht Party | D-484 duration ladder (half day) | $2200 → **$2200** | private boat | Half Day |
| 630360 | Luxury Yacht Charter | D-482 ambiguous full-fare set (7 disti | $15000 → **$15000** | private boat | One Day |
| 660734 | 42' (Top Shelf) Freeman Power Catamaran | D-484 duration ladder (full day) | $3500 → **$3500** | private boat | Go Fast Full Day BVI Cruise |
| 664103 | 27’ (Palma Bella III) Worldcat | D-484 duration ladder (full day) | $995 → **$1300** | private boat | Standard Full Day Palma Bella III BVI Cruise |
| 673310 | 42' (Another Round) Freeman Power Catama | D-484 duration ladder (full day) | $3500 → **$3500** | private boat | Go Fast Full Day BVI Cruise |
| 678098 | Lime Out & Snorkel Half-Day | D-482 ambiguous full-fare set (2 disti | $975 → **$875** | private boat | Private Charter |
| 678117 | Lime Out & Snorkel Full-Day | D-482 ambiguous full-fare set (2 disti | $1500 → **$1400** | private boat | Private Charter |
| 681726 | Full Day BVI Power Catamaran | D-484 duration ladder (full day) | $2950 → **$2950** | private boat | Full Day BVI |
| 691460 | Full Day USVI Power Catamaran | D-484 duration ladder (full day) | $2650 → **$2650** | private boat | Full Day USVI |
| 701648 | Private Luxury Sunset Charter | D-484 no asserted person unit (thing-t | $1300 → **$1300** | private boat | Private Luxury Sunset Cruise |
| 704467 | Sunset Power Catamaran | D-484 no asserted person unit (thing-t | $1950 → **$1950** | private boat | Sunset Cruise |
| 730766 | St. Thomas Island Tour - Full Day | D-482 ambiguous full-fare set (2 disti | $129.95 → **$129.95** | per adult |  |
| 730773 | St. Thomas Island Tour - Half Day | D-482 ambiguous full-fare set (2 disti | $79.95 → **$79.95** | per adult |  |
| 8450 | Full Day Private Jeep Tour St Thomas | D-485 group/charter unit (private jeep | $545 → **$545** | Private Jeep | Private Jeep |
| 98818 | Bioluminescent Kayak Trip | D-482 ambiguous full-fare set (2 disti | $50 → **$50** | Ocean Kayak - Per Person Ticket | Ocean Kayak - Per Person Ticket |
| 194434 | Snorkel Gear Rentals - St. John | D-482 ambiguous full-fare set (5 disti | $55 → **$12** | One Day Rental | One Day Rental |
| 200902 | Snorkel Gear Rental – St. Thomas | D-482 ambiguous full-fare set (5 disti | $24 → **$12** | One Day Rental | One Day Rental |
| 211022 | Paddle Board Rental | D-482 ambiguous full-fare set (4 disti | $35 → **$35** | One Hour | One Hour |
| 211088 | Single Sit-On-Top Kayak Rental | D-482 ambiguous full-fare set (4 disti | $35 → **$35** | One Hour | One Hour |
| 211098 | Beach Chair Rental | D-482 ambiguous full-fare set (2 disti | $10 → **$10** | Adirondack Chair | Adirondack Chair |
| 212043 | AM 1/2 Day Private Jeep Tour St Thomas | D-485 group/charter unit (private jeep | $325 → **$325** | Private Jeep | Private Jeep |
| 212044 | PM 1/2 Day Private Jeep Tour St. Thomas | D-485 group/charter unit (private jeep | $325 → **$325** | Private Jeep | Private Jeep |
| 216194 | Private Guided Jeep Tour | D-482 ambiguous full-fare set (2 disti | $136 → **$420** | Private Group | St. Thomas | per group, up to 16 people |
| 334765 | Private St John Tour including Trunk Bay | D-485 group/charter unit (group) | $456 → **$456** | Private Group (1-3 people) | Private Group (1-3 people) |
| 334928 | Private Airport Round Trip Transportatio | D-482 ambiguous full-fare set (3 disti | $342.58 → **$228** | Emerald / Lindbergh Bay (Z1) | Emerald / Lindbergh Bay (Z1) |
| 341213 | 1.5 Hour Mini Island Jeep Tour "St Thoma | D-485 group/charter unit (private tour | $195 → **$195** | Private Tour - Number of Jeeps | Private Tour - Number of Jeeps |
| 341226 | "St Thomas" Half Day Jeep Cultural Adven | D-485 group/charter unit (private tour | $440 → **$440** | Private Tour - Number of Jeeps | Private Tour - Number of Jeeps |
| 341232 | Full Day Jeep Cultural Tour,  St. Thomas | D-485 group/charter unit (private tour | $620 → **$620** | Private Tour - Number of Jeeps | Private Tour - Number of Jeeps |
| 377230 | Jeep Wrangler | D-482 ambiguous full-fare set (27 dist | $290 → **$290** | 3 Day | 3 Day |
| 377266 | Jet Ski Rental | D-484 no asserted person unit | $140 → **$140** | Yamaha Jet Ski | Yamaha Jet Ski |
| 393873 | Zodiac | D-482 ambiguous full-fare set (2 disti | $495 → **$495** | Half Day Rental | Half Day Rental |
| 411733 | Full Day Surf & Turf Excursion | D-484 no asserted person unit (thing-t | $1100 → **$1100** | Surf N' Turf Trip | Surf N' Turf Trip |
| 411739 | Full Day Private Jeep Tour St John | D-485 group/charter unit (private tour | $549 → **$549** | Private Tour | Private Tour |
| 414292 | USVI Private Full Day | D-482 ambiguous full-fare set (2 disti | $1350 → **$1350** | Includes Up To 6 Guests | Includes Up To 6 Guests |
| 424388 | Full Day USVI Adventure | D-484 duration ladder (full day) | $1200 → **$1450** | Full Day USVI | Full Day USVI |
| 424579 | Full Day USVI Adventure | D-484 duration ladder (full day) | $50 → **$1600** | Full Day USVI | Full Day USVI |
| 438217 | Private Parasailing (Departs from Sapphi | D-482 ambiguous full-fare set (2 disti | $1000 → **$1000** | Private Parasail Trip | Private Parasail Trip |
| 438300 | Private Parasailing (Departs from St. Jo | D-482 ambiguous full-fare set (2 disti | $1100 → **$1100** | Private Parasail Trip | Private Parasail Trip |
| 509300 | Pub Krawl Tour | D-484 no asserted person unit (thing-t | $150 → **$120** | Machine | Machine |
| 509348 | Private Parasailing (Departs from Christ | D-485 group/charter unit (private para | $1000 → **$1000** | Private Parasail Trip | Private Parasail Trip |
| 529079 | Children's Botanical Garden in St. Thoma | D-485 group/charter unit (group) | $70 → **$70.15** | Group (3 People) | Group (3 People) |
| 591493 | Water Taxi  USVI -> BVI | D-482 ambiguous full-fare set (3 disti | $65 → **$900** | TO: Jost Van Dyke | per group, up to 9 people |
| 591523 | Water Taxi            BVI -> USVI | D-482 ambiguous full-fare set (4 disti | $900 → **$900** | FROM: Jost Van Dyke | FROM: Jost Van Dyke |
| 607206 | USVI Overnight Trips with CAPTAIN ONLY - | D-482 ambiguous full-fare set (5 disti | $5000 → **$5000** | Three Nights | Three Nights |
| 607223 | USVI Overnight Trips with CAPTAIN ONLY - | D-482 ambiguous full-fare set (5 disti | $5000 → **$5000** | Three Nights | Three Nights |
| 614944 | Half Day USVI - Innovation II | D-484 no asserted person unit | $995 → **$995** | Innovation 2 | Innovation 2 |
| 622386 | White Honda HRV | D-482 ambiguous full-fare set (13 dist | $85 → **$85** | One Day Rental | One Day Rental |
| 634849 | St. Thomas Half-Day Private Guided Jeep  | D-485 group/charter unit (group) | $325 → **$325** | Private Group | St. Thomas | Private Group | St. Thomas |
| 648540 | Water Taxi  USVI -> JVD for the Day! | D-484 no asserted person unit (thing-t | $1200 → **$1200** | TO: Jost Van Dyke | TO: Jost Van Dyke |
| 662320 | Multi Beach Adventure | D-484 no asserted person unit (thing-t | $500 → **$500** | Jeep | Jeep |
| 662546 | Rent A Local - New Tour! | D-484 no asserted person unit (thing-t | $500 → **$500** | Jeep | Jeep |
| 662593 | Jeep Tour + Sea Turtles | D-484 no asserted person unit (thing-t | $500 → **$500** | Jeep | Jeep |
| 662679 | Beach Rum & Beer Tour | D-484 no asserted person unit (thing-t | $500 → **$500** | Jeep | Jeep |
| 665446 | Surfboard Rentals | D-482 ambiguous full-fare set (2 disti | $75 → **$75** | One Day Rental | One Day Rental |
| 665457 | SUP Rentals | D-482 ambiguous full-fare set (2 disti | $75 → **$75** | One Day Rental | One Day Rental |

## #135 / #139 nulled rows and 11993 (machine)

| pk | name | disposition | new | label | conf |
|---|---|---|---|---|---|
| 170659 | Afternoon 2-Tank Scuba Dive | HELD:d482_ambiguous | $65 | Passenger | low |
| 274477 | Kayak Rental - Glass Bottom Kayak | D-614:repriced | $75.68 | Half Day Single Glass Bottom Kayak | high |
| 414439 | USVI Private Sunset | D-621:repriced | $675 | Includes Up To 6 Guests | high |
| 464915 | Full Day BVI Adventure | D-614:repriced | $1450 | private boat | high |
| 464969 | Full Day USVI Adventure | D-614:repriced | $1150 | private boat | high |
| 194421 | Kayak & SUP Rentals - St. Thomas | HELD:d482_ambiguous | $55 | Snorkel Gear Rental - 1 week | low |
| 439757 | Private Island Lime Out Tour | D-621:repriced | $649 | Private Tour | high |
| 624228 | BVI Full Day Charter | D-614:repriced | $1550 | private boat | high |
| 448377 | Private 37' Boston Whaler Charter | D-614:repriced | $1475 | private boat | high |
| 469720 | Private VanDutch 40' Charter | D-614:repriced | $1475 | private boat | high |
| 572332 | Caneel Beach Club Adventure | D-614:repriced | $750 | private boat | high |
| 607195 | USVI Overnight Trips with Captain & Chef | D-614:repriced | $7000 | Three Nights | high |
| 670098 | The Best of Jost Van Dyke | D-614:repriced | $1550 | Private Charter 1-6 Guests | high |
| 316901 | Private 37' Axopar Charter | D-614:repriced | $1475 | private boat | high |
| 607221 | USVI Overnight Trips with Captain & Chef | D-614:repriced | $7000 | Three Nights | high |
| 679197 | Kayak & SUP Rentals - St. Thomas - Daily | HELD:d482_ambiguous | $110 | Single Kayak Rental - 1 Day | low |
| 11993 | Private Sailing Lessons | UNSAMPLED |  |  | low |

## HELD (low, floor stamped unpublished) — s50 hold classes

| pk | name | hold | floor | ladder |
|---|---|---|---|---|
| 170668 | Sunset + Night Scuba Dive | d482_ambiguous | $90 `Snorkeler` | Diver $160 [base] / Snorkeler $90 [base] |
| 589096 | Sunset Champagne Charter 50' Luxury Voya | no_base_tier | $995 `Private Charter - Additional Guests` | Private Charter - Additional Guests $995 [never] |
| 170659 | Afternoon 2-Tank Scuba Dive | d482_ambiguous | $65 `Passenger` | Diver $160 [base] / Snorkeler $85 [base] / Passenger $65 [never] |
| 170680 | Discover Scuba Diving | d482_ambiguous | $85 `Snorkeler` | Diver $150 [base] / Snorkeler $85 [base] |
| 662575 | Secret Beaches & Caves Boat Charter | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 662702 | Private Boat Charter | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 662706 | Turtle Boat Excursion | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 662709 | St. John Boat Charter | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 662710 | Secret Beach Hike & Snorkel | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 662715 | SUP & Snorkel Tour | d482_ambiguous | $200 `Person` | Group $800 [group] / Person $200 [base] |
| 194501 | SUP Rental - St. John | d482_ambiguous | $205 `Single Kayak Rental - 1 Week` | Stand Up Paddleboard Rental - 1 Week $225 [group] / Double Kayak Rental - 1 Week $225 [group] / Single Kayak Rental - 1 Week $205 [base] |
| 377231 | SUV | d484_no_unit | $240 `3 Day` | 3 Day $240 [base_implicit] / 4 Day $320 [base_implicit] / 5 Day $415 [base_implicit] / 6 Day $503 [base_implicit] / 7 Day $575 [base_implicit] / 8 Day $680 [bas |
| 377232 | Sedan | d484_no_unit | $200 `2 Day` | 2 Day $200 [base_implicit] / 3 Day $225 [base_implicit] / 4 Day $300 [base_implicit] / 5 Day $375 [base_implicit] / 6 Day $450 [base_implicit] / 7 Day $525 [bas |
| 194421 | Kayak & SUP Rentals - St. Thomas | d482_ambiguous | $55 `Snorkel Gear Rental - 1 week` | Stand Up Paddleboard Rental - 1 Week $275 [group] / Double Kayak Rental - 1 Week $275 [group] / Single Kayak Rental - 1 Week $195 [base] / Snorkel Gear Rental - |
| 334606 | St John Island Sightseeing Tour from St  | d482_ambiguous | $79 `Adult Price (11 to 15 pax)` | Adult Price (4 to 10 Pax) $84 [base] / Adult Price (11 to 15 pax) $79 [base] / Child Price $79 [never] / Infant $0 [zero] |
| 630553 | Day Time UTV Tour | d484_no_unit | $300 `Be Driven` | You Drive $400 [base_implicit] / Be Driven $300 [base_implicit] |
| 212792 | Tropicat - Private Charter | mixed_verdict | $600 `Half Day Private Charter` | Half Day Private Charter $600 [group] |
| 591486 | Water Taxi  St Thomas -> St John | d484_no_unit | $400 `From: STT Sapphire Marina        TO:     STJ` | From: Crown Bay Marina, St Thomas $800 [base_implicit] / From: STT Sapphire Marina        TO:     STJ $400 [base_implicit] |
| 627167 | Christiansted's Artisan Shopping Tour | d482_ambiguous | $23 `Meet Up at Joyia Jewelry (Child)` | Pick Up from Carambola hotel (Adults) $115 [base] / Pick Up Frederiksted Pier (with beach) (Adults) $97 [base] / Meet Up at Joyia Jewelry (Adults) $25 [base] /  |
| 437222 | Drive Your Own UTV 4 Seater St Thomas | d484_no_unit | $369 `Drive Your Own UTV Tour` | Drive Your Own UTV Tour $369 [base_implicit] |
| 591491 | Water Taxi  St John --> St Thomas | d484_no_unit | $400 `From: St John  To: Sapphire Marina STT` | From: St John, To: Crown Bay marina, St Thomas $800 [base_implicit] / From: St John  To: Sapphire Marina STT $400 [base_implicit] |
| 679197 | Kayak & SUP Rentals - St. Thomas - Daily | d482_ambiguous | $110 `Single Kayak Rental - 1 Day` | Stand Up Paddleboard Rental - 1 Week $200 [group] / Double Kayak Rental - 1 Week $250 [group] / Single Kayak Rental - 1 Week $220 [base] / Single Kayak Rental - |
| 675760 | 26’ (Palma Bella II) Glacier Bay | mixed_verdict | $450 `Sunset Tour` | Sunset Tour $450 [group] |
| 605301 | Drive Your Own UTV 4 Seater St John | d484_no_unit | $369 `Drive Your Own UTV Tour` | Drive Your Own UTV Tour $369 [base_implicit] |
| 552937 | Guided Paddle Board Tour from Margaritav | d484_no_unit | $40 `Water Sports` | Water Sports $40 [base_implicit] |
| 358743 | Transportation | d484_unit_conflict | $18 `Public Shared Transportation One Way` | Public Shared Transportation One Way $18 [unnamed] / Public Shared Transportation Round Trip $35 [conflict] / Private Transportation Round Trip $250 [never] / S |
| 603944 | Budget Magens Bay Beach - Crown Bay and  | no_base_tier | $224.99 `Group Package (up to 6 pax)` | 15+ Groups call 1-800-679-6501 $0 [zero] / Group Package (up to 6 pax) $224.99 [never] / Group Package (7 to 10 Pax) $299.99 [never] / Group Package (11 - 15 pa |
| 652152 | NCL - St. John Beach Escape | d482_ambiguous | $50 `Empty Seat - Full Price` | Adult $88 [base] / Child $78 [never] / Empty Seat - Full Price $50 [base] |
| 663260 | Celebrity - St. John Trunk Beach Break | d484_no_unit | $60 `All Ages` | All Ages $60 [base_implicit] |

## zero_price / UNSAMPLED (machine rows)

zero_price (price null, low): 167652, 662888, 702413, 702916, 703715, 707722, 703411

UNSAMPLED (stored figure retained unpublished, low): 172285, 170675, 424721, 424727, 424742, 11993

## Render verification (node vm, both dynamic paths, renderer fixed at HEAD, data origin/main → after)

| | before | after |
|---|---|---|
| app.js all live (551) — price elements | 439 | 448 |
| app.js all live (551) — “· private boat” | 114 | 140 |
| app.js all live (551) — “per adult” | 152 | 149 |
| app.js all live (551) — Price on request | 173 | 159 |
| app.js all live (551) — unit badges | 53 | 133 |
| app.js all live (551) — schema Offer.price | 152 | 149 |
| app.js population only — “· private boat” | 100 | 126 |
| app.js population only — “per adult” | 61 | 58 |
| app.js population only — Price on request | 104 | 90 |
| app.js population only — unit badges | 0 | 80 |
| activity strip Snorkel (cards / boat / adult / unit) | 3/0/3/0 | 3/0/3/0 |
| activity strip Kayak (cards / boat / adult / unit) | 3/0/3/0 | 3/0/3/0 |
| activity strip Jet Ski Tour (cards / boat / adult / unit) | 2/0/1/0 | 2/0/1/1 |
| activity strip Fishing (cards / boat / adult / unit) | 3/3/0/0 | 3/3/0/0 |
| activity strip Zipline (cards / boat / adult / unit) | 1/0/0/0 | 1/0/0/0 |
| rows outside population — rendered bytes identical | | **True** |

## Gates

- `detect-bcvi-false-prices.sh` — clean (569248 first tripped it: the s42 BCVI ruling was not in the git-derived ledger; added as a ruling, re-applied from clean data)
- `detect-live-airport-renders.sh` — path A 0, path B 0
- `assert-nav-claims-uniformity.sh` — UNIFORMITY OK

## Static island cards (NOT in this PR — separate one-commit PR after #151)

32 population rows also have a hardcoded card on st-thomas/st-john/st-croix.html. Card figure vs the row after this PR:

| file | pk | card | row after |
|---|---|---|---|
| st-thomas.html | 149197 | Check availability | $182.5 `per adult` high — honoured:unchanged |
| st-john.html | 664103 | $995 | $1300 `private boat` high — D-621:repriced |

All other cards agree with their row. 664103's card ($995, the USVI cruise) now differs from the row ($1300 BVI cruise whole-boat — the only product on the four sampled dates); **not in this PR** — a separate one-commit PR after #151 lands.

## Caveats

- The "unicode-normalised never-anchor" is implemented as G2 above from the rule's name; no prior WUSVI/WAMS code carried it, so the exact normalisation (NFKD strip + NFKC + quote/dash fold + casefold) is this PR's reading of it.
- Honoured rows keep the ruled confidence when the figure is unchanged even on a single open reading (3 rows read $0 on 3 of 4 dates) — the s50 "1 reading → medium" rule is applied only to newly derived figures.
- `_unknownFields.priceSource: v52-dominant-gate` residue removed from 63 rows as in s50.

