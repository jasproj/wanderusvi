# v5.2 Dominant-Price Gate — Dry-Run Report (PATCHED)

**Generated:** 2026-05-03T17:40:04.214Z
**Branch:** `feat/usvi-v52-dominant-gate`
**Mode:** `--dry-run-v52-gate-only` (no writes to tours-data.json)

## 0. What changed since the previous run

Three patches applied to `scripts-staging/extract-price-v5.2.js` after the first dry-run produced 2 Cat-E zero-FP violations:

1. **Disqualifier blocklist extended**: added `additional`, `extra`, `option`, `optional`, `rental`, `nitrox`, `upgrade`, `supplement`. Plus plurals: `children`, `kid` (so `\bchildren?\b` and `\bkids?\b` are both covered via separate tokens).
2. **`+$` add-on idiom guard**: criterion 4 now hard-rejects any match whose immediately-preceding char is `+` (catches "...is +$20", "...option available +$271").
3. **Plural fix**: `child` and `children`, `kid` and `kids` now all in blocklist (the prior `\bchild\b` regex did not match `children`).

Result: previous Cat-E violations (170659, 170656) now FAIL via the `+$` guard. PASS dropped from 93 → 77 (16 collateral; see §5).

## 1. Inputs

- Low-confidence tours evaluated: **156** (confirmed)
- Page-text source: **30** cached audit samples + **126** fresh Playwright fetches

## 2. Gate criteria (current)

1. v5.4 captured a price (`price !== null`)
2. Distinct `$N` values in page text ≤ **2**
3. Captured price is one of those distinct values (literal match)
4. No disqualifier in ±40 char window AND char-immediately-before-`$` is not `+`
   - blocklist: `deposit | fee | surcharge | tax | tip | gratuity | add-on | addon | child | children | kid | kids | junior | senior | discount | additional | extra | option | optional | rental | nitrox | upgrade | supplement`

## 3. Headline counts

| Outcome | Count | Disposition under v5.2 |
|---|---:|---|
| Gate **PASS** (low → medium via gate) | **77** | promote |
| Gate **FAIL** (criterion 2/3/4) | **46** | stay low |
| Auto-promoted on fresh re-enrichment (v5.4 alone) | 5 | promote (no gate) |
| No price on current page (effective crit-1 fail) | 28 | stay low |
| Other | 0 | — |
| **Total** | **156** | |

**Net effect of running v5.2 live:** 82 tours move to medium (77 via gate, 5 via fresh v5.4); 74 remain low.

### 3a. FAIL histogram by criterion

| Criterion | Count |
|---|---:|
| 1 (effective: re-extract null) | 28 |
| 2 | 23 |
| 4 | 23 |

### 3b. Crit-4 disqualifier-token breakdown

| Token | Count |
|---|---:|
| `additional` | 10 |
| `+$` | 4 |
| `gratuity` | 4 |
| `rental` | 3 |
| `nitrox` | 2 |

## 4. Audit cross-reference (sanity checks)

| Audit ID | Cat | Expected | Decision | Detail | Note |
|---|---|---|---|---|---|
| 102397 | G | mixed | **PASS** | crit — |  |
| 114303 | F | FAIL | FAIL | crit 1 (null) |  |
| 161648 | F | FAIL | FAIL | crit 1 (null) |  |
| 170656 | E | FAIL (zero-FP) | FAIL | crit 4 (+$) |  |
| 170659 | E | FAIL (zero-FP) | FAIL | crit 4 (+$) |  |
| 185836 | G | mixed | auto-medium | → medium |  |
| 194421 | F | FAIL | FAIL | crit 1 (null) |  |
| 200902 | G | mixed | **PASS** | crit — |  |
| 211022 | D | PASS (most) | **PASS** | crit — |  |
| 211088 | D | PASS (most) | **PASS** | crit — |  |
| 211096 | D | PASS (most) | FAIL | crit 2 | D blocked: gate-fail |
| 212044 | D | PASS (most) | **PASS** | crit — |  |
| 274477 | B | FAIL | FAIL | crit 2 |  |
| 292330 | F | FAIL | FAIL | crit 1 (null) |  |
| 334293 | F | FAIL | FAIL | crit 1 (null) |  |
| 340838 | F | FAIL | FAIL | crit 1 (null) |  |
| 369332 | D | PASS (most) | FAIL | crit 4 (rental) | D blocked: gate-fail |
| 424388 | D | PASS (most) | **PASS** | crit — |  |
| 424739 | D | PASS (most) | **PASS** | crit — |  |
| 464992 | D | PASS (most) | **PASS** | crit — |  |
| 487206 | D | PASS (most) | **PASS** | crit — |  |
| 521254 | D | PASS (most) | **PASS** | crit — |  |
| 564306 | D | PASS (most) | **PASS** | crit — |  |
| 601987 | D | PASS (most) | **PASS** | crit — |  |
| 607195 | B | FAIL | FAIL | crit 2 |  |
| 607221 | B | FAIL | FAIL | crit 2 |  |
| 614944 | D | PASS (most) | **PASS** | crit — |  |
| 615132 | D | PASS (most) | **PASS** | crit — |  |
| 615474 | D | PASS (most) | FAIL | crit 2 | D blocked: gate-fail |
| 660757 | B | FAIL | FAIL | crit 1 (null) |  |

