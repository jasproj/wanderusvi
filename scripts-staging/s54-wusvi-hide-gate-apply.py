#!/usr/bin/env python3
"""s54-wusvi-hide-gate — APPLY stage. Ports KWST's hidden:true render gate
(keywestsandbartours #254, 05daac7) instead of hand-disposing the 43 dark
rows (ruled: wtpa/TASKS.md "WUSVI: port KWST's hide gate rather than dispose
of the 43").

POPULATION IS RE-DERIVED, NOT COPIED FROM MEMORY. The 43 = the s40 297-sweep
DEAD set (scripts-staging/evidence/s50-wusvi-refresh/s40-297-sets.json, key
"## 7. DEAD (101)") intersected with rows that are STILL status=="active" in
tours-data.json today (58 of the 101 have since resolved to inactive via
s50/s51/s52/s53 rulings). This script recomputes that intersection at run
time and asserts it against the count and bucket lists below — if the live
data has drifted since 2026-08-28, the assertions fail loudly instead of
silently hiding the wrong set.

BUCKETS below are provenance labels only (from the ruling's own
classification, wtpa/STATE.md "The 43 at 3rd-session standard, bucketed with
evidence"), not a re-litigation of s40-s53 rulings:
  A  dated/seasonal event (5)
  B  whole-operator-dark — every row of that operator's catalogue is dark (6)
  C  course/certification, cohort or on-demand rather than calendared (2)
  D  genuinely dark, no A/B/C evidence (30); 9 of the 30 are the Reef2Peak
     pattern (every guided product dark, every self-serve rental live —
     an operator business-model shift, not seasonality)

MECHANISM: adds hidden/hiddenReason/hiddenAt to each row (status stays
"active" — untrue to call these "inactive"/retired; they are dark, not
closed). app.js and activity-tours.js gain "&& !t.hidden" on their existing
status/bookingDead filter (see the sibling commit's app.js/activity-tours.js
diff) — cards for these 43 leave BOTH render paths. Nothing is deleted, no
status flips to inactive, and the gate reverses by clearing hidden -> false
whenever future evidence shows one of these rows live again (no sweep
script exists yet in this repo to do that automatically — see PR body).

Usage: python3 scripts-staging/s54-wusvi-hide-gate-apply.py [--execute]
"""
import json, sys, hashlib, datetime, collections

DATA = 'tours-data.json'
SETS = 'scripts-staging/evidence/s50-wusvi-refresh/s40-297-sets.json'
EV = 'scripts-staging/evidence/s54-wusvi-hide-gate'
SOURCE = 's54-wusvi-hide-gate'
execute = '--execute' in sys.argv

raw = open(DATA, 'rb').read()
doc = json.loads(raw)
assert (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode() == raw, 'round-trip not byte-identical; refusing'
rows = doc['tours']
R = {t['pk']: t for t in rows}

dead_set = set(json.load(open(SETS))['## 7. DEAD (101)'])
assert len(dead_set) == 101, f'DEAD set drifted: {len(dead_set)} != 101'

still_active = sorted(pk for pk in dead_set if pk in R and R[pk].get('status') != 'inactive')
now_inactive = [pk for pk in dead_set if pk in R and R[pk].get('status') == 'inactive']
missing = [pk for pk in dead_set if pk not in R]
print(f're-derived: DEAD={len(dead_set)} still_active={len(still_active)} now_inactive={len(now_inactive)} missing={len(missing)}')

BUCKETS = {
    'A — dated/seasonal event': [12127, 23304, 731034, 554947, 98820],
    'B — whole-operator-dark': [484583, 484584, 487206, 487208, 601987, 602576],
    'C — course/certification': [407382, 170676],
    'D — dark (Reef2Peak guided-product-retired)': [211099, 211109, 211114, 211118, 211126, 211131, 399468, 399477, 399480],
}
bucketed = {pk for pks in BUCKETS.values() for pk in pks}
D_PLAIN = sorted(set(still_active) - bucketed)
BUCKETS['D — dark'] = D_PLAIN

# Assert the ruling's bucket lists plus the plain-dark remainder reconstruct
# the re-derived population EXACTLY — a bucket drift is a finding, not
# something to silently absorb.
all_bucketed = sorted({pk for pks in BUCKETS.values() for pk in pks})
assert all_bucketed == still_active, ('bucket partition != re-derived population', all_bucketed, still_active)
assert len(still_active) == 43, f'population is {len(still_active)}, not 43 — this IS a finding, do not proceed silently'

REASON = {pk: label for label, pks in BUCKETS.items() for pk in pks}

before = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
now = datetime.datetime.now(datetime.timezone.utc)
ts = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

summary = []
disp = collections.Counter()
for pk in still_active:
    t = R[pk]
    assert not t.get('hidden'), (pk, 'already hidden')
    t['hidden'] = True
    t['hiddenReason'] = f"{REASON[pk]}; s40 297-sweep DEAD (2026-08-22), still status=active as of {SOURCE} re-derivation; no live availability found across s40/s50/s51 probes"
    t['hiddenAt'] = ts
    disp[REASON[pk]] += 1
    summary.append(dict(pk=pk, name=t['name'], bucket=REASON[pk]))

after = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
changed = sorted(pk for pk in after if after[pk] != before[pk])
assert changed == still_active, 'touched set != re-derived 43'

out = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
result = dict(
    derivedAt=ts,
    rowsChanged=len(changed),
    disposition=dict(disp),
    sha256=dict(before=hashlib.sha256(raw).hexdigest(), after=hashlib.sha256(out.encode()).hexdigest()),
    summary=summary,
)
print(json.dumps({k: result[k] for k in ('derivedAt', 'rowsChanged', 'disposition', 'sha256')}, indent=1), 'EXECUTE' if execute else 'DRY RUN')
if execute:
    open(DATA, 'w', encoding='utf-8').write(out)
    import os
    os.makedirs(EV, exist_ok=True)
    json.dump(result, open(f'{EV}/apply-summary.json', 'w'), indent=1, ensure_ascii=False)
    print('WROTE', DATA)
