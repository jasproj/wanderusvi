#!/usr/bin/env python3
"""s50-wusvi-refresh — APPLY stage. Port of wanderamsterdam scripts/s49-wams-refresh-apply.py (itself the
wanderengland s48-weng-refresh-b apply() + classifyTier() with the s49 refinements), adapted to wanderusvi.

WHY PYTHON: tours-data.json carries Python float spellings (109.0, 175.0 …) that JSON.stringify flattens, so
only json.dumps(indent=2, ensure_ascii=False)+'\\n' round-trips it byte-for-byte (asserted below). New
integral amounts are spelled as ints (num()).

Population: the 267 pks frozen in scripts-staging/evidence/s50-wusvi-refresh/population.json (evidence
< 2026-08-01, live, not s42-s49 ruled, not s40 HOLD). Evidence: probe.json (4 dated readings per pk).

WUSVI adaptations (vs WAMS s49):
  #1 site currency USD; D-620 holds any row whose live details.currency != USD.
  #2 gate vocabulary: app.js / activity-tours.js render ONLY priceLabel 'per adult' (conf high|medium) and
     'private boat' (conf high). A D-624 per-person anchor is therefore stamped priceLabel='per adult'; a
     party/whole-unit anchor is stamped 'private boat' only when the product is a vessel (#144 UNIT_NOT_VESSEL
     ruling: jeeps, parasail, vans, gardens are not boats) — otherwise the tier label verbatim, which the gate
     does not render. The anchoring tier's own name is always in priceTiers/priceBreakdown/priceBasis.
  #3 this repo's consensus gate (memory: price-consensus-gate / D-482): the position-0 eligible tier and the
     discount-exclusion pick must agree on price, else HOLD 'D-482 ambiguous full-fare set' (low).
  #4 cross-date agreement: the anchor price must be identical on every sampled reading; ≥2 sampled readings
     → high, exactly 1 → medium (renders for per adult, not for private boat), disagreement → HOLD mixed (low).
  #5 every touched row gets the full dated stamp: priceSource, priceEnrichmentSource, priceEnrichmentAt,
     priceEnrichmentStatus, priceVerifiedAt, priceBasis, priceTiers, priceConfidence. The stale
     _unknownFields.priceSource ('v52-dominant-gate') residue is removed from population rows.

Dispositions: UNSAMPLED / PROBE_ERROR (stored figure retained, low — the 43 s40-DEAD rows are in-batch, empty
availability is a date verdict), zero_price (price null, low), D-620, D-624 (per adult), D-614 / D-621 / s48-R1
(group anchors with priceUnit), single-tier, HELD (D-482 / no anchorable tier / hire-accessory / mixed).
Final add-on sweep aborts the run if a released anchor is add-on shaped. Deposits/vouchers never anchor.
Usage: python3 scripts-staging/s50-wusvi-refresh-apply.py [--execute]
"""
import json, re, sys, hashlib, collections, datetime, os
DATA = 'tours-data.json'; EV = 'scripts-staging/evidence/s50-wusvi-refresh'; SOURCE = 's50-wusvi-refresh'
ENRICH_SOURCE = 's50-wusvi-refresh-price-preview-v2'; SITE_CUR = 'USD'
execute = '--execute' in sys.argv
raw = open(DATA, 'rb').read(); doc = json.loads(raw)
assert (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode() == raw, 'round-trip not byte-identical; refusing'
ev = json.load(open(f'{EV}/probe.json')); DATES = ev['dates']
assert not ev['reconcile']['incomplete'], 'probe incomplete'
POP = json.load(open(f'{EV}/population.json')); pop_set = set(POP['pks'])
rows = doc['tours']; pop = [t for t in rows if t['pk'] in pop_set]
assert ev['population'] == len(pop) == POP['count'] == 267, ('population drift', ev['population'], len(pop))
assert set(map(str, pop_set)) == set(ev['perPk']), 'probe/population pk set mismatch'
assert any(len({p['start_at'] for p in v['probes'] if p.get('start_at')}) > 1 for v in ev['perPk'].values()), 'date parameter ignored'
S40_DEAD = set(json.load(open(f'{EV}/s40-297-sets.json'))['## 7. DEAD (101)'])
def num(x): return int(x) if isinstance(x, float) and x.is_integer() else x
def u(c): return num(round(c / 100, 2))
now = datetime.datetime.now(datetime.timezone.utc); STAMP_DAY = now.strftime('%Y-%m-%d')
ts = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# ---- tier classification (WENG regexes, WAMS additions kept, USVI additions marked) ----
NEVER = re.compile(r"\b(child|childs|child's|children|childrens|children's|kid|kids|kid's|infant|infants|baby|babies|toddler|junior|juniors|youth|youths|teen|teenager|teens|adolescent|adolescents|young adult|student|students|senior|seniors|oap|concession|concessions|pensioner|disabled|wheelchair|carer|companion|blue light|nhs|discount|under\s*\d+s?|\d+\s*(and|&)\s*under|family|families|bundle|package|add[- ]?on|extra(?!\s*(small|large))|extras|additional|supplement|upgrade|gratuity|tip|tips|donation|deposit|voucher|gift card|redemption|per additional|spectator|non[- ]?participant|observer|rider(?= only)|dog|dogs|pet|pets|kit|merchandise|parking|resident|residents|local|locals|military|member|members|comp|complimentary|crew|niño|niños|niña|niñas|bebé|bebe|infante"
                   r"|kinderen|kindje|peuter|peuters|jeugd|jongeren|studenten|senioren|65\+|korting|toeslag|bijboeking|optie|opties|fooi|borg|cadeaubon|familie|gezin|pakket|arrangement"
                   r"|aggiuntiv[oa]|adicional|adicionales|zusätzlich|zusätzliche|supplémentaire|extra persoon|bijboeken|optional|optioneel|aanbetaling|voorschot|deposito|caparra|kaution|anzahlung)\b|^add (a|an|the)\b", re.I)
NOT_A_PRICE = re.compile(r"\b(deposit|deposito|borg|aanbetaling|voorschot|caparra|kaution|anzahlung|voucher|gift card|cadeaubon|donation|gratuity|tip|tips|fooi|balance due|remaining balance)\b", re.I)
ACCESSORY = re.compile(r"\b(bag|bags|lock|helmet|child seat|seat cover|basket|poncho|raincoat|insurance|boots?|gloves?|hoods?|wetsuit|trailer|map|extra[- ]person|extra participants?|cooler|ice|fuel|gas|captain(?:'s)? fee)\b", re.I)
RENTAL_NAME = re.compile(r"\b(hire|rental|rentals|rent)\b", re.I)
AGE_RANGE = re.compile(r"\b\d{1,2}\s*(-|–|to)\s*\d{1,2}\s*(yrs|years|year olds|yr olds|y/o|y/old|yo)\b", re.I)
WORDNUM = r"(two|three|four|five|six|seven|eight|nine|ten|twelve|\d+)"
GROUP = re.compile(r"\b(per group|group|groups|party|parties|private|exclusive|charter|boat|vessel|catamaran|yacht|powerboat|sailboat|dinghy|jet ?ski|waverunner|kayak|canoe|paddle ?board|sup|raft|vehicle|car|jeep|van|suv|minibus|coach|table|room|cabin|villa|couple|couples|for two|for 2|whole|hire|rental|rentals|seater|nights?|berth|capacity|machine|unit|trip|includes up to"
                   r"|" + WORDNUM + r"\s*(people|persons|ppl|pax|guests|players|riders|passengers|adults|divers|snorkelers)|up to \d+|max(?:imum)?\.? ?\d+)\b", re.I)
BASE_WORDS = r"adult|adults|person|per person|standard|general|guest|guests|visitor|participant|passenger|rider|player|ticket|seat|single|individual|one person|1 person|per seat|snorkeler|snorkelers|diver|divers|swimmer|hiker|paddler|regular|normal|traveler|traveller|customer|passenger"
BASE = re.compile(r"\b(" + BASE_WORDS + r")\b", re.I); BASE_HEAD = re.compile(r"^(" + BASE_WORDS + r")\b", re.I)
BASE_AGE = re.compile(r"^\s*(1[0-9]|[2-5][0-9])\s*(years?|yrs?|y\.?o\.?)?\s*(and (up|over|older)|\+|plus)\b", re.I)
CUSTOMER_HEAD = re.compile(r"^(adult|adults|person|persons|standard|general|guest|guests|visitor|participant|passenger|rider|player|regular|normal|individual|single|seat|snorkeler|diver|\d{1,2}\s*(years?|yrs?)?\s*(and up|and over|\+))\b", re.I)
PER_PERSON = re.compile(r"\b(per (person|player|participant|head|adult|guest|rider|passenger|student|diver|snorkeler))\b|\beach person\b|\bpricing is per person\b|\b(1|one) (person|student|player|guest)\b(?!\s*(or|to|-|–|of))", re.I)   # USVI: bare "pp"/"PP Fee" dropped — a fee mention is not a unit assertion
ADDON_SELF = re.compile(r"per additional|\bprice per item\b|\bper extra person\b|\beach additional\b", re.I)
ADDON_LABEL = re.compile(r"\badditional\b|\bextra\b|\badd[- ]?on\b|\bsupplement\b|^add (a|an|the)\b|\boptional\b|\bupgrade\b", re.I)
VOLUME = re.compile(r"^(" + WORDNUM + r"\s*(or more|\+)?\s*(people|persons|adults|guests|players|passengers|students|divers|snorkelers)|groups? of|([2-9]|\d{2,})\s*(-|–|to|\+)\s*\d*\s*(people|persons|adults|guests|players|passengers|students))\b", re.I)
NAME_GROUP = re.compile(r"\b(hire|rental|rentals|charter|charters|private|boat|vessel|catamaran|yacht|powerboat|cruise|jeep)\b", re.I)
# USVI adaptation #2: is the whole-unit a vessel? ('private boat' is factually false on a jeep / parasail / van)
VESSEL = re.compile(r"\b(boat|boats|charter|charters|catamaran|yacht|powerboat|sailboat|sail|sailing|vessel|cruise|cruiser|dinghy|pontoon|trimaran|monohull|skiff|marlin|sportfish|sport ?fisher)\b", re.I)
NOT_VESSEL = re.compile(r"\b(jeep|jeeps|van|suv|car|cars|parasail|parasailing|kayak|kayaks|paddle ?board|sup|bike|bikes|e-?bike|scooter|segway|golf cart|atv|utv|buggy|hike|hiking|walk|walking|garden|villa|room|cabin|transfer|transport|transportation|shuttle|taxi|airport|jet ?ski|waverunner|flyboard)\b", re.I)
def classify(t, product_name):
    sing = (t.get('singular') or '').strip(); note = t.get('note') or ''
    if not (t.get('priceCents') or 0) > 0: return 'zero'
    if NEVER.search(sing) or AGE_RANGE.search(sing): return 'never'
    if NOT_A_PRICE.search(sing): return 'never'
    if ADDON_SELF.search(note): return 'never'
    if VOLUME.search(sing): return 'group'
    if BASE_HEAD.search(sing) or BASE_AGE.search(sing): return 'base'
    if BASE.search(sing) and not GROUP.search(sing): return 'base'
    if PER_PERSON.search(note): return 'conflict' if GROUP.search(sing) else 'unnamed'   # USVI D-484: "Private Charter … pricing is per person" asserts two units at once → held, never anchored
    if GROUP.search(sing) or GROUP.search(note): return 'group'
    if NAME_GROUP.search(product_name or ''): return 'group'
    return 'unnamed'
PARTY_BAND = re.compile(WORDNUM + r"\s*(or more|\+)?\s*(people|person|persons|guests|pax|adults|players|passengers|divers|snorkelers)\b|\b(groups? of|up to \d|max(?:imum)?\.? ?\d|from \d|includes up to)", re.I)
def classify_ladder(tiers, product_name):
    cl = [(x, classify(x, product_name)) for x in tiers]
    if sum(1 for x, c in cl if c in ('base', 'group') and PARTY_BAND.search(x.get('singular') or '')) >= 2:
        cl = [(x, ('unnamed' if c in ('group', 'base') and not PARTY_BAND.search(x.get('singular') or '') and not CUSTOMER_HEAD.search(x.get('singular') or '') else c)) for x, c in cl]
    explicit = any(c in ('base', 'group') for _, c in cl)
    return [(x, ('base_implicit' if c == 'unnamed' and not explicit else c)) for x, c in cl]   # USVI D-484: an implicit unit ("3 Day", "One Hour Photo Session") may not anchor

# ---- s49 unit derivation for group anchors ----
WORD2N = dict(two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10, twelve=12)
AGE_PHRASE = re.compile(r"\b\d{1,2}\s*(?:-|–|to)?\s*\d{0,2}\s*(years?|yrs?|y\.?o\.?)\b(\s*(and (up|over|older)|olds?|\+))?|\b\d{1,2}\s*\+(?!\s*(people|persons|guests|pax))|\bages?\s*\d{1,2}(\s*(-|–|to|and|&)\s*(\d{1,2}|under|up|over))?", re.I)
DURATION = re.compile(r"\b\d{1,3}([.,]\d+)?\s*(hours?|hrs?|hr|h|minutes?|mins?|min|days?|nights?|weeks?)\b", re.I)
FEET = re.compile(r"\b\d{2,3}\s*(?:'|’|ft|foot|feet)\b", re.I)   # USVI: "41' Catamaran" carries a hull length, not a party size
def band_size(label):
    label = AGE_PHRASE.sub(' ', DURATION.sub(' ', FEET.sub(' ', label)))
    m = re.search(r"\b(\d{1,3})\s*(?:-|–|to)\s*(\d{1,3})\b", label)
    if m: return int(m.group(2))
    m = re.search(r"\b(\d{1,3})\b", label)
    if m: return int(m.group(1))
    m = re.search(r"\b(" + "|".join(WORD2N) + r")\b", label, re.I)
    return WORD2N[m.group(1).lower()] if m else None
CAP = re.compile(r"((?:up to|maximum(?: of)?|max(?:imum)?\.?|for up to|space for(?: up to)?|accommodates(?: up to)?|seats(?: up to)?|no more than|includes up to)\s*(\d{1,3})\s*(guests|passengers|people|persons|pax|divers|snorkelers))", re.I)
SIZE_OR_DUR = re.compile(r"\d|" + "|".join(WORD2N) + r"|\b(hour|hours|minute|minutes|min|day|days|half|full)\b", re.I)
NAME_BAND = re.compile(r"((?:\d{1,3})\s*(?:-|–|to)\s*(\d{1,3})\s*(people|persons|guests|pax|passengers))", re.I)
def unit_for_group(anchor_label, t):
    if SIZE_OR_DUR.search(FEET.sub(' ', anchor_label)): return anchor_label, 'tier label verbatim'
    name = t.get('name') or ''
    m = NAME_BAND.search(name) or CAP.search(name)
    if m:
        n = m.group(2); noun = (m.group(3)).lower()
        return f"per group, up to {n} {noun}", f'product name quoted: "{m.group(1)}"'
    if RENTAL_NAME.search(name): return anchor_label, 'tier label verbatim'
    m = CAP.search(t.get('description') or '')
    if m:
        noun = 'boat' if VESSEL.search(name) and not NOT_VESSEL.search(name) else 'group'
        return f"per {noun}, up to {m.group(2)} {m.group(3).lower()}", f'description quoted: "{m.group(1)}"'
    return anchor_label, 'tier label verbatim'
def r1_ladder(base, group):
    if any((band_size(x['singular']) or 1) != 1 for x in base): return None
    sized = [(x, band_size(x['singular'])) for x in group]
    if not sized or any(not n or n < 2 for _, n in sized): return None
    by_n = {}
    for x, n in sized: by_n.setdefault(n, []).append(x)
    seq = [(1, min(x['priceCents'] for x in base))] + [(n, min(x['priceCents'] for x in xs)) for n, xs in sorted(by_n.items())]
    if not all(b[1] < a[1] for a, b in zip(seq, seq[1:])): return None
    n = seq[-1][0]; return n, min(by_n[n], key=lambda x: x['priceCents'])
COUPLE = re.compile(r"\b(couple|couples|for two|for 2|two persons|2 persons|2 people|two people)\b", re.I)
def hybrid_couple(base, group):
    couples = [x for x in group if COUPLE.search(x['singular'])]
    if not couples or not base: return None
    if all((band_size(x['singular']) or 1) >= 3 for x in base): return min(couples, key=lambda x: x['priceCents'])
    return None
def fmt(tiers): return ' / '.join(f"{x['singular']} ${u(x['priceCents'])}" for x in tiers if x['priceCents'] > 0)
def key(p): return json.dumps([[x['singular'], x['priceCents']] for x in p['tiers']])
def is_vessel(t, anchor):
    text = f"{t.get('name') or ''} | {anchor['singular']} | {anchor.get('note') or ''}"
    return bool(VESSEL.search(text)) and not NOT_VESSEL.search(t.get('name') or '')
before = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
summary = []; disp = collections.Counter(); sweep_hits = []; residue_removed = 0
for t in pop:
    v = ev['perPk'][str(t['pk'])]; ok = [p for p in v['probes'] if not p['error']]; sampled = [p for p in ok if not p['absent']]
    old = dict(price=t.get('price'), label=t.get('priceLabel'), conf=t.get('priceConfidence'))
    rec = dict(pk=t['pk'], name=t['name'], old=old['price'], oldLabel=old['label'], oldConf=old['conf'], s40Dead=t['pk'] in S40_DEAD)
    t['priceSource'] = SOURCE; t['priceEnrichmentSource'] = ENRICH_SOURCE; t['priceEnrichmentAt'] = ts; t['priceVerifiedAt'] = STAMP_DAY
    uf = t.get('_unknownFields')
    if uf and 'priceSource' in uf: del uf['priceSource']; residue_removed += 1
    if uf and 'priceUnit' in uf: del uf['priceUnit']
    if uf is not None and not uf: del t['_unknownFields']
    if not sampled:
        d = 'UNSAMPLED' if ok else 'PROBE_ERROR'
        t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = 'unsampled' if ok else 'probe_error'
        stored = 'null' if old['price'] is None else f"${old['price']}"
        t['priceBasis'] = f"UNSAMPLED: absent from price-preview items[] on {len(ok)}/{len(DATES)} dated probes ({', '.join(DATES)}){f', {len(DATES)-len(ok)} probe error(s)' if len(ok) < len(DATES) else ''}; stored {stored}{f' ({old['label']})' if old['label'] else ''} retained unpublished pending a live reading (empty availability is a date verdict, not a liveness verdict)"
        t['priceTiers'] = [dict(singular=x.get('singular'), plural=x.get('plural'), note=x.get('note') or '', priceCents=x.get('priceCents'), price=x.get('price'), minPartySize=x.get('minPartySize')) for x in (t.get('priceBreakdown') or [])]
        rec.update(disposition=d, new=t.get('price'), probeErrors=[p['error'] for p in v['probes'] if p['error']]); disp[d] += 1; summary.append(rec); continue
    counts = collections.Counter(key(p) for p in sampled); maj_key = counts.most_common(1)[0][0]; maj = next(p for p in sampled if key(p) == maj_key)
    valid = sum(1 for p in sampled if p.get('dateValid')); evid = f"{len(sampled)}/{len(DATES)} dated readings ({valid} date-valid), {len(counts)} ladder shape(s)"
    cur = maj['liveCurrency']; tiers = maj['tiers']
    t['priceBreakdown'] = [dict(id=c['id'], singular=c['singular'], plural=c['plural'], note=c['note'], priceCents=c['priceCents'], price=u(c['priceCents']), minPartySize=c['min']) for c in tiers]
    t['priceIncludesBookingFees'] = maj['includeFees']; t['priceIncludesTaxes'] = maj['includeTaxes']
    t['priceTiers'] = [dict(singular=c['singular'], plural=c['plural'], note=c['note'] or '', priceCents=c['priceCents'], price=u(c['priceCents']), minPartySize=c['min']) for c in tiers]
    classes = classify_ladder(tiers, t['name']); rec['tiers'] = [dict(singular=x['singular'], note=x.get('note') or '', price=u(x['priceCents']), min=x.get('min'), cls=c) for x, c in classes]
    base = [x for x, c in classes if c == 'base']; group = [x for x, c in classes if c == 'group']; nz = [x for x in tiers if x['priceCents'] > 0]
    implicit = [x for x, c in classes if c == 'base_implicit' and x['priceCents'] > 0]; conflict = [x for x, c in classes if c == 'conflict' and x['priceCents'] > 0]
    never_nz = [x for x, c in classes if c == 'never' and x['priceCents'] > 0]
    cheapest = lambda xs: min(xs, key=lambda x: x['priceCents'])
    skipped = lambda: ', '.join(f"{x['singular']} ${u(x['priceCents'])} [{c}]" for x, c in classes if c != 'base' and x['priceCents'] > 0)
    # USVI adaptation #4: does every sampled reading carry this anchor tier (by NAME) at the same price?
    def cross_date(anchor):
        prices = set()
        for p in sampled:
            m = [x for x in p['tiers'] if x['singular'] == anchor['singular']]
            prices.add(min(x['priceCents'] for x in m) if m else None)
        return prices
    def hold(status, basis, floor):
        t['currency'] = SITE_CUR if cur == SITE_CUR else t.get('currency'); t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = status
        t['price'] = u(floor['priceCents']); t['priceLabel'] = floor['singular']; t['priceBasis'] = basis
        rec.update(disposition='HELD', hold=status, new=t['price'], label=floor['singular']); disp[f'HELD:{status}'] += 1
    def release(anchor, unit, rule, basis, gate_label):
        prices = cross_date(anchor)
        if len(prices) != 1:
            return hold('mixed_verdict', f"HELD (mixed verdict across dates): anchor \"{anchor['singular']}\" reads {sorted([(u(p) if p else "absent") for p in prices], key=str)} across {len(sampled)} sampled dates; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished; would have been {rule}; ladder {fmt(tiers)}; {evid}; live {cur}", cheapest(nz))
        conf = 'high' if len(sampled) >= 2 else 'medium'
        t['currency'] = SITE_CUR; t['price'] = u(anchor['priceCents']); t['priceLabel'] = gate_label; t['priceConfidence'] = conf; t['priceEnrichmentStatus'] = 'high'
        t['priceBasis'] = basis + (f"; single sampled reading → medium" if conf == 'medium' else f"; anchor identical on all {len(sampled)} sampled dates")
        if unit: t.setdefault('_unknownFields', {})['priceUnit'] = unit
        if ADDON_LABEL.search(anchor['singular']) or ADDON_SELF.search(anchor.get('note') or ''): sweep_hits.append((t['pk'], anchor['singular'], anchor.get('note')))
        changed = old['price'] != t['price']; d = f"{rule}:{'repriced' if changed else 'unchanged'}"
        rec.update(disposition=d, rule=rule, new=t['price'], label=gate_label, tier=anchor['singular'], unit=unit, conf=conf); disp[d] += 1
    if not nz:
        t['price'] = None; t['priceLabel'] = None; t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = 'zero_price'; t['currency'] = SITE_CUR if cur == SITE_CUR else t.get('currency')
        t['priceBasis'] = f"zero_price: every live tier is $0 on the majority reading ({' / '.join(x['singular'] for x in tiers)}); {evid}; live {cur}"
        rec.update(disposition='zero_price', new=None); disp['zero_price'] += 1
    elif cur != SITE_CUR:
        anchor = cheapest(base or nz)
        t['currency'] = cur; t['price'] = u(anchor['priceCents']); t['priceLabel'] = anchor['singular']; t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = f"non_usd_currency:{cur}"
        t['priceBasis'] = f"HELD (D-620): live details.currency {cur} ≠ site USD; true amount {cur} {t['price']} ({anchor['singular']}) stamped, unpublished; {evid}"
        rec.update(disposition='D-620', new=t['price'], currency=cur); disp['D-620'] += 1
    elif conflict and not base:
        hold('d484_unit_conflict', f"HELD (D-484 unit conflict): tier(s) {', '.join(f'\"{x['singular']}\" ${u(x['priceCents'])} (note: {x.get('note') or ''})' for x in conflict)} carry a party-shaped label with a per-person note — two units asserted at once; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished pending a ruling; ladder {fmt(tiers)}; {evid}; live USD", cheapest(nz))
    elif implicit and not base and not group:
        hold('d484_no_unit', f"HELD (D-484 no asserted person unit): ladder {fmt(tiers)} names no adult/base or party tier — {', '.join(f'\"{x['singular']}\"' for x in implicit[:4])}{' …' if len(implicit) > 4 else ''} is a duration/thing token, not a unit; floor ${u(cheapest(nz)['priceCents'])} ({cheapest(nz)['singular']}) stamped unpublished pending a ruling; {evid}; live USD", cheapest(nz))
    elif base and group and hybrid_couple(base, group):
        anchor = hybrid_couple(base, group); gl = 'private boat' if is_vessel(t, anchor) else anchor['singular']
        release(anchor, anchor['singular'], 'D-614', f"D-614 hybrid ladder: couple tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} is the smallest bookable unit and anchors with the tier label verbatim as unit; per-person tiers ({', '.join(f'{x['singular']} ${u(x['priceCents'])}' for x in base)}) do not anchor; ladder {fmt(tiers)}; {evid}; live USD", gl)
    elif base and group and r1_ladder(base, group):
        n, anchor = r1_ladder(base, group); unit = f"per person, {anchor['singular']}"
        release(anchor, unit, 's48-R1', f"s48-R1 per-head rate ladder (price per head falls as band grows; 1-person tier ${u(cheapest(base)['priceCents'])} is the dearest, not a From anchor): largest band \"{anchor['singular']}\" ${u(anchor['priceCents'])} per person anchors with unit \"{unit}\"; ladder {fmt(tiers)}; {evid}; live USD", 'per adult')
    elif base:
        anchor = cheapest(base)
        # USVI adaptation #3 — consensus gate: position-0 eligible tier (ladder order, non-zero, non-never) must agree in price
        pos0 = next((x for x, c in classes if c in ('base', 'group') and x['priceCents'] > 0), None)
        if pos0 is not None and pos0['priceCents'] != anchor['priceCents']:
            hold('d482_ambiguous', f"HELD (D-482 ambiguous full-fare set): position-0 eligible tier \"{pos0['singular']}\" ${u(pos0['priceCents'])} ≠ discount-exclusion pick \"{anchor['singular']}\" ${u(anchor['priceCents'])}; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished; ladder {fmt(tiers)}; {evid}; live USD", cheapest(nz))
        else:
            bs = band_size(anchor['singular']); unit = f"per person, {anchor['singular']}" if bs and bs >= 2 and PARTY_BAND.search(anchor['singular']) else None
            release(anchor, unit, 'D-624', f"D-624 cheapest adult/base per-person tier \"{anchor['singular']}\" ${u(anchor['priceCents'])}{f' of {len(base)} base tiers (D-625)' if len(base) > 1 else ''}, published as per adult{f'; unit \"{unit}\"' if unit else ''}{f'; not anchoring: {skipped()}' if skipped() else ''}; ladder {fmt(tiers)}; {evid}; live USD", 'per adult')
    elif group and RENTAL_NAME.search(t['name']) and not ACCESSORY.search(t['name']) and not [x for x in group if not ACCESSORY.search(x['singular'])]:
        hold('hire_accessory', f"HELD (hire/rental rule): no non-accessory hire tier in ladder {fmt(tiers)}; floor ${u(cheapest(nz)['priceCents'])} ({cheapest(nz)['singular']}) stamped unpublished; {evid}; live USD", cheapest(nz))
    elif group:
        if RENTAL_NAME.search(t['name']) and not ACCESSORY.search(t['name']): group = [x for x in group if not ACCESSORY.search(x['singular'])]
        sized = [(x, band_size(x['singular'])) for x in group]; sized = [(x, n) for x, n in sized if n]
        by_n = {}
        for x, n in sized: by_n.setdefault(n, []).append(x)
        seq = [(n, min(xs, key=lambda x: x['priceCents'])['priceCents']) for n, xs in sorted(by_n.items())]
        if len(seq) >= 2 and all(b[1] < a[1] for a, b in zip(seq, seq[1:])):
            n, _ = seq[-1]; anchor = min(by_n[n], key=lambda x: x['priceCents']); unit = f"per person, {anchor['singular']}"; gl = 'per adult'
            rule = 's48-R1'; how = f"s48-R1 per-head rate ladder (price falls as band grows): largest band \"{anchor['singular']}\" ${u(anchor['priceCents'])} per person anchors with unit \"{unit}\""
        else:
            anchor = cheapest(group); unit, src = unit_for_group(anchor['singular'], t)
            rising = len(seq) >= 2 and all(b[1] > a[1] for a, b in zip(seq, seq[1:]))
            rule = 'D-614' if (rising or len(group) > 1) else 'D-621'
            gl = 'private boat' if is_vessel(t, anchor) else anchor['singular']
            how = (f"D-614 party-total ladder (price rises with band; a total is never divided by headcount): floor tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} anchors" if rising else
                   f"{'D-614 party-size ladder floor' if len(group) > 1 else 'D-621 whole-party tier'}: tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} anchors") + f" with unit \"{unit}\" ({src}); published as {'private boat (vessel)' if gl == 'private boat' else 'tier label verbatim — not a vessel (#144 UNIT_NOT_VESSEL), gate does not render'}"
        release(anchor, unit, rule, f"{how}; no standalone adult/base per-person tier{f'; not anchoring: {skipped()}' if skipped() else ''}; ladder {fmt(tiers)}; {evid}; live USD", gl)
    elif len(nz) == 1 and never_nz and not implicit and not conflict and not ADDON_LABEL.search(nz[0]['singular']) and not ADDON_SELF.search(nz[0].get('note') or '') and not NOT_A_PRICE.search(nz[0]['singular']):
        anchor = nz[0]; gl = 'per adult' if PER_PERSON.search(anchor.get('note') or '') or BASE.search(anchor['singular']) else ('private boat' if is_vessel(t, anchor) and GROUP.search(anchor['singular']) else anchor['singular'])
        release(anchor, anchor['singular'] if gl != 'per adult' else None, 'single-tier', f"single-tier product (s49 wave-2 rule: the sole tier is the entire audience): tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} anchors; published as {gl}; {evid}; live USD", gl)
    else:
        floor = cheapest(nz); unnamed = [x for x, c in classes if c == 'unnamed' and x['priceCents'] > 0]
        hold('no_base_tier', f"HELD (no adult/base tier): live ladder {fmt(tiers)} has no anchorable tier ({', '.join(f'{x['singular']} [never]' for x in never_nz)}{'; ' if never_nz and unnamed else ''}{', '.join(f'{x['singular']} [unnamed extra]' for x in unnamed)}); floor ${u(floor['priceCents'])} ({floor['singular']}) stamped unpublished pending a ruling; {evid}; live USD", floor)
    summary.append(rec)
assert not sweep_hits, ('ABORT: add-on-shaped anchor tier(s)', sweep_hits)
after = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
changed = [pk for pk in after if after[pk] != before[pk]]; outside = [pk for pk in changed if pk not in pop_set]
assert not outside and len(rows) == len(before), ('rows outside population changed', outside)
untouched = len(pop) - len(changed); assert untouched == 0, ('population rows without a fresh stamp', untouched)
out = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
result = dict(stampedAt=ts, population=len(pop), rowsChanged=len(changed), untouchedInPop=untouched, residuePriceSourceRemoved=residue_removed, disposition=dict(disp),
              sha256=dict(before=hashlib.sha256(raw).hexdigest(), after=hashlib.sha256(out.encode()).hexdigest()), summary=summary)
print(json.dumps({k: result[k] for k in ('stampedAt', 'population', 'rowsChanged', 'untouchedInPop', 'residuePriceSourceRemoved', 'disposition', 'sha256')}, indent=1), 'EXECUTE' if execute else 'DRY RUN')
if execute:
    open(DATA, 'w', encoding='utf-8').write(out); json.dump(result, open(f'{EV}/apply-summary.json', 'w'), indent=1, ensure_ascii=False); print('WROTE', DATA)
elif os.environ.get('DRY_OUT'):
    json.dump(result, open(os.environ['DRY_OUT'], 'w'), indent=1, ensure_ascii=False)
