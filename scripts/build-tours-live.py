#!/usr/bin/env python3
"""Build tours-live.json: the slim, live-only subset of tours-data.json that
activity-tours.js needs (the activity-page strip renders 3 cards; it does not
need the 3 MB full catalogue). Re-run after any tours-data.json change:

    python3 scripts/build-tours-live.py

Liveness filter mirrors activity-tours.js / app.js exactly: status != inactive,
not bookingDead, not hidden, bookingUrl present.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELDS = ['id', 'name', 'company', 'bookingUrl', 'price', 'priceLabel',
          'priceConfidence', 'tags', 'image', 'description', 'status']
src = json.loads((ROOT / 'tours-data.json').read_text())
tours = src['tours'] if isinstance(src, dict) else src
out = []
for t in tours:
    if t.get('status') == 'inactive' or t.get('bookingDead') or t.get('hidden') or not t.get('bookingUrl'):
        continue
    s = {k: t[k] for k in FIELDS if k in t}
    if isinstance(s.get('description'), str) and len(s['description']) > 200:
        s['description'] = s['description'][:200]
    pu = (t.get('_unknownFields') or {}).get('priceUnit')
    if pu: s['_unknownFields'] = {'priceUnit': pu}
    out.append(s)
(ROOT / 'tours-live.json').write_text(json.dumps({'tours': out}, separators=(',', ':'), ensure_ascii=False))
print(f'{len(out)} live of {len(tours)} → tours-live.json')
