#!/usr/bin/env bash
# Detector: CBW airport-transfer rows that still RENDER LIVE on the built site.
#
# Two render paths exist, and status:inactive only closes one of them:
#   (A) dynamic grid  — app.js:170 and activity-tours.js:186-188 both drop
#                       `status === 'inactive'` and `bookingDead` rows, so a
#                       hidden tours-data.json row emits nothing.
#   (B) static card   — hardcoded <article class="tour-card"> blocks in the
#                       island .html pages. These are NOT filtered by anything;
#                       status:inactive is invisible to them.
#
# A row is a FINDING when it is an airport transfer AND reachable by either path.
# Exit 1 on any finding, 0 when clean.
#
# Usage:
#   detect-live-airport-renders.sh            # whole CBW population
#   detect-live-airport-renders.sh --only PK  # scope to one pk (control runs)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHORTNAME="cruzbaywatersports"
TOURS_FILE="$REPO_ROOT/tours-data.json"

# Airport-transfer name pattern. Deliberately name-only: descriptions mention
# "airport" for pickup logistics on ordinary boat tours (492066, 635962), and
# matching those would make the detector fire on the control.
AIRPORT_RE='[Aa]irport'

# --- path A: dynamic grid rows ------------------------------------------------
scan_data_rows() {
    local only="$1"
    python3 - "$TOURS_FILE" "$SHORTNAME" "$AIRPORT_RE" "$only" <<'PY'
import json, re, sys
tours_file, shortname, airport_re, only = sys.argv[1:5]
with open(tours_file) as fh:
    tours = json.load(fh)["tours"]
pat = re.compile(airport_re)
for t in tours:
    url = t.get("bookingUrl") or ""
    m = re.search(r"fareharbor\.com/embeds/book/([^/]+)/", url)
    if not m or m.group(1) != shortname:
        continue
    if only and str(t.get("pk")) != only:
        continue
    if not pat.search(t.get("name") or ""):
        continue
    if t.get("status") == "inactive" or t.get("bookingDead"):
        continue
    print("DATA\t%s\t%s" % (t.get("pk"), t.get("name")))
PY
}

# --- path B: static island-page cards -----------------------------------------
scan_static_cards() {
    local only="$1"
    local hits
    hits="$(grep -rIn --include='*.html' \
        "data-tour-name=\"[^\"]*${AIRPORT_RE}" "$REPO_ROOT" \
        --exclude-dir=.git 2>/dev/null || true)"
    [ -z "$hits" ] && return 0

    local line file lineno pk name
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        file="${line%%:*}"
        lineno="$(printf '%s' "$line" | cut -d: -f2)"
        pk="$(printf '%s' "$line" | sed -n 's/.*data-tour-id="\([0-9]*\)".*/\1/p')"
        name="$(printf '%s' "$line" | sed -n 's/.*data-tour-name="\([^"]*\)".*/\1/p')"
        # Only CBW cards are in scope for this ruling.
        printf '%s' "$line" | grep -q "embeds/book/${SHORTNAME}/" || continue
        [ -n "$only" ] && [ "$pk" != "$only" ] && continue
        printf 'STATIC\t%s\t%s\t%s:%s\n' "$pk" "$name" "${file#$REPO_ROOT/}" "$lineno"
    done <<< "$hits"
}

main() {
    local only=""
    if [ "${1:-}" = "--only" ]; then
        only="${2:-}"
    fi

    # Per-path accounting. An aggregate zero is not enough: status:inactive
    # closes path A only, so "clean" has to be asserted on A and B separately
    # or a surviving static card hides behind a clean data scan.
    local data_hits static_hits data_n static_n
    data_hits="$(scan_data_rows "$only")"
    static_hits="$(scan_static_cards "$only")"
    data_n="$(printf '%s' "$data_hits" | grep -c . || true)"
    static_n="$(printf '%s' "$static_hits" | grep -c . || true)"

    echo "DETECTOR${only:+ (scope pk=$only)}: path A (dynamic grid) = $data_n, path B (static cards) = $static_n"

    if [ "$data_n" -eq 0 ] && [ "$static_n" -eq 0 ]; then
        echo "  CLEAN — zero live CBW airport-transfer renders on BOTH paths."
        return 0
    fi

    [ "$data_n" -gt 0 ] && printf '%s\n' "$data_hits" | sed 's/^/  /'
    [ "$static_n" -gt 0 ] && printf '%s\n' "$static_hits" | sed 's/^/  /'
    echo "  FAIL — $((data_n + static_n)) live render(s)."
    return 1
}

main "$@"