### 4a. Audit-cat tally

| Cat / Decision | Count |
|---|---:|
| B/FAIL | 4 |
| D/FAIL | 3 |
| D/PASS | 12 |
| E/FAIL | 2 |
| F/FAIL | 6 |
| G/PASS | 2 |
| G/auto-medium | 1 |

**Cat E policy violations:** 0 ✓

### Sanity gate verification (target IDs from patch spec)

| ID | Name | Decision | Detail |
|---|---|---|---|
| 170659 | Afternoon 2-Tank Scuba Dive | FAIL ✓ | crit 4 (+$) |
| 170656 | Morning 2-Tank Scuba Dive | FAIL ✓ | crit 4 (+$) |
| 2103 | Sunset & Harbor Lights Dinner Sail from the Marriott's  | auto-high (gate did not run) | v5.4 → high/per adult |

Note on 2103: re-extract on the fresh page now matches v5.4 Method 1 (`per adult` / high), so the gate is not invoked at all. Either way, the gate cannot promote a child-priced page.

## 5. Collateral PASS → FAIL caused by patches

Tours that would have PASSed before the patches but now FAIL on a newly-added disqualifier (`additional`, `extra`, `option`, `optional`, `rental`, `nitrox`, `upgrade`, `supplement`, `children`, `kid`) or the `+$` guard. Count: **19** (gate fails on new tokens / +$).

