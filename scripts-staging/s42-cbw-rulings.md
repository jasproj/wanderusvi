# S42 — CBW adjudicated rulings: airport-transfer hides + cruise-contract HOLD

| | |
|---|---|
| Repo | `github.com/jasproj/wanderusvi` (origin verified) |
| Branch | `cbw-rulings-s42` off `origin/main` @ `1be527c` |
| Data file | `tours-data.json` (634 tours, unchanged count) |
| Operator | CBW = `cruzbaywatersports` — 59 rows, all `company: "Cruz Bay Watersports"` |
| Adjudicated | 2026-08-22 |

## 1. Population re-derivation

CBW is keyed on the FareHarbor shortname in `bookingUrl`, not on the company
string. Both agree exactly: 59 rows under `cruzbaywatersports`, zero Cruz-Bay-named
rows under any other shortname. `tours-data.json` is the only tracked data file —
`tours-data-merged.json` and `tours-data-new.json` are gitignored and absent from
`git ls-files`.

**Airport-transfer rows: 8** (name-matched, case-insensitive `airport`). The
carried figure was 7.

| pk | name | island | price |
|---|---|---|---|
| 508266 | Private One-Way Airport Pick-Up \| SUV | st-thomas | $299 |
| 508279 | Private One-Way Airport Drop-Off \| SUV | st-john | $299 |
| 670059 | Private One-Way Airport Pick-Up \| Van | st-thomas | $299 |
| 670063 | Shared Airport Pick-Up to Frenchman's Reef \| One-Way | st-thomas | $44.95 |
| 670092 | Shared Airport Drop-Off from Frenchman's Reef \| One-Way | st-john | $44.95 |
| 670108 | Private One-Way Airport Drop-Off \| Van | st-john | null |
| 683565 | VIPDS - Airport TO Hotel • One Way | st-thomas | $270 |
| 683569 | VIPDS - Hotel TO Airport • One Way | st-thomas | $270 |

Matching is **name-only** and deliberately so: 492066 (Guided Jet Ski Tours) and
635962 (Turtles & Tacos at Lime Out) mention "airport" in their *descriptions* for
pickup logistics. A description-scoped match would sweep in two ordinary boat tours.

## 2. Delta note D-??

> **D-??** — CBW airport-transfer ruling, re-derived 2026-08-22.
>
> 1. **Roster expanded 7 → 8 on re-derive.** The carried ruling named 7 rows; the
>    tree yields 8 by name match. Adjudicated as covering the **category as
>    re-derived**, not a fixed 7-row roster. All 8 hidden.
> 2. **558638 is dual-classified.** `name` reads `"VIPDS - Group Transportation"`
>    (group transport, no airport token); `priceLabel` reads
>    `"VIPDS Buy Rate - One-Way SUV Airport Transfer"` (airport transfer). The
>    name-scoped detector does **not** match it. Hidden under the original ruling,
>    which named it explicitly — not via the category rule. If the category is ever
>    re-derived from `priceLabel` as well as `name`, the count is 9, not 8.
> 3. **Non-CBW airport rows observed, NOT adjudicated, left active** — 5 rows
>    outside the CBW population: 289236 (`viboatcharter`), 334928 / 334968 / 529773
>    (`greatexplorationtours`), 528184 (`kopromotions`). Out of scope for this
>    ruling. 289236 also carries a static card at `st-thomas.html:400`, likewise
>    untouched.

## 3. Applied changes

**Path A — dynamic grid (9 rows → `status: "inactive"`)**

508266, 508279, 670059, 670063, 670092, 670108, 683565, 683569 (the 8 airport rows)
plus 558638 (original ruling).

Each also gets a `statusReason`. The 73 pre-existing hides carry
`operator-declared-dead: … is_private=true`, which would be **false** here — these
items are live on FareHarbor and were removed on editorial scope grounds, not
because the operator delisted them. The reason string says so, and names the
reversal:

```
cbw-airport-transfer-ruling-s42: adjudicated out of catalogue scope 2026-08-22;
ground-transfer/airport product, item remains live on FareHarbor — reversible,
restore status to active to re-list
```

**Path B — static cards (2 `<article>` blocks removed from `st-john.html`)**

`status:inactive` closes path A only. `app.js:170` and `activity-tours.js:186-188`
both filter `status !== 'inactive' && !bookingDead`, but the island pages hardcode
`<article class="tour-card">` blocks that nothing filters. Two of the eight airport
rows had one:

- `st-john.html:343-354` — 670092
- `st-john.html:355-366` — 670108

Both blocks removed whole (24 lines). Verified: `<article>` 20 → 18 balanced,
`<div>` 113 → 105 balanced (4 divs per card), no orphaned wrappers, no references
to either pk remain. The page's `ItemList` JSON-LD never listed either row, so
structured data needed no edit. Git history is the reversibility.

Worth recording: of the 58 distinct pks with static cards, **not one was previously
`status:inactive`** — every prior hide happened to target a row with no static card.
670092 and 670108 were the first where the flag alone would have been insufficient.

## 4. HOLD — cruise-contract items, untouched

Read-only probe, unauthenticated item API
`/api/v1/companies/cruzbaywatersports/items/{pk}/`:

| pk | name | `is_private` | 17-date availability | 180-day sweep | verdict |
|---|---|---|---|---|---|
| 652152 | NCL - St. John Beach Escape | False | 5 slots | 18 slots | live |
| 663260 | Celebrity - St. John Trunk Beach Break | False | **0 slots** | **8 slots** | live |

Dates probed: 14 consecutive from 2026-08-22 plus +30 / +60 / +90 = 17 distinct.

663260 returned **zero across all 17 dates**. That is a date verdict, not a product
verdict. Widening to a 180-day sweep at 5-day steps surfaces 8 slots — 2026-11-10,
11-25, 11-30, 12-30, 2027-01-14, 01-19, 01-24, 02-03. Its calendar simply **opens in
November**, as a cruise-contract product on winter season would. Reading the 14-day
window as "dead" would have deactivated a live product.

`price-preview` was not available as a cross-check — that path returns the FareHarbor
error page. `is_private=False` plus confirmed forward inventory is decisive without it.

**Neither row was written to.** HOLD confirmed.

## 5. Detector

`scripts-staging/detect-live-airport-renders.sh` — covers both render paths, exits 1
on any finding. Asserts **per path**, not in aggregate: a bare aggregate zero would
let a surviving static card hide behind a clean data scan.

| run | path A | path B | exit |
|---|---|---|---|
| pre-fix | 8 | 2 | 1 |
| post-fix | 0 | 0 | 0 |
| re-corrupt A (683565 → active) | 1 | 0 | 1 |
| re-corrupt B (670108 card restored) | 0 | 1 | 1 |
| after revert | 0 | 0 | 0 |

Controls drawn **before** the fix, all silent both pre- and post-fix: 10975 (Picnic
Snorkel Sail), 424875 (Buck Island Snorkel Sail), **491003 (Guided Jet Ski Tours —
has a static card at `st-john.html:340`, so it exercises path B)**, plus 492066 and
635962 which say "airport" in their descriptions. A `--only` scope on a real airport
pk still fires, so the silent controls are not a broken flag.

Both re-corruptions were reverted before commit; `cmp` confirms both files
byte-identical to their pre-corruption state.
