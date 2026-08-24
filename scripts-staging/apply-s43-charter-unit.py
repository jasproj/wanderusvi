#!/usr/bin/env python3
"""S43 - apply the adjudicated charter-unit prices to tours-data.json.

Deterministic (D-581). The only input is the frozen ledger
scripts-staging/s43-charter-unit-adjudicated.json. Re-running on an
already-applied file reports "0 modified" and does not rewrite the file.

Python rather than node on purpose: tours-data.json carries float literals
such as 109.0, which JavaScript's JSON.stringify flattens to 109. That would
rewrite hundreds of rows this change never adjudicated. Python's json module
round-trips the file byte-for-byte (verified: sha256 unchanged on a no-op run),
so the diff contains only the rows in the ledger.

Writes EXACTLY four fields per row, #247 convention:
    price            live floor of the confirmed whole-boat tier
    priceLabel       "private boat"
    priceConfidence  "high"
    priceBreakdown   the live tier array for that row

Usage: python3 scripts-staging/apply-s43-charter-unit.py [--dry-run]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tours-data.json")
LEDGER = os.path.join(ROOT, "scripts-staging", "s43-charter-unit-adjudicated.json")

FIELDS = ("price", "priceLabel", "priceConfidence", "priceBreakdown")


def main():
    dry_run = "--dry-run" in sys.argv

    with open(LEDGER, encoding="utf-8") as fh:
        ledger = json.load(fh)
    with open(DATA, encoding="utf-8") as fh:
        doc = json.load(fh)

    by_pk = {int(t["pk"]): t for t in doc["tours"]}

    modified, unchanged, missing = 0, 0, 0
    for row in ledger["rows"]:
        tour = by_pk.get(int(row["pk"]))
        if tour is None:
            missing += 1
            print("  pk %s: not in tours-data.json - skipped" % row["pk"])
            continue
        before = [tour.get(f) for f in FIELDS]
        for f in FIELDS:
            tour[f] = row[f]
        if before == [tour.get(f) for f in FIELDS]:
            unchanged += 1
        else:
            modified += 1

    print("ledger rows: %d" % len(ledger["rows"]))
    print("  modified : %d" % modified)
    print("  unchanged: %d" % unchanged)
    print("  missing  : %d" % missing)

    if dry_run:
        print("\n--dry-run: tours-data.json not written")
        return
    if modified == 0:
        print("\nno change - tours-data.json not rewritten")
        return

    with open(DATA, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print("\nwrote %s" % DATA)


if __name__ == "__main__":
    main()