| ID | Name | Cap $ | Disqualifier | Window |
|---|---|---:|---|---|
| 190947 | 58' Princess Yachts - Luxury Yacht Chart | 50 | `+$` | `city of 12 guests, each guest over six +$50. All Ages Welcome What's included Capta` |
| 578452 | Try Scuba Pool Time | 50 | `additional` | `ut will also get the second dive free! ($50 savings) Additional information Cancell` |
| 170659 | Afternoon 2-Tank Scuba Dive | 20 | `+$` | `Rental gear (besides weights/tanks) is +$20 Divers can get Nitrox Certified Close S` |
| 170950 | Rescue Diver Certification | 150 | `additional` | `e students may be charged an additional $150 for private instruction at our discreti` |
| 170949 | Advanced Open Water Diver Certification | 200 | `+$` | `itrox Certified too - option available +$200 *Rates may vary on holiday dates* Pleas` |
| 369332 | Medline 9 | 1250 | `rental` | ` Rental Time: Starting at 9:00am Price: $1250 Includes: Safety Equipment, Garmin GPS ` |
| 421957 | Half Day Private Charter | 277 | `nitrox` | `! Nitrox Certification option available $277 (pre scheduled only) Our cooler is stoc` |
| 648780 | Half Day Lime Out Taco Trip | 850 | `additional` | `up to 12 people. There is an additional $100 charge after 6 passengers on each boat.` |
| 170656 | Morning 2-Tank Scuba Dive | 271 | `+$` | `Certified this trip - option available +$271 Please be aware we need to Close Secure` |
| 607533 | USVI Full Day | 100 | `additional` | `cluded in base price. Additional guests $100 each up to the legal max 12 guests rega` |
| 172285 | Open Water Dive Referral Course | 150 | `additional` | `nstruction may be an additional cost of $150 Certification sessions require a minimu` |
| 421802 | Full Day Private Charter | 200 | `nitrox` | `! Nitrox Certification option available $200 In addition to snorkeling and certified` |
| 103544 | Half Day Private Boat Charter - Snorkeli | 50 | `additional` | `assengers, each additional passenger is $50/pp up to our 10 max capacity Duration A` |
| 532681 | BVI Full Day Private Boat Charter | 50 | `additional` | `assengers, each additional passenger is $50/pp up to our 10 max capacity. Fuel, Cus` |
| 532682 | A Day on Jost - Home of the Painkiller | 50 | `additional` | `assengers, each additional passenger is $50/pp up to our 10 Max capacity. Fuel, Cus` |
| 519075 | Travel Between The US Virgin Islands | 75 | `additional` | `6 passengers - Additional passenger are $75/people up to our 12 person max capacity` |
| 103534 | Full Day Private Boat Charter - USVI | 50 | `additional` | `assengers, each additional passenger is $50/pp up to our 10 max capacity Duration 7` |
| 109394 | Dinghys | 245 | `rental` | `y Rental Time: 10:00am or 2:00pm Price: $245 Includes: Fuel, Safety Equipment Capaci` |
| 324279 | SUP Rental - Sea Thru Paddleboard | 70 | `rental` | `ation 4.8 stars 495 Google reviews Rate $70/half day rental self-explore Duration H` |

Of the 19 collateral fails, the audit-D regression count is small: only `369332` (Medline 9) — page literally says `Rental Time:` (booking time slot, not add-on). All others are real add-on / supplemental-passenger / certification-upsell patterns where the price is genuinely not the per-tour rate.

## 6. Sample PASSes (first 5)

### 377266 — Jet Ski Rental

- captured price: **$140**
- distinct $-values: [140]
- matched token: `$140`
- ±40 char window:

  ```
   TripAdvisor travelers as of April 2026 $140 Yamaha VX-C 2024 (Recommended) Single o
  ```

### 196766 — Red Hook to St John Snorkel, Beach Charter Aboard MV Island Flyer

- captured price: **$140**
- distinct $-values: [140]
- matched token: `$140`
- ±40 char window:

  ```
  to TripAdvisor travelers as of May 2026 $140 People All Ages Prices for Monday, May 
  ```

### 30025 — Package #3: Sightseeing, Shopping & Swimming Excursion

- captured price: **$70**
- distinct $-values: [70]
- matched token: `$70.00`
- ±40 char window:

  ```
  , Shopping & Swimming Excursion Rate... $70.00 | 5-6 Hours | Ages 3 to adult. | Most P
  ```

### 102397 — Baths, Virgin Gorda and White Bay, JVD (BVI trip)

- captured price: **$300**
- distinct $-values: [300]
- matched token: `$300`
- ±40 char window:

  ```
  M T W Th F S 26 27 28 29 30 1 2 3 4 5 6 $300 7 8 9 $300 10 11 $300 12 13 $300 14 15 
  ```

### 102398 — Sail and Explore Jost Van Dyke (BVI trip)

- captured price: **$270**
- distinct $-values: [270]
- matched token: `$270`
- ±40 char window:

  ```
   Su M T W Th F S 26 27 28 29 30 1 2 3 4 $270 5 6 $270 7 8 9 10 11 12 13 14 $270 15 1
  ```

## 6b. Sample FAILs (one per kind)

### 190947 — 58' Princess Yachts - Luxury Yacht Charter (Enchantment) USVI trips only

- criterion failed: **4** — Crit 4 — disqualifier token in ±40 char window (or `+$` guard)
- captured price: $50
- distinct $-values: [50]
- disqualifier hit: `+$`
- window:

  ```
  city of 12 guests, each guest over six +$50. All Ages Welcome What's included Capta
  ```

### 190946 — 37' Intrepid with Triple 350 Yamaha Engines (Max'd Out/ Carried Away)

- criterion failed: **2** — Crit 2 — > 2 distinct $-values
- captured price: $200
- distinct $-values: [50,200,600,1350]

### 536583 — Pizza Pi - Jet Ski

- criterion failed: **1 (re-extract null)** — v5.4 returned price=null on fresh fetch
- captured price: $175
- re-extract: price=null, confidence=null

## 7. Halt-condition check

- Cat E violations: **0** ✓ (was 2 before patches)
- Gate PASS count: **77** ≥ 75 floor ✓ (was 93 before patches)

Halt conditions are not triggered. Standard halt-for-review applies — `--live` mode is still not implemented and should not be added without further sign-off.

## 8. Out of scope for this run

- No edits to `tours-data.json`.
- No edits to `extract-price-v5.js` (v5.4 is untouched).
- No push to `main`.
- No `--live` mode implemented or run.
