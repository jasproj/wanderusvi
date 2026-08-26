#!/usr/bin/env python3
"""s50-wusvi-holds — APPLY stage for the 43 rows HELD by #148 (s50-wusvi-refresh), per the adjudicated ruling
packet (2026-08-26). Evidence: the #148 probe (scripts-staging/evidence/s50-wusvi-refresh/probe.json, 4 dated
readings per pk) — no new requests. Every figure below is asserted against that evidence before it is written.

Rule refinements shipped here (recorded in each row's priceBasis):
  R-zero-base   a reading whose base tiers are all $0 is a closed date, not a price (excluded like UNSAMPLED)
  R-passenger   a non-participant "Passenger / stays onboard" tier never anchors
  R-omitted     a tier that omits a named component of the product ("Ticket only", "No Beach") never anchors
  R-season      when the anchor tier reads different prices across dates, the cross-date FLOOR anchors as
                "From" (date-valid on the day of the refresh), the step is recorded in priceBasis
Dispositions: 41 released (published or badged), 2 HOLD re-stamped (671029 alternating pattern, 194495
multi-product rental). Full dated stamp (priceSource s50-wusvi-holds) on all 43.
Usage: python3 scripts-staging/s50-wusvi-holds-apply.py [--execute]
"""
import json, sys, hashlib, datetime, os, collections
DATA = 'tours-data.json'; EV = 'scripts-staging/evidence/s50-wusvi-holds'; PROBE = 'scripts-staging/evidence/s50-wusvi-refresh/probe.json'
SOURCE = 's50-wusvi-holds'; execute = '--execute' in sys.argv
raw = open(DATA, 'rb').read(); doc = json.loads(raw)
assert (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode() == raw, 'round-trip not byte-identical; refusing'
rows = doc['tours']; R = {t['pk']: t for t in rows}; probe = json.load(open(PROBE))['perPk']; DATES = json.load(open(PROBE))['dates']
now = datetime.datetime.now(datetime.timezone.utc); ts = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z'); day = now.strftime('%Y-%m-%d')
def num(x): return int(x) if isinstance(x, float) and x.is_integer() else x
EVID = f"evidence: #148 probe, 4 dated readings {', '.join(DATES)} (s50-wusvi-refresh/probe.json); ruled 2026-08-26 (s50 holds packet)"
def R1(pk, price, tier, band): return dict(pk=pk, price=price, label='per adult', unit=f'per person, {band}', conf='high', rule='s48-R1', tier=tier,
    basis=f'RELEASED s48-R1 falling per-head ladder: largest band "{tier}" ${price} per person anchors; unit "per person, {band}"; ')
D = [
 # A1 — s48-R1 (13)
 R1(334589, 58, 'Adult Price (5 to 15 Pax)', 'Adult Price (5 to 15 Pax)'), R1(334596, 88, 'Adult (Groups of 11-15)', 'Adult (Groups of 11-15)'),
 R1(334622, 131.61, 'Adult 7-15', 'Adult 7-15'), R1(341630, 78, 'Adult Price (11 to 15 pax)', 'Adult Price (11 to 15 pax)'),
 R1(538171, 85, 'Adult Price (5 to 15 Pax)', 'Adult Price (5 to 15 Pax)'), R1(558412, 67, 'Adult (Pricing for 11 - 15 pax)', 'Adult (Pricing for 11 - 15 pax)'),
 R1(558413, 58, 'Adult 4-15', 'Adult 4-15'), R1(559118, 84, 'Adult Price (11 to 15 pax)', 'Adult Price (11 to 15 pax)'),
 R1(559119, 90, 'Adult Price (5 to 15 Pax)', 'Adult Price (5 to 15 Pax)'), R1(585279, 60, 'Adult Price (5 to 15 Pax)', 'Adult Price (5 to 15 Pax)'),
 R1(585280, 60, 'Adult Price (5 to 15 Pax)', 'Adult Price (5 to 15 Pax)'),
 R1(344761, 25, 'Adults', 'Adults (5-10)'), R1(586139, 85, 'Adults', 'Adults (Groups with 7 to 10 guests)'),
 # A2 — D-625 cheapest of several base tiers, unit names the variant (2)
 dict(pk=162048, price=59.47, label='per adult', unit='Adult - Sit on Top Ocean Kayak', conf='high', rule='D-625', tier='Adult - Sit on Top Ocean Kayak', basis='RELEASED D-625 cheapest of 2 base tiers: "Adult - Sit on Top Ocean Kayak" $59.47 anchors, unit names the variant (Transparent Sea Thru Kayak $75.68 is the dearer variant); '),
 dict(pk=628803, price=32.24, label='per adult', unit='Meet Up Chocolate Tasting (Adult)', conf='high', rule='D-625', tier='Meet Up Chocolate Tasting (Adult)', basis='RELEASED D-625 cheapest of 2 base tiers: "Meet Up Chocolate Tasting (Adult)" $32.24 anchors, unit names the variant (Pickup Pier Tasting $68.24 is the dearer variant); '),
 # A3 — whole-unit anchors (3)
 dict(pk=414427, price=1049.99, label='private boat', unit='per boat, up to 6 guests', conf='high', rule='D-621', tier='Includes Up To 6 Guests', basis='RELEASED D-621 whole-party tier: "Includes Up To 6 Guests" $1049.99 (+ Fees) anchors as private boat, unit "per boat, up to 6 guests" (label quoted); the 12 "Adult [API]" tiers are the whole fare divided by headcount ($1050/n) — derived, never anchor; "Additional Passenger" $50 is an add-on; '),
 dict(pk=630592, price=400, label='Be Driven', unit='per UTV', conf='high', rule='D-621', tier='Be Driven', basis='RELEASED D-621 whole-unit tier: "Be Driven" $400 anchors, unit "per UTV" (note quoted: "Price is per UTV"); "You Drive" $500 is per UTV driver; not a vessel — label verbatim, gate renders Price on request + unit; '),
 dict(pk=341844, price=224.99, label='Group Package (up to 6 pax)', unit='per group, up to 6 pax', conf='high', rule='D-614', tier='Group Package (up to 6 pax)', basis='RELEASED D-614 rising party-total ladder floor: "Group Package (up to 6 pax)" $224.99 anchors (7-10 pax $299.99, 11-15 pax $493.42), unit "per group, up to 6 pax" (label quoted); "package" here is a banded party tier, not a bundle; not a vessel — gate renders Price on request + unit; '),
 # A4 (1)
 dict(pk=334293, price=349, label='per adult', unit='Land and Sea Treasure Hunter', conf='high', rule='D-624', tier='Land and Sea Treasure Hunter', basis='RELEASED D-624 via s49 note sanction: sole tier "Land and Sea Treasure Hunter" $349, note "Both teens & adults" names a person audience → per adult; '),
 # A5 — zero-base = closed date (2)
 dict(pk=8234, price=119, label='per adult', unit=None, conf='high', rule='D-624', tier='Visitor', basis='RELEASED D-624 under R-zero-base: "Visitor" $119 on 2026-09-05 and 2026-09-19; 2026-10-03 and 2026-10-24 read Visitor $0 (closed date, not a price — excluded); Resident/Member/Accompanied Child never anchor; '),
 dict(pk=8237, price=64, label='per adult', unit=None, conf='high', rule='D-624', tier='Visitor', basis='RELEASED D-624 under R-zero-base: "Visitor" $64 on 2026-09-05 and 2026-09-19; later dates read $0 (closed date — excluded); Resident/Member never anchor; '),
 # B1 — seasonal step, cross-date FLOOR (8)
 *[dict(pk=pk, price=floor, label='per adult', unit=None, conf='high', rule='R-season', tier='Adult', floor=True,
        basis=f'RELEASED D-624 under R-season (seasonal-step floor): "Adult" reads {reads} across the 4 dated probes; cross-date floor ${floor} anchors as From (date-valid on 2026-09-05, the first probe date); majority reading ${maj} applies later in the window; ')
   for pk, floor, maj, reads in [(10949, 179, 199, '179 / 179 / 199 / 199'), (10995, 69, 89, '69 / 89 / 89 / 89'), (11995, 199, 219, '199 / 219 / 219 / 219'), (11996, 119, 139, '119 / 139 / 139 / 139'),
                                 (268925, 139, 159, '139 / 159 / 159 / 159'), (377253, 119, 139, '119 / 119 / 139 / 139'), (424875, 99, 119, '99 / 119 / 119 / 119'), (424879, 59, 79, '59 / 79 / 79 / 79')]],
 # B2 — HOLD (1)
 dict(pk=671029, hold='alternating_pattern', basis='HELD (alternating pattern not understood): "Adult 4-15" reads $48.75 / $25 / $48.75 / $25 and "Child Price" $45 / $21 / $45 / $21 on the 4 dated probes — not a seasonal step, alternates by date; floor $25 stamped unpublished pending an operator reading; '),
 # B3 (3)
 dict(pk=170656, price=160, label='per adult', unit=None, conf='high', rule='D-624', tier='Diver', basis='RELEASED D-624 under R-passenger: "Diver" $160 anchors; "Passenger" $65 (note "Stays Onboard") is a non-participant tier and never anchors; '),
 dict(pk=341846, price=41.03, label='per adult', unit='per person, Adults (7 to 10 Adults)', conf='high', rule='s48-R1', tier='Adults', basis='RELEASED s48-R1 falling per-head ladder under R-omitted: "Adults [For 7 to 10 Adults]" $41.03 is the largest band and anchors, unit "per person, Adults (7 to 10 Adults)" (note quoted); "Adult Ticket [Ticket only]" $12 omits the transport component of the named product and never anchors; '),
 dict(pk=589442, price=85, label='per adult', unit=None, conf='high', rule='D-624', tier='Adults', basis='RELEASED D-624 under R-omitted: "Adults" $85 (cruise-ship and hotel pick-up, 4-15 pax) anchors; "Adult - Wenner Farm Meet-up (Farm Tour only - No Beach)" $19.76 omits the Sapphire Beach component of the named product and never anchors; '),
 # B4 (2)
 *[dict(pk=pk, price=300, label='Group', unit='per group, up to 4 people', conf='high', rule='D-621', tier='Group', basis='RELEASED D-621 whole-party tier: "Group" $300 anchors, unit "per group, up to 4 people" (note quoted: "Includes up to 4 people per group"); "Person" $75 (note "Add more passengers!") is an add-on and never anchors; vessel status not established — label stays non-gate, renders Price on request + unit; ') for pk in (662539, 662582)],
 # B5 — stored floor + unit (3)
 dict(pk=282247, price=330, label='3 Day', unit='per vehicle, 3 days', conf='high', rule='D-614', tier='3 Day', basis='RELEASED D-614 duration-ladder floor (s50 ruling): "3 Day" $330 anchors, unit "per vehicle, 3 days"; ladder runs to 31 Day $3400 (~$110/day); a rental duration is not a fare — label stays non-gate, renders Price on request + unit; '),
 *[dict(pk=pk, price=750, label='One Hour Photo Session', unit='per session, 1 hour', conf='high', rule='D-614', tier='One Hour Photo Session', basis='RELEASED D-614 duration-ladder floor (s50 ruling): "One Hour Photo Session" $750 anchors, unit "per session, 1 hour"; ladder to Five Hour $3750; not a fare — label stays non-gate, renders Price on request + unit; ') for pk in (615474, 615491)],
 # B6 (1)
 dict(pk=489164, price=10174.94, label='private boat', unit='per boat, up to 6 people, 7 days', conf='high', rule='D-621', tier='Private Charter', basis='RELEASED D-621 whole-boat (s50 ruling on the note contradiction): sole tier "Private Charter" $10174.94, note "For up to 6 People | Pricing is per person" asserts two units at once; read as the whole boat — $10,174.94 × 6 = $61,050/week is implausible for a captained monohull, and the sibling 498637 (VI Captained Charter - Catamaran, 7 Days, no note) reads $11,872 whole-boat; unit "per boat, up to 6 people, 7 days"; '),
 # B7 — single-cabin fare (3)
 *[dict(pk=pk, price=price, label='Private Cabin for 1 Student', unit='private cabin, 1 student', conf='high', rule='D-621', tier='Private Cabin for 1 Student', basis=f'RELEASED (s50 ruling, student-class product): "Private Cabin for 1 Student" ${price} is the single-occupancy fare and anchors, unit "private cabin, 1 student"; shared-cabin per-person tiers do not anchor; "student" is the whole audience of a sailing-school week, so the never-class does not apply; label stays non-gate, renders Price on request + unit; ') for pk, price in ((489157, 3814.94), (491881, 3814.94), (575294, 4344.94))],
 # B8 — HOLD (1)
 dict(pk=194495, hold='multi_product_rental', basis='HELD (multi-product rental ladder): five products in one item (Stand Up Paddleboard 1 Week $200 / Double Kayak 1 Week $250 / Single Kayak 1 Week $220 / Snorkel Gear 1 week $55 / Snorkel Gear 1 day $12) — no single unit is the price; floor $12 stamped unpublished; candidate for a per-product split; '),
]
assert len(D) == 43 and len({d['pk'] for d in D}) == 43
before = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
summary = []; disp = collections.Counter()
for d in D:
    t = R[d['pk']]; assert t.get('priceSource') == 's50-wusvi-refresh' and t['priceConfidence'] == 'low', d['pk']
    tiers = t['priceTiers']; tier_prices = {(x['singular'], x['price']) for x in tiers}
    readings = [p for p in probe[str(d['pk'])]['probes'] if not p.get('error') and not p.get('absent')]
    old = dict(price=t['price'], label=t['priceLabel'])
    if 'hold' in d:
        floor = min(x['price'] for x in tiers if x['priceCents'] > 0)
        t['price'] = num(floor); t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = d['hold']; t['priceBasis'] = d['basis'] + EVID
        (t.get('_unknownFields') or {}).pop('priceUnit', None)
        summary.append(dict(pk=d['pk'], name=t['name'], disposition='HELD', hold=d['hold'], old=old, new=t['price'])); disp['HELD'] += 1
    else:
        # evidence assertion: the figure must exist on the majority ladder under the named tier, or (B1) as a per-date reading of that tier
        if d.get('floor'): assert any(any(x['singular'] == d['tier'] and abs(x['priceCents'] / 100 - d['price']) < 0.005 for x in p['tiers']) for p in readings), ('floor not in readings', d['pk'])
        else: assert (d['tier'], d['price']) in tier_prices, ('figure not in stamped tiers', d['pk'], d['tier'], d['price'])
        t['price'] = num(d['price']); t['priceLabel'] = d['label']; t['priceConfidence'] = d['conf']; t['priceEnrichmentStatus'] = 'high'; t['currency'] = 'USD'
        t['priceBasis'] = d['basis'] + EVID
        uf = t.get('_unknownFields') or {}
        if d['unit']: uf['priceUnit'] = d['unit']
        else: uf.pop('priceUnit', None)
        if uf: t['_unknownFields'] = uf
        elif '_unknownFields' in t: del t['_unknownFields']
        gate = d['label'] in ('per adult', 'private boat')
        summary.append(dict(pk=d['pk'], name=t['name'], disposition=d['rule'], old=old, new=t['price'], label=d['label'], unit=d['unit'], tier=d['tier'], renders='price' if gate else 'badge only')); disp[f"{d['rule']}:{'published' if gate else 'badged'}"] += 1
    t['priceSource'] = SOURCE; t['priceEnrichmentSource'] = 's50-wusvi-holds-ruling'; t['priceEnrichmentAt'] = ts; t['priceVerifiedAt'] = day
after = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
changed = [pk for pk in after if after[pk] != before[pk]]; assert sorted(changed) == sorted(d['pk'] for d in D), 'touched set != 43'
out = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
result = dict(stampedAt=ts, rowsChanged=len(changed), disposition=dict(disp), sha256=dict(before=hashlib.sha256(raw).hexdigest(), after=hashlib.sha256(out.encode()).hexdigest()), summary=summary)
print(json.dumps({k: result[k] for k in ('stampedAt', 'rowsChanged', 'disposition', 'sha256')}, indent=1), 'EXECUTE' if execute else 'DRY RUN')
if execute: open(DATA, 'w', encoding='utf-8').write(out); json.dump(result, open(f'{EV}/apply-summary.json', 'w'), indent=1, ensure_ascii=False); print('WROTE', DATA)
