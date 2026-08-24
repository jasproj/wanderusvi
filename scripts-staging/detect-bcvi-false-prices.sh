#!/usr/bin/env bash
# Detector: Beach Charters VI rows storing a price that contradicts the
# live-verified whole-boat base fare.
#
# Every BCVI HOLD row resolves to a whole-boat `Private Charter` base tier
# (s42 adjudication 2026-08-22; 569248 resolved via the prose-party-condition
# branch, base = Private Charter $900). A stored per-person figure far below
# that floor is a false price: it is not a different unit reading, it matches
# no live tier at all.
#
# The floors below are the live-verified base fares from the s42 sweep —
# FareHarbor price-preview per-item v2, 17 requested dates, 174 valid readings
# after discarding 30 near-edge date-fallback readings, tier set identical
# across every valid reading for all 12 rows.
#
# A row is a FINDING when it stores a non-null price that deviates from its
# verified floor by more than TOLERANCE. Exit 1 on any finding, 0 when clean.
#
# Usage:
#   detect-bcvi-false-prices.sh            # whole BCVI HOLD batch
#   detect-bcvi-false-prices.sh --only PK  # scope to one pk (control runs)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOURS_FILE="$REPO_ROOT/tours-data.json"
TOLERANCE="0.5"   # >50% deviation from the verified floor is a false price

# pk:live-verified whole-boat base fare (USD), s42 sweep 2026-08-23
FLOORS="556346:1350
556358:900
556360:2500
556364:1300
556366:6000
557375:1250
557393:900
560835:8000
569248:900
589553:2500
719217:2400
719228:7200"

scan() {
    local only="$1"
    printf '%s\n' "$FLOORS" | python3 -c "
import json, sys
tours_file, only, tol = sys.argv[1], sys.argv[2], float(sys.argv[3])
floors = {}
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    pk, fare = line.split(':')
    floors[int(pk)] = float(fare)

with open(tours_file) as fh:
    tours = json.load(fh)['tours']
by = {t['pk']: t for t in tours}

for pk in sorted(floors):
    if only and str(pk) != only:
        continue
    row = by.get(pk)
    if row is None:
        print('MISSING\t%d\t(row absent from tours-data.json)' % pk)
        continue
    stored = row.get('price')
    if stored is None:
        continue          # retracted price cannot be false
    floor = floors[pk]
    if abs(stored - floor) / floor > tol:
        print('FALSE-PRICE\t%d\tstored \$%s %r vs live-verified whole-boat \$%.2f  (%.0fx)\t%s'
              % (pk, stored, row.get('priceLabel'), floor, floor / stored if stored else 0,
                 (row.get('name') or '')[:44]))
" "$TOURS_FILE" "$only" "$TOLERANCE"
}

main() {
    local only=""
    if [ "${1:-}" = "--only" ]; then
        only="${2:-}"
    fi

    local findings count
    findings="$(scan "$only")"
    count="$(printf '%s' "$findings" | grep -c . || true)"

    if [ "$count" -eq 0 ]; then
        echo "DETECTOR${only:+ (scope pk=$only)}: clean — no BCVI row stores a price contradicting its live-verified floor."
        return 0
    fi

    echo "DETECTOR${only:+ (scope pk=$only)}: $count false stored price(s):"
    printf '%s\n' "$findings" | sed 's/^/  /'
    return 1
}

main "$@"
