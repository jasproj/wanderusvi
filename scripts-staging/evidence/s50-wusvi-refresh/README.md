# S50 — WUSVI price-stamp refresh: 267 rows, 53 shortnames
| | |
|---|---|
| Base | origin/main `3ec0164` (PR #147 squash) |
| Stamped | `2026-08-26T00:31:18.695Z` |
| Population | 267 (frozen in population.json; evidence < 2026-08-01, live, not s42–s49 ruled, not s40 HOLD) |
| Probe | price-preview/per-item/v2, include_breakdown=yes, dates 2026-09-05, 2026-09-19, 2026-10-03, 2026-10-24, ≤20 pks/req, 1 req/s, 220 requests, 0 retries, 0 errors, reconcile 267/267 |
| Rows changed | 267 / 267, 0 outside population (sha-asserted), stale `_unknownFields.priceSource` residue removed on 19 |
| tours-data.json sha256 | before `df190a9002a348e5…` → after `51d698d7f74af235…` |
## Dispositions

| disposition | n |
|---|---|
| UNSAMPLED | 120 |
| D-624:unchanged | 39 |
| D-624:repriced | 23 |
| HELD:d482_ambiguous | 22 |
| zero_price | 20 |
| HELD:mixed_verdict | 11 |
| D-621:repriced | 8 |
| D-621:unchanged | 5 |
| D-614:repriced | 5 |
| HELD:d484_no_unit | 5 |
| D-614:unchanged | 4 |
| HELD:no_base_tier | 4 |
| HELD:d484_unit_conflict | 1 |

Every population row carries the full dated stamp: `priceSource=s50-wusvi-refresh`, `priceEnrichmentSource=s50-wusvi-refresh-price-preview-v2`, `priceEnrichmentAt`, `priceEnrichmentStatus`, `priceVerifiedAt`, `priceBasis`, `priceTiers`, `priceConfidence`. Released group anchors also carry `_unknownFields.priceUnit` (PR #147 render path).

## Render verification (node vm, both paths, renderer fixed at HEAD, data before=origin/main vs after)

| | before | after |
|---|---|---|
| app.js all live (551) — price elements | 435 | 437 |
| app.js all live (551) — “· private boat” | 100 | 112 |
| app.js all live (551) — “per adult” | 148 | 123 |
| app.js all live (551) — Price on request | 187 | 202 |
| app.js all live (551) — unit badges | 0 | 23 |
| app.js all live (551) — schema Offer.price | 148 | 123 |
| app.js population only — “· private boat” | 0 | 12 |
| app.js population only — “per adult” | 87 | 62 |
| app.js population only — Price on request | 83 | 98 |
| app.js population only — unit badges | 0 | 23 |
| activity strip Snorkel (cards / boat / adult / unit) | 3/0/3/0 | 3/0/3/0 |
| activity strip Kayak (cards / boat / adult / unit) | 3/0/3/0 | 3/0/3/0 |
| activity strip Jet Ski Tour (cards / boat / adult / unit) | 2/0/1/0 | 2/0/1/0 |
| activity strip Fishing (cards / boat / adult / unit) | 3/3/0/0 | 3/3/0/0 |
| activity strip Zipline (cards / boat / adult / unit) | 1/0/0/0 | 1/0/0/0 |
| rows outside population — rendered bytes identical | | **True** |

## Released — repriced

| pk | shortname | name | stored → live | gate label | anchor tier | unit | conf |
|---|---|---|---|---|---|---|---|
| 340838 | stormypirates | Private (37' Axopar's) | 1300 → **1400** | private boat | Six Hour Private Charter (USVI only trip) | Six Hour Private Charter (USVI only trip) | high |
| 190946 | sonicchartersstthomas | 37' Intrepid with Triple 350 Yamaha Engines (Max'd Out/ | 200 → **1350** | private boat | Full Day Boat Charter | Full Day Boat Charter | high |
| 8232 | coralworldvi | Sea Lion Swim | 143 → **182.5** | per adult | Visitor |  | high |
| 274479 | seathrukayaksstcroix | Kayak Rental - Sit On Top Ocean Kayak | 64 → **64.87** | Half Day Single Sit On Top Ocean Kayak | Half Day Single Sit On Top Ocean Kayak | Half Day Single Sit On Top Ocean Kayak | high |
| 170949 | diveaquamarine | Advanced Open Water Diver Certification | 200 → **618.75** | per adult | Diver |  | high |
| 421957 | diveaquamarine | Half Day Private Charter | 277 → **995** | private boat | Private Charter | per boat, up to 20 passengers | high |
| 281741 | seathrukayaksstcroix | National Park Kayak Tour | 64 → **64.87** | per adult | Adult |  | high |
| 359074 | seathrukayaksstcroix | LED Moonlight Tour | 75 → **75.68** | per adult | Adult - Transparent Sea Thru Kayak |  | high |
| 648780 | boattingvi | Half Day Lime Out Taco Trip | 850 → **895** | private boat | 32'  Intrepid Boat (32 ft.) | 32'  Intrepid Boat (32 ft.) | high |
| 194418 | viecotours | Explore on Your Own – Mangrove Lagoon | 69 → **109** | per adult | Adult |  | high |
| 284524 | seathrukayaksstcroix | Glass Bottom Kayak Tour of Salt River Bay | 64 → **64.87** | per adult | Adult |  | high |
| 334660 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach from St. Thomas H | 77 → **70** | per adult | Adult From St. Thomas Hotels |  | high |
| 334774 | greatexplorationtours | Private St John Tour including Trunk Bay from St. John | 527 → **527.5** | Private Group (4-6 people) | Private Group (4-6 people) | Private Group (4-6 people) | high |
| 334803 | greatexplorationtours | Private St Thomas Tour with Beach and Downtown Shopping | 700 → **500** | Group of 1–5 Adults | Group of 1–5 Adults | Group of 1–5 Adults | high |
| 421802 | diveaquamarine | Full Day Private Charter | 200 → **1800** | private boat | Private Charter Full day | Private Charter Full day | high |
| 336074 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach From St. John Cru | 35 → **35.46** | per adult | Adults |  | high |
| 57772 | cruzbaywatersports | PiZZA Pi Snorkel Sail | 109 → **129** | per adult | Adult |  | high |
| 498637 | firstreefsailing | VI Captained Charter - Catamaran (7 Days) | None → **11872** | private boat | Private Charter | Private Charter | high |
| 353816 | viecotours | Stand-Up Paddleboard Rentals - St. Thomas | 69 → **109** | per adult | Adult |  | high |
| 660757 | palmtreechartersvi | 36' (Last Call) Aquila Power Cat | 850 → **2500** | private boat | Luxury Full Day BVI Cruise | Luxury Full Day BVI Cruise | high |
| 10966 | cruzbaywatersports | Discover Jost Van Dyke - British Virgin Islands | 179 → **199** | per adult | Adult |  | high |
| 586128 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach From The Westin V | 40 → **40.28** | per adult | Adults |  | high |
| 586129 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach from St. John Cru | 38 → **45** | per adult | Adults |  | high |
| 605308 | seathrukayaksstcroix | Coastal Kayaking Package Tour | 156 → **156.77** | per adult | Adult - Coastal Kayak Tour |  | high |
| 11999 | cruzbaywatersports | Days End Sunset Sail | 99 → **119** | per adult | Adult |  | high |
| 353281 | cruzbaywatersports | Lime Out Snorkel Sail | 139 → **159** | per adult | Adult |  | high |
| 276276 | cruzbaywatersports | Lime Out Snorkel Sail | 129 → **149** | per adult | Adult |  | high |
| 211096 | reef2peak | Snorkel Gear Rental | 20 → **15** | Snorkel Gear- Mask/Snorkel Only | Snorkel Gear- Mask/Snorkel Only | Snorkel Gear- Mask/Snorkel Only | high |
| 12001 | cruzbaywatersports | Discover The Baths of Virgin Gorda - British Virgin Isl | 199 → **219** | per adult | Adult |  | high |
| 681082 | greatexplorationtours | Frederiksted Cruise Ship Port Shuttle to Christiansted | 20 → **20.25** | per adult | Adults |  | high |
| 538166 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach from St. Thomas - | 77 → **70** | per adult | Adults |  | high |
| 559117 | greatexplorationtours | Half-Day Excursion to Trunk Bay Beach from St. Thomas - | 82 → **75** | per adult | Adults |  | high |
| 539666 | parasailvirginislands | Private Parasailing (Departs from Havensight, St. Thoma | None → **120** | Parasailor - Depart from St. Thomas | Parasailor - Depart from St. Thomas | Parasailor - Depart from St. Thomas | high |
| 635962 | cruzbaywatersports | Turtles & Tacos at Lime Out | 159 → **149** | per adult | Adult |  | high |
| 622841 | greatexplorationtours | Budget Trunk Bay with Scenic Stops (Docks) | 38 → **38.75** | per adult | Adults 4-15 |  | high |
| 438194 | vijetboat | Private High Speed Jet Boat Tour | None → **840** | private boat | Private Charter | Private Charter | high |

## Released — unchanged (fresh stamp, same figure)

| pk | shortname | name | price | gate label | anchor tier | conf |
|---|---|---|---|---|---|---|
| 2101 | thevicat | Turtle Cove Catamaran Snorkel & Sail Adventure at Littl | 109 | per adult | Adult | high |
| 2102 | thevicat | Sunset Sail with Cocktails and Appetizers | 85 | per adult | Adult | high |
| 259438 | st-thomaswatersports | Glow Boats LED Night Kayak from The Marriott Frenchman' | 65 | per adult | Adult | high |
| 259453 | st-thomaswatersports | Turtle Cove Catamaran Snorkel & Sail Adventure to Littl | 109 | per adult | Adult | high |
| 292330 | seasthedaychartersusvi | Full Day Aboard Sailing Catamaran SY Mazu or SY Neptune | 1495 | private boat | Full Day Charter | high |
| 266857 | stormypirates | Circle St. John & Food Boat Tour (USVI only) | 220 | per adult | Person | high |
| 197271 | oceansurfari | National Park Snorkeling Excursion - 2 Locations | 75 | per adult | Adult - St. Thomas Pickup | high |
| 161648 | stormypirates | Full Day (6-8 hours) Private - 27' Hydra Sport | 1000 | private boat | Six Hour Private Charter (USVI only trip) | high |
| 30022 | brenda-n-frankosfuntours | Package #1: Sightseeing Excursion | 45 | per adult | Person | high |
| 181500 | stormypirates | 1/2 Day (4 hours) Private - 27' Hydra Sport | 800 | 1/2 day (4 hours) Buccaneer (USVI only) | 1/2 day (4 hours) Buccaneer (USVI only) | high |
| 270804 | st-thomaswatersports | Sunset Sail | 85 | per adult | Adult | high |
| 194484 | viecotours | Kayak & Snorkel with Sea Turtles, National Park, St. Jo | 119 | per adult | Adult | high |
| 270790 | st-thomaswatersports | SUNSET & Harbor Lights Dinner Sail | 109 | per adult | Adult | high |
| 72784 | toursandwatersportsinthevirginislands | Cocktail Sunset Cruise from Sapphire Beach Resort | 110 | per adult | Adult | high |
| 191573 | tropicaltreasurehunt | Ghosts of Piracy Past | 175 | per adult | Adult | high |
| 194391 | viecotours | Mangrove Best of Kayak, Hike & Snorkel Tour 5 Hours -   | 199 | per adult | Adult | high |
| 608195 | toursandwatersportsinthevirginislands | Midday Snorkel Tour from Margaritaville Resort | 125 | per adult | Adult | high |
| 194410 | viecotours | Night Kayak Tour | 69 | per adult | Adult | high |
| 194395 | viecotours | Cas Cay Kayak, Hike & Snorkel Adventure Tour 3 Hours -  | 139 | per adult | Adult | high |
| 194404 | viecotours | Mangrove Adventure Kayak & Snorkel Tour 2.5 Hours - St. | 129 | per adult | Adult | high |
| 671870 | viecotours | Sunset Kayak Tour – Golden Hour Paddle from Cruz Bay, S | 49 | per adult | Adult | high |
| 651635 | viecotours | Best of St. John: Kayak, Snorkel and Picnic Adventure | 159 | per adult | Adult | high |
| 558582 | boattingvi | Pizza Boat Afternoon | 750 | private boat | 32'  Intrepid Boat (32 ft.) | high |
| 369332 | wharfsidewatersports | Medline 9 | 1250 | Full Day Rental | Full Day Rental | high |
| 662601 | stthomasadventures | Island Jeep Excursion | 500 | Jeep | Jeep | high |
| 426719 | viecotours | Snorkel with Sea Turtles - St. John | 99 | per adult | Adult | high |
| 194491 | viecotours | St. John Eco Hike & Snorkel with Sea Turtles | 99 | per adult | Adult | high |
| 255689 | tropicaltreasurehunt | Magic Portal Treasure Hunt | 109 | per adult | Adult | high |
| 334632 | greatexplorationtours | Round-Trip Transportation to Coral World Park and Coki  | 50 | per adult | Adults | high |
| 194408 | viecotours | Sunset Kayak Tour - St. Thomas | 99 | per adult | Adult | high |
| 584436 | stcs | Resort Beach Day Pass | 60 | per adult | Adult | high |
| 239155 | oceansurfari | Do It All Trip: Snorkel, Pizza and Sunset | 99 | per adult | Adult - St. Thomas Pickup | high |
| 289101 | oceansurfari | St James Snorkel and Pizza Party | 75 | per adult | Adult - St. Thomas Pickup | high |
| 411756 | islandbuddy-stj | AM 1/2 Day Private Jeep Tour St John | 325 | Private Tour | Private Tour | high |
| 635223 | toursandwatersportsinthevirginislands | Pizza Pi Party- Snorkel & Sunset Cruise | 165 | per adult | Adult | high |
| 334764 | greatexplorationtours | St Croix Island Tour Meet-up at Christiansted | 76 | per adult | Adults | high |
| 688676 | viecotours | Kayak Hurricane Hole – Self-Guided Kayak & Snorkel Expe | 119 | per adult | Adult | high |
| 585601 | greatexplorationtours | St John Island Sightseeing Tour From St. John Dock Near | 50 | per adult | Adults | high |
| 328502 | calypsocharters | Bad Kitty - Friday FUNday in the BVI | 200 | per adult | Adult | high |
| 109394 | wharfsidewatersports | Dinghys | 245 | private boat | Half Day: Dinghy 25HP | high |
| 212562 | calypsocharters | Bad Kitty - Best of the British Virgin Islands | 225 | per adult | Adult | high |
| 519998 | islandbuddy-stj | Underwater Scooter Rental | 200 | One Day Rental | One Day Rental | high |
| 538168 | greatexplorationtours | St John Island Sightseeing Tour from St. John Cruz Bay  | 50 | per adult | Adult Price (4 to 10 Pax) | high |
| 358083 | greatexplorationtours | Budget Trunk Bay with Scenic Stops | 38 | per adult | Adults 4-15 | high |
| 10975 | cruzbaywatersports | Picnic Snorkel Sail | 129 | per adult | Adult | high |
| 424877 | cruzbaywatersports | Pizza Pi Snorkel | 129 | per adult | Adult | high |
| 510184 | vijetboat | High Speed Jet Boat Tour- Havensight (Cruise Ship Dock) | 65 | per adult | Adult | high |
| 424878 | cruzbaywatersports | Best of St. John - Sail | Snorkel | Shop | 119 | per adult | Adult | high |

## HELD (low, floor stamped unpublished)

| pk | hold | name | stored → floor | ladder |
|---|---|---|---|---|
| 8234 | mixed_verdict | Sea Lion Encounter | 119 → 71.4 | Visitor $119 [base] / Resident $107.1 [never] / Accompanied Child $71.4 [never] / Member $107.1 [never] |
| 414427 | d482_ambiguous | USVI Private Half Day | 899 → 50 | Includes Up To 6 Guests $1049.99 [group] / Additional Passenger $50 [never] / Adult $87.5 [base] / Adult $95.45 [base] / Adult $105 [base] / Adult $116.67 [base] / Adult $131.25 [base] / Adult $150 [base] / Adult $175 [base] / Adult $210 [base] / Adult $262.5 [base] / Adult $350 [base] / Adult $525 [base] / Adult $1050 [base] |
| 162048 | d482_ambiguous | Bioluminescent Bay Kayak Tour | 75 → 32.44 | Adult - Transparent Sea Thru Kayak $75.68 [base] / Child - Transparent Sea Thru Kayak $43.25 [never] / Adult - Sit on Top Ocean Kayak $59.47 [base] / Child -  Sit on Top Ocean Kayak $32.44 [never] |
| 194495 | d482_ambiguous | Kayak & SUP Rentals - St. John | 200 → 12 | Stand Up Paddleboard Rental - 1 Week $200 [group] / Double Kayak Rental - 1 Week $250 [group] / Single Kayak Rental - 1 Week $220 [base] / Snorkel Gear Rental - 1 week $55 [group] / Snorkel Gear Rentals - 1 day $12 [group] |
| 8237 | mixed_verdict | Shark Encounter | 64 → 57.6 | Visitor $64 [base] / Resident $57.6 [never] / Member $57.6 [never] |
| 662539 | d482_ambiguous | Night Snorkel Adventure | 300 → 75 | Group $300 [group] / Person $75 [base] |
| 662582 | d482_ambiguous | Beach Break in St. Thomas | 300 → 75 | Group $300 [group] / Person $75 [base] |
| 282247 | d484_no_unit | Full Size SUV | None → 330 | 3 Day $330 [base_implicit] / 4 Day $440 [base_implicit] / 5 Day $550 [base_implicit] / 6 Day $660 [base_implicit] / 7 Day $770 [base_implicit] / 8 Day $880 [base_implicit] / 9 Day $990 [base_implicit] / 10 Day $1090 [base_implicit] / 11 Day $1200 [base_implicit] / 12 Day $1310 [base_implicit] / 13 Day $1420 [base_implicit] / 14 Day $1530 [base_implicit] / 15 Day $1640 [base_implicit] / 16 Day $1750 [base_implicit] / 17 Day $1860 [base_implicit] / 18 Day $1970 [base_implicit] / 19 Day $2080 [base_implicit] / 20 Day $2190 [base_implicit] / 21 Day $2300 [base_implicit] / 22 Day $2410 [base_implicit] / 23 Day $2520 [base_implicit] / 24 Day $2630 [base_implicit] / 25 Day $2740 [base_implicit] / 26 Day $2850 [base_implicit] / 27 Day $2960 [base_implicit] / 28 Day $3070 [base_implicit] / 29 Day $3180 [base_implicit] / 30 Day $3290 [base_implicit] / 31 Day $3400 [base_implicit] |
| 615474 | d484_no_unit | Elopement & Engagement Photography | 750 → 750 | One Hour Photo Session $750 [base_implicit] / Two Hour Photo Session $1500 [base_implicit] / Three Hour Photo Session $2250 [base_implicit] / Four Hour Photo Session $3000 [base_implicit] / Five Hour Photo Session $3750 [base_implicit] |
| 615491 | d484_no_unit | Family & Couples Photoshoots | 750 → 750 | One Hour Photo Session $750 [base_implicit] / Two Hour Photo Session $1500 [base_implicit] / Three Hour Photo Session $2250 [base_implicit] / Four Hour Photo Session $3000 [base_implicit] / Five Hour Photo Session $3750 [base_implicit] |
| 170656 | d482_ambiguous | Morning 2-Tank Scuba Dive | 271 → 65 | Diver $160 [base] / Passenger $65 [base] |
| 10995 | mixed_verdict | Days End Sunset Sail | 69 → 49 | Adult $89 [base] / Child $49 [never] / Adult $89 [base] / Child $59 [never] |
| 334293 | d484_no_unit | The Salty Piracy Adventure | 349 → 349 | Land and Sea Treasure Hunter $349 [base_implicit] |
| 341630 | d482_ambiguous | St John Island Sightseeing Tour - West Indian | 84 → 78 | Adult Price (4 to 10 Pax) $80 [base] / Adult Price (11 to 15 pax) $78 [base] / Child Price $78 [never] |
| 334622 | d482_ambiguous | St. Thomas and St. John Two Day Tour | 146 → 131.61 | Adult 3-6 $146.99 [base] / Adult 2-2 $148.49 [base] / Adult 7-15 $131.61 [base] |
| 334589 | d482_ambiguous | St John Island and Trunk Bay Beach Tour - Mee | 63 → 53 | Adult Price (4 to 4 Pax) $63 [base] / Adult Price (5 to 15 Pax) $58 [base] / Child Price $53 [never] |
| 341844 | no_base_tier | Budget Magens Bay Beach | 224 → 224.99 | Group Package (up to 6 pax) $224.99 [never] / Group Package (7 to 10 Pax) $299.99 [never] / Group Package (11 - 15 pax) $493.42 [never] |
| 630592 | d484_no_unit | Night Time UTV Tour | 500 → 400 | You Drive $500 [base_implicit] / Be Driven $400 [base_implicit] |
| 585279 | d482_ambiguous | St John Island and Trunk Bay Beach Tour From  | 65 → 55 | Adult Price (4 to 4 Pax) $65 [base] / Adult Price (5 to 15 Pax) $60 [base] / Child Price $55 [never] |
| 585280 | d482_ambiguous | St John Island and Trunk Bay Beach Tour From  | 65 → 55 | Adult Price (4 to 4 Pax) $65 [base] / Adult Price (5 to 15 Pax) $60 [base] / Child Price $55 [never] |
| 10949 | mixed_verdict | Discover The Baths of Virgin Gorda - British  | 179 → 129 | Adult $179 [base] / Child $129 [never] / Adult $199 [base] |
| 11995 | mixed_verdict | Discover Jost Van Dyke - British Virgin Islan | 199 → 169 | Adult $219 [base] / Child $169 [never] / Adult $219 [base] |
| 558412 | d482_ambiguous | St. Thomas Island Tour with Mountain Top & Ma | 45 → 67 | Adult (pricing for 2-10 pax) $72 [base] / Adult (Pricing for 11 - 15 pax) $67 [base] |
| 558413 | d482_ambiguous | St. Thomas Island Tour with Mountain Top & Ma | 65 → 30 | Infant $30 [never] / Adult 2-3 $65 [base] / Adult 4-15 $58 [base] |
| 559118 | d482_ambiguous | St John Island Sightseeing Tour - Crown Bay D | 89 → 84 | Adult Price (4 to 10 Pax) $89 [base] / Adult Price (11 to 15 pax) $84 [base] / Child Price $84 [never] |
| 671029 | mixed_verdict | Cruise Ship Port Shuttle to St John Ferry | 25 → 45 | Child Price $45 [never] / Adult 4-15 $48.75 [base] |
| 589442 | d482_ambiguous | Island Eco Farm Tour with Local Treats and Sa | 68 → 14.82 | Adults $85 [base] / Adults $85 [base] / Child Price $62 [never] / Adult - Wenner Farm Meet-up (Farm Tour only - No Beach) $19.76 [base] / Children - Wenner Farm Meet-up (Farm Tour only - No Beach) $14.82 [never] |
| 628803 | d482_ambiguous | Island Chocolate Experience with Tasting | 82 → 27.74 | Pickup Pier Tasting (Adult) $68.24 [base] / Pickup Pier Tasting (Child) $56.99 [never] / Meet Up Chocolate Tasting (Adult) $32.24 [base] / Meet Up Chocolate Tasting (Child) $27.74 [never] |
| 11996 | mixed_verdict | Dinner Sail to St. John | 119 → 89 | Adult $139 [base] / Child $89 [never] / Adult $139 [base] / Child $99 [never] |
| 334596 | d482_ambiguous | St John Island and Trunk Bay Beach Tour - St. | 93 → 83 | Adult (Groups of 4-10) $93 [base] / Adult (Groups of 11-15) $88 [base] / Child (Group of 1-13) $83 [never] |
| 538171 | d482_ambiguous | St John Island and Trunk Bay Beach Tour Pick- | 90 → 80 | Adult Price (4 to 4 Pax) $90 [base] / Adult Price (5 to 15 Pax) $85 [base] / Child Price $80 [never] |
| 559119 | d482_ambiguous | St John Island and Trunk Bay Beach Tour - Cro | 95 → 85 | Adult Price (4 to 4 Pax) $95 [base] / Adult Price (5 to 15 Pax) $90 [base] / Child Price $85 [never] |
| 586139 | d482_ambiguous | St Croix Island Tour Pick up at Selected Hote | 90 → 85 | Adults $90 [base] / Adults $85 [base] |
| 424879 | mixed_verdict | Days End Sunset Sail | 59 → 49 | Adult $79 [base] / Child $49 [never] |
| 268925 | mixed_verdict | Maho Bay Turtle Snorkel Sail | 139 → 99 | Adult $159 [base] / Child $99 [never] / Adult $159 [base] |
| 377253 | mixed_verdict | Best of St. John Sail - Sail, Snorkel & Shop | 159 → 79 | Adult $119 [base] / Child $79 [never] / Adult $139 [base] / Child $99 [never] |
| 424875 | mixed_verdict | Buck Island Snorkel Sail | 99 → 79 | Adult $119 [base] / Child $79 [never] |
| 341846 | d482_ambiguous | Nature and Sightseeing Tour at Phantasea Trop | 42 → 10 | Adults $42.55 [base] / Adults $41.03 [base] / Adults $47.11 [base] / Adult Ticket $12 [base] / Child Ticket $10 [never] |
| 344761 | d482_ambiguous | Rainbow Beach with Round-trip Transportation  | 30 → 25 | Adults $30 [base] / Adults $25 [base] / Adults $30 [base] / Adults $25 [base] |
| 489157 | no_base_tier | VI ASA Combo Course Week- Monohull | None → 2887.44 | Private Cabin for 1 Student $3814.94 [never] / 2 Students in a Private Cabin $3655.94 [never] / 1 Student and 1 Non-Student in a Private Cabin $2887.44 [never] |
| 491881 | no_base_tier | VI ASA Single Course Week - Monohull | None → 2887.44 | Private Cabin for 1 Student $3814.94 [never] / 2 Students in a Private Cabin $3655.94 [never] / 1 Student and 1 Non-Student in a Private Cabin $2887.44 [never] |
| 575294 | no_base_tier | VI ASA Combo Course Week- Catamaran | None → 3418.5 | Private Cabin for 1 Student $4344.94 [never] / 2 Students in a Private Cabin $4187 [never] / 1 Student and 1 Non-Student in a Private Cabin $3418.5 [never] |
| 489164 | d484_unit_conflict | VI Captained Charter - Monohull  (7 Days) | None → 10174.94 | Private Charter $10174.94 [conflict] |

## zero_price (price null, low)

289236, 30072, 416943, 672351, 108035, 334968, 601021, 529773, 601328, 413523, 616139, 75237, 632923, 720341, 720352, 450343, 450354, 653593, 718756, 387127

## UNSAMPLED (120; stored figure retained, low; 37 were also DEAD in the s40 probe — empty availability is a date verdict)

601988, 602579, 266651, 601985, 602576†, 601987†, 170950, 211109†, 211099†, 416942, 211118†, 211131†, 442936, 484579, 484583†, 484584†, 667405, 344830, 591534, 170944, 76469, 211126†, 483423, 448258†, 622183†, 622387†, 622389†, 622391†, 622393†, 622395†, 622399†, 622401, 519046, 519070, 621994, 622002, 170676†, 622009, 98820†, 519075, 590716, 642428, 143803, 211116, 509655, 211114†, 337950, 521254†, 416907†, 487206†, 487208†, 554947†, 587820, 262055, 587814†, 619238, 490938, 589438, 71433, 667020, 194130†, 399480†, 276913†, 399468†, 399477†, 731034†, 170940, 221392, 236042, 521251, 653575, 423603, 443551, 445669, 271749†, 231376, 163387, 172853, 458346, 458352, 505196, 407382†, 578839, 552940, 560048, 545175, 341008, 526262, 560111, 560124, 12128, 271721, 12127†, 23304†, 428052, 11864, 268609, 483402, 490993, 667058, 490987, 628556, 667051, 728250, 251910, 324457, 337310, 343591, 351538, 358030, 432765, 574927, 195725, 622015, 489595, 488909, 629937, 528184, 483293, 664660†

† s40-DEAD

## Caveats

- Non-vessel group anchors (Jeep, Private Tour, rentals, parasail — 10 rows) are stamped with the tier label verbatim + priceUnit; the gate renders them as “Price on request” with the unit badge, never as a seat price (#144 UNIT_NOT_VESSEL).
- Single-reading releases are `medium`: renders for per adult, not for private boat.
- 43 held rows (D-482 22, mixed 11, D-484 5 + 1 unit-conflict, no-base 4) keep their floor as `price` with `priceConfidence: low`; the gate does not render low.
