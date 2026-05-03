# wanderusvi v5.2 Null-Price Dry-Run Report — null-price tour re-extraction

**Generated:** 2026-05-03T20:35:56.680Z
**Branch:** `feat/usvi-v52-null-price-rescrape`
**Mode:** `--dry-run-only` (no writes to tours-data.json)

## 1. Inputs

- wanderusvi total tours: 465
- Tours with `price: null` evaluated: **148**
- Extractor: v5.4 baseline + v5.2 dominant-price gate (ported verbatim from wanderusvi)
- Page fetch: Playwright (chromium headless), 1.5 s settle wait

## 2. Result distribution

| Outcome | Count | Disposition |
|---|---:|---|
| **high** (v5.4 Method 1/2 — adult/per-person anchor) | 3 | "From $X" if applied |
| **medium** (v5.4 native — Method 3/4/6) | 18 | "From $X" if applied |
| **medium** (v5.2 dominant-price gate) | 23 | "From $X" if applied |
| **low** (Method 5 unanchored, gate FAILed) | 3 | stays "Check availability" |
| **no-price** (extractor returned null) | 101 | stays "Check availability" |
| **error** (fetch/parse) | 0 | stays "Check availability" |
| **Total** | 148 | |

**Net effect if applied --live:** 44 tours flip from "Check availability" → "From $X" (29.7% of the 148). 104 stay hidden.

## 3. Cat-E candidate sanity check

**0 Cat-E candidates** detected among gate PASSes. Disqualifier blocklist (`additional, extra, option, optional, rental, nitrox, upgrade, supplement, add-on, addon, surcharge` + `+$` literal) appears to be holding.

## 4. Sample 10 promoted tours

### 110165 — Turtles, Pizza Pi & Sunset (USVI only)

- company: Stormy Pirates Boat Charters
- extracted price: **$220** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [220]
- gate matched token: `$220`
- gate ±40 char window:

  ```
  to TripAdvisor travelers as of May 2026 $220 People All Ages Welcome! Prices for Tue
  ```
- all $-hits in page: ["$220"]

### 704467 — Sunset Power Catamaran

- company: One Caribbean Charters
- extracted price: **$1950** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [1950]
- gate matched token: `$1,950`
- gate ±40 char window:

  ```
   TripAdvisor travelers as of April 2026 $1,950 Sunset Cruise Prices for Tuesday, May 5
  ```
- all $-hits in page: ["$1,950"]

### 509348 — Private Parasailing (Departs from Christiansted, St. Croix)

- company: Parasail Virgin Islands
- extracted price: **$1000** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [1000]
- gate matched token: `$1,000`
- gate ±40 char window:

  ```
  commended 4.9 stars 1809 Google reviews $1,000 Private Parasail Trip Please Select The
  ```
- all $-hits in page: ["$1,000"]

### 438217 — Private Parasailing (Departs from Sapphire Beach Marina, St. Thomas)

- company: Parasail Virgin Islands
- extracted price: **$1000** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [0,1000]
- gate matched token: `$1,000`
- gate ±40 char window:

  ```
  commended 4.9 stars 1809 Google reviews $1,000 Private Parasail Trip Please Select The
  ```
- all $-hits in page: ["$1,000","$0","$0"]

### 630359 — Island Hopping Yacht Party

- company: Island Tour Connect
- extracted price: **$2200** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [2200]
- gate matched token: `$2,200`
- gate ±40 char window:

  ```
  • 3 or 7 Hours • Island hopping Charter $2,200 Half Day Prices for Tuesday, May 5, 202
  ```
- all $-hits in page: ["$2,200"]

### 660734 — 42' (Top Shelf) Freeman Power Catamaran

- company: Palm Tree Charters
- extracted price: **$3500** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [3500]
- gate matched token: `$3,500`
- gate ±40 char window:

  ```
  ss. Prices Go Fast Full Day BVI Cruise: $3,500 Go Fast Full Day USVI Cruise: $3,500 Ca
  ```
- all $-hits in page: ["$3,500","$3,500"]

### 630355 — Island Hopping Boat Charter

- company: Island Tour Connect
- extracted price: **$1200** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [1200]
- gate matched token: `$1,200`
- gate ±40 char window:

  ```
  • 3 or 7 Hours • Island hopping Charter $1,200 Half Day Prices for Tuesday, May 5, 202
  ```
- all $-hits in page: ["$1,200"]

### 411733 — Full Day Surf & Turf Excursion

- company: Island Buddy - STJ
- extracted price: **$1100** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [1100]
- gate matched token: `$1,100`
- gate ±40 char window:

  ```
  y Island Tour + Half Day Boat Charter | $1,100 | Call to Book Activity details The ult
  ```
- all $-hits in page: ["$1,100","$1,100"]

### 662546 — Rent A Local - New Tour!

- company: St. Thomas Adventures
- extracted price: **$500** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [500]
- gate matched token: `$500`
- gate ±40 char window:

  ```
   TripAdvisor travelers as of April 2026 $500 Jeeps Fits up to 4 passengers Prices fo
  ```
- all $-hits in page: ["$500"]

### 662593 — Jeep Tour + Sea Turtles

- company: St. Thomas Adventures
- extracted price: **$500** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [500]
- gate matched token: `$500`
- gate ±40 char window:

  ```
   TripAdvisor travelers as of April 2026 $500 Jeeps Fits up to 4 passengers Prices fo
  ```
- all $-hits in page: ["$500"]

## 5. Sample 5 stays-hidden tours

### 627167 — Christiansted's Artisan Shopping Tour

- outcome: low
- gate criterion failed: 2
- distinct $-values: [23,25,51,53,77,79,95,97,113,115]
- all $-hits: ["$115","$97","$25","$113","$23","$79","$77","$95","$53","$51"]

### 607206 — USVI Overnight Trips with CAPTAIN ONLY - Kindred Spirit II

- outcome: low
- gate criterion failed: 2
- distinct $-values: [5000,7000,9000,11000,13000]
- all $-hits: ["$5,000","$7,000","$9,000","$11,000","$13,000"]

### 607223 — USVI Overnight Trips with CAPTAIN ONLY - Intrepid

- outcome: low
- gate criterion failed: 2
- distinct $-values: [5000,7000,9000,11000,13000]
- all $-hits: ["$5,000","$7,000","$9,000","$11,000","$13,000"]

### 476450 — Sunset/Night Snorkel

- outcome: no-price

### 440447 — Glow Boats LED Night Kayak from The Marriott's Frenchman's Cove, USVI

- outcome: no-price

## 6. Out of scope for this run

- No edits to `tours-data.json`.
- No commits, no push, no deploy.
- `--live` mode not implemented yet — adopt USVI's `apply-v52-live.js` pattern when ready.
