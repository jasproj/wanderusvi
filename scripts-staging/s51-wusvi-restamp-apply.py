#!/usr/bin/env python3
"""s51-wusvi-restamp — APPLY stage. Dated re-stamp of the 282 live rows that carry no s50 stamp: the rows ruled in
PRs #135-#145 before the stamp convention (161 figure rulings + 569248 ruled by s42 without a data edit, 16 #135/#139 nulls) plus the 104 s40 297-sweep HOLD rows
that were never edited, and 11993 (island-only edit). Population frozen in evidence/s51-wusvi-restamp/population.json;
per-row ruling ledger (ruled figure, named tier, label, unit, source) in rulings.json; live evidence in probe.json
(4 dated price-preview readings per pk, same dates as s50).

Built on scripts-staging/s50-wusvi-refresh-apply.py (classifier, consensus gate, gate vocabulary, cross-date agreement,
UNIT_NOT_VESSEL, add-on abort, byte-identical round-trip) with these s51 changes:
  G1 both s50 classifier guards stay active: bare "pp"/"PP Fee" is not a per-person assertion (PER_PERSON), and the
     D-625 unnamed→base promotion is tracked as base_implicit and HELD under D-484 (never anchors).
  G2 never-anchor on a unicode-normalised label: NEVER / NOT_A_PRICE / ADDON regexes run on NFKD-stripped, NFKC,
     quote-folded, casefolded text as well as the raw label ("Niño", "Child’s", full-width digits cannot slip past).
  R-zero-base   a reading whose base tiers are all $0 is a closed date — excluded like UNSAMPLED (s50 holds packet)
  R-passenger   a non-participant "Passenger / stays onboard" tier never anchors
  R-omitted     a tier that omits a named component of the product ("Ticket only", "No Beach") never anchors
  R-season      when the anchor tier reads different prices across dates (present on all), the cross-date FLOOR anchors
                as "From", high; the step is recorded in priceBasis (replaces the s50 mixed_verdict hold for that shape)
  G3 an adjective head (Standard/General/Regular/Normal) over a whole-unit token ("Standard Full Day … Cruise") is a
     group tier, not a seat; "cruise" joins the whole-unit token list (s40 held it as a thing-token).
  P-floor       a candidate anchor at or below $1 is a placeholder, not a fare — HELD (memory: dchain placeholder fares)
  HONOUR (rows with a ruled figure): the ruling's named tier is looked up BY NAME on every sampled reading.
     tier present, live == ruled figure  → honoured:unchanged (fresh dated stamp, same figure/label/unit)
     tier present, live != ruled figure  → honoured:repriced (live figure; ruled label/unit kept; R-season floor if stepped)
     tier absent from every reading      → s51 packet: identical figure on a renamed tier → D-621 re-anchor as private boat, unit = the
                                           live tier label quoted verbatim (it contains the unit), high; otherwise TIER_GONE: REPORTED, NOT WRITTEN (the wrong-anchor precedent)
     no sampled reading / probe error    → s51 packet: standard UNSAMPLED low dated stamp (low never releases)
     ruled tier now classifies never under the settled rules, or ≤ $1 → HOLD + listed for ruling (novel shape)
     The classifier still runs on every honoured row; its anchor is recorded and any disagreement with the ruling is
     listed (ruling wins).
  MACHINE (rows with no ruled figure — s40 HOLD-only, #135/#139 nulls, 11993): the settled rule set decides; UNSAMPLED
     and PROBE_ERROR rows get the s50 low stamp with the stored figure retained unpublished; a former s40 HOLD that now
     releases is listed as such.
Every written row gets the full dated stamp: priceSource s51-wusvi-restamp, priceEnrichmentSource, priceEnrichmentAt,
priceEnrichmentStatus, priceVerifiedAt, priceBasis, priceTiers, priceConfidence (+ priceBreakdown/includes when sampled).
Rows reported-not-written are byte-identical (sha-asserted) and listed in apply-summary.json / README.
Usage: python3 scripts-staging/s51-wusvi-restamp-apply.py [--execute]
"""
import json, re, sys, hashlib, collections, datetime, os, unicodedata
DATA = 'tours-data.json'; EV = 'scripts-staging/evidence/s51-wusvi-restamp'; SOURCE = 's51-wusvi-restamp'
ENRICH_SOURCE = 's51-wusvi-restamp-price-preview-v2'; SITE_CUR = 'USD'
execute = '--execute' in sys.argv
raw = open(DATA, 'rb').read(); doc = json.loads(raw)
assert (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode() == raw, 'round-trip not byte-identical; refusing'
ev = json.load(open(f'{EV}/probe.json')); DATES = ev['dates']
assert not ev['reconcile']['incomplete'], 'probe incomplete'
POP = json.load(open(f'{EV}/population.json')); pop_set = set(POP['pks'])
RUL = {int(k): v for k, v in json.load(open(f'{EV}/rulings.json')).items()}
rows = doc['tours']; pop = [t for t in rows if t['pk'] in pop_set]
assert ev['population'] == len(pop) == POP['count'] == 282, ('population drift', ev['population'], len(pop))
assert set(map(str, pop_set)) == set(ev['perPk']), 'probe/population pk set mismatch'
assert set(RUL) == pop_set, 'rulings/population pk set mismatch'
assert all(not t.get('priceSource') and t.get('status') != 'inactive' and not t.get('bookingDead') for t in pop), 'population rule violated'
assert any(len({p['start_at'] for p in v['probes'] if p.get('start_at')}) > 1 for v in ev['perPk'].values()), 'date parameter ignored'
def num(x): return int(x) if isinstance(x, float) and x.is_integer() else x
def u(c): return num(round(c / 100, 2))
now = datetime.datetime.now(datetime.timezone.utc); STAMP_DAY = now.strftime('%Y-%m-%d')
ts = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# ---- G2: unicode normalisation for the never-anchor classes ----
def norm(s):
    s = unicodedata.normalize('NFKD', s or ''); s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = unicodedata.normalize('NFKC', s).replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-')
    return s.casefold()
def hit(rx, s): return bool(rx.search(s or '') or rx.search(norm(s)))

# ---- tier classification (s50 regexes; USVI additions marked) ----
NEVER = re.compile(r"\b(child|childs|child's|children|childrens|children's|kid|kids|kid's|infant|infants|baby|babies|toddler|junior|juniors|youth|youths|teen|teenager|teens|adolescent|adolescents|young adult|student|students|senior|seniors|oap|concession|concessions|pensioner|disabled|wheelchair|carer|companion|blue light|nhs|discount|under\s*\d+s?|\d+\s*(and|&)\s*under|family|families|bundle|package|add[- ]?on|extra(?!\s*(small|large))|extras|additional|supplement|upgrade|gratuity|tip|tips|donation|deposit|voucher|gift card|redemption|per additional|spectator|non[- ]?participant|observer|rider(?= only)|dog|dogs|pet|pets|kit|merchandise|parking|resident|residents|local|locals|military|member|members|comp|complimentary|crew|niño|niños|niña|niñas|nino|ninos|nina|ninas|bebé|bebe|infante"
                   r"|kinderen|kindje|peuter|peuters|jeugd|jongeren|studenten|senioren|65\+|korting|toeslag|bijboeking|optie|opties|fooi|borg|cadeaubon|familie|gezin|pakket|arrangement"
                   r"|aggiuntiv[oa]|adicional|adicionales|zusätzlich|zusätzliche|zusatzlich|zusatzliche|supplémentaire|supplementaire|extra persoon|bijboeken|optional|optioneel|aanbetaling|voorschot|deposito|caparra|kaution|anzahlung)\b|^add (a|an|the)\b", re.I)
NOT_A_PRICE = re.compile(r"\b(deposit|deposito|borg|aanbetaling|voorschot|caparra|kaution|anzahlung|voucher|gift card|cadeaubon|donation|gratuity|tip|tips|fooi|balance due|remaining balance)\b", re.I)
ACCESSORY = re.compile(r"\b(bag|bags|lock|helmet|child seat|seat cover|basket|poncho|raincoat|insurance|boots?|gloves?|hoods?|wetsuit|trailer|map|extra[- ]person|extra participants?|cooler|ice|fuel|gas|captain(?:'s)? fee)\b", re.I)
RENTAL_NAME = re.compile(r"\b(hire|rental|rentals|rent)\b", re.I)
AGE_RANGE = re.compile(r"\b\d{1,2}\s*(-|–|to)\s*\d{1,2}\s*(yrs|years|year olds|yr olds|y/o|y/old|yo)\b", re.I)
WORDNUM = r"(two|three|four|five|six|seven|eight|nine|ten|twelve|\d+)"
GROUP = re.compile(r"\b(per group|group|groups|party|parties|private|exclusive|charter|boat|vessel|catamaran|yacht|powerboat|sailboat|dinghy|jet ?ski|waverunner|kayak|canoe|paddle ?board|sup|raft|vehicle|car|jeep|van|suv|minibus|coach|table|room|cabin|villa|couple|couples|for two|for 2|whole|hire|rental|rentals|seater|nights?|berth|capacity|machine|unit|trip|cruise|cruises|includes up to"
                   r"|" + WORDNUM + r"\s*(people|persons|ppl|pax|guests|players|riders|passengers|adults|divers|snorkelers)|up to \d+|max(?:imum)?\.? ?\d+)\b", re.I)
BASE_WORDS = r"adult|adults|person|per person|standard|general|guest|guests|visitor|participant|passenger|rider|player|ticket|seat|single|individual|one person|1 person|per seat|snorkeler|snorkelers|diver|divers|swimmer|hiker|paddler|regular|normal|traveler|traveller|customer|passenger"
BASE = re.compile(r"\b(" + BASE_WORDS + r")\b", re.I); BASE_HEAD = re.compile(r"^(" + BASE_WORDS + r")\b", re.I)
BASE_AGE = re.compile(r"^\s*(1[0-9]|[2-5][0-9])\s*(years?|yrs?|y\.?o\.?)?\s*(and (up|over|older)|\+|plus)\b", re.I)
ADJ_HEAD = re.compile(r"^(standard|general|regular|normal)\b", re.I)
CUSTOMER_HEAD = re.compile(r"^(adult|adults|person|persons|standard|general|guest|guests|visitor|participant|passenger|rider|player|regular|normal|individual|single|seat|snorkeler|diver|\d{1,2}\s*(years?|yrs?)?\s*(and up|and over|\+))\b", re.I)
PER_PERSON = re.compile(r"\b(per (person|player|participant|head|adult|guest|rider|passenger|student|diver|snorkeler))\b|\beach person\b|\bpricing is per person\b|\b(1|one) (person|student|player|guest)\b(?!\s*(or|to|-|–|of))", re.I)   # G1: bare "pp"/"PP Fee" is a fee mention, not a unit assertion
ADDON_SELF = re.compile(r"per additional|\bprice per item\b|\bper extra person\b|\beach additional\b", re.I)
ADDON_LABEL = re.compile(r"\badditional\b|\bextra\b|\badd[- ]?on\b|\bsupplement\b|^add (a|an|the)\b|\boptional\b|\bupgrade\b", re.I)
VOLUME = re.compile(r"^(" + WORDNUM + r"\s*(or more|\+)?\s*(people|persons|adults|guests|players|passengers|students|divers|snorkelers)|groups? of|([2-9]|\d{2,})\s*(-|–|to|\+)\s*\d*\s*(people|persons|adults|guests|players|passengers|students))\b", re.I)
NAME_GROUP = re.compile(r"\b(hire|rental|rentals|charter|charters|private|boat|vessel|catamaran|yacht|powerboat|cruise|jeep)\b", re.I)
VESSEL = re.compile(r"\b(boat|boats|charter|charters|catamaran|yacht|powerboat|sailboat|sail|sailing|vessel|cruise|cruiser|dinghy|pontoon|trimaran|monohull|skiff|marlin|sportfish|sport ?fisher)\b", re.I)
NOT_VESSEL = re.compile(r"\b(jeep|jeeps|van|suv|car|cars|parasail|parasailing|kayak|kayaks|paddle ?board|sup|bike|bikes|e-?bike|scooter|segway|golf cart|atv|utv|buggy|hike|hiking|walk|walking|garden|villa|room|cabin|transfer|transport|transportation|shuttle|taxi|airport|jet ?ski|waverunner|flyboard)\b", re.I)
# s50 holds-packet refinements
R_PASSENGER_NOTE = re.compile(r"\b(stays? on ?board|on ?board only|non[- ]?participant|not diving|no diving|does not dive|spectat)", re.I)   # "ride along" is the rider on a UTV, not a spectator
R_OMITTED = re.compile(r"\b(ticket|tour|entry|admission|transport|transportation|transfer|gear|rental|farm tour|park access|drinks?)\s+only\b|\bno\s+(beach|lunch|food|meal|transport|transportation|pick-?up|snorkel(?:ing)?|drinks?|alcohol|shuttle)\b|\bwithout\s+(transport|transportation|lunch|beach|pick-?up)\b", re.I)
PARTICIPANT = re.compile(r"\b(divers?|snorkelers?|students?|riders?|paddlers?|players?)\b", re.I)
def never_class(t, tiers):
    """G2 + R-passenger + R-omitted: reasons a tier may never anchor (list of rule tags, empty if none)."""
    sing = (t.get('singular') or '').strip(); note = t.get('note') or ''; why = []
    if hit(NEVER, sing) or AGE_RANGE.search(sing) or AGE_RANGE.search(norm(sing)): why.append('never')
    if hit(NOT_A_PRICE, sing): why.append('not-a-price')
    if hit(ADDON_SELF, note): why.append('add-on-note')
    if re.search(r"\bpassengers?\b", sing, re.I) and (R_PASSENGER_NOTE.search(note) or any(PARTICIPANT.search(x.get('singular') or '') for x in tiers if x is not t)): why.append('R-passenger')
    if hit(R_OMITTED, sing): why.append('R-omitted')
    return why
def classify(t, product_name, tiers):
    sing = (t.get('singular') or '').strip(); note = t.get('note') or ''
    if not (t.get('priceCents') or 0) > 0: return 'zero'
    if never_class(t, tiers): return 'never'
    if VOLUME.search(sing): return 'group'
    if (BASE_HEAD.search(sing) and not (ADJ_HEAD.search(sing) and GROUP.search(sing))) or BASE_AGE.search(sing): return 'base'   # USVI G3: "Standard Full Day … Cruise" — an adjective head over a whole-unit token is not a seat
    if BASE.search(sing) and not GROUP.search(sing): return 'base'
    if PER_PERSON.search(note): return 'conflict' if GROUP.search(sing) else 'unnamed'   # G1 / D-484: two units asserted at once → held
    if GROUP.search(sing) or GROUP.search(note): return 'group'
    if NAME_GROUP.search(product_name or ''): return 'group'
    return 'unnamed'
PARTY_BAND = re.compile(WORDNUM + r"\s*(or more|\+)?\s*(people|person|persons|guests|pax|adults|players|passengers|divers|snorkelers)\b|\b(groups? of|up to \d|max(?:imum)?\.? ?\d|from \d|includes up to)", re.I)
def classify_ladder(tiers, product_name):
    cl = [(x, classify(x, product_name, tiers)) for x in tiers]
    if sum(1 for x, c in cl if c in ('base', 'group') and PARTY_BAND.search(x.get('singular') or '')) >= 2:
        cl = [(x, ('unnamed' if c in ('group', 'base') and not PARTY_BAND.search(x.get('singular') or '') and not CUSTOMER_HEAD.search(x.get('singular') or '') else c)) for x, c in cl]
    explicit = any(c in ('base', 'group') for _, c in cl)
    return [(x, ('base_implicit' if c == 'unnamed' and not explicit else c)) for x, c in cl]   # G1 / D-484: implicit unit never anchors

# ---- s49 unit derivation for group anchors (unchanged from s50) ----
WORD2N = dict(two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10, twelve=12)
AGE_PHRASE = re.compile(r"\b\d{1,2}\s*(?:-|–|to)?\s*\d{0,2}\s*(years?|yrs?|y\.?o\.?)\b(\s*(and (up|over|older)|olds?|\+))?|\b\d{1,2}\s*\+(?!\s*(people|persons|guests|pax))|\bages?\s*\d{1,2}(\s*(-|–|to|and|&)\s*(\d{1,2}|under|up|over))?", re.I)
DURATION = re.compile(r"\b\d{1,3}([.,]\d+)?\s*(hours?|hrs?|hr|h|minutes?|mins?|min|days?|nights?|weeks?)\b", re.I)
FEET = re.compile(r"\b\d{2,3}\s*(?:'|’|ft|foot|feet)\b", re.I)
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
UNIT_NOUN = re.compile(r"\b(jet ?skis?|waverunners?|boats?|charters?|catamarans?|yachts?|kayaks?|paddle ?boards?|sups?|jeeps?|vans?|suvs?|utvs?|atvs?|flights?|parasail (?:flights?|trips?)|sessions?|rentals?|vehicles?|bikes?|scooters?)\b", re.I)
def unit_chain_live(label, t):
    """s51 ruling packet: tier label → description quoted → product name quoted. Returns (unit, source) or (None, None)."""
    m = UNIT_NOUN.search(label)
    if m: return f"per {re.sub(r's$', '', m.group(1).lower()).replace('jetski', 'jet ski')}", f'tier label quoted: "{label}"'
    for field, src in (('description', 'description'), ('name', 'product name')):
        text = t.get(field) or ''
        c = CAP.search(text)
        if c:
            noun = 'boat' if VESSEL.search(t.get('name') or '') and not NOT_VESSEL.search(t.get('name') or '') else 'group'
            return f"per {noun}, up to {c.group(2)} {c.group(3).lower()}", f'{src} quoted: "{c.group(1)}"'
        pu = re.search(r"\b(per|price per|priced per)\s+(jet ?ski|boat|flight|vessel|vehicle|jeep|kayak|board|session|rental|group|party|person|seat|adult|guest)\b", text, re.I)
        if pu: return f"per {pu.group(2).lower()}", f'{src} quoted: "{pu.group(0)}"'
        m = UNIT_NOUN.search(text) if field == 'name' else None
        if m: return f"per {re.sub(r's$', '', m.group(1).lower())}", f'{src} quoted: "{m.group(0)}"'
    return None, None
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
def zero_base_reading(p, name):
    """R-zero-base: a reading whose base tiers are all $0 is a closed date."""
    cl = classify_ladder(p['tiers'], name)
    b = [x for x, c in cl if c == 'base' or (c == 'zero' and (BASE_HEAD.search(x.get('singular') or '') or BASE_AGE.search(x.get('singular') or '')))]
    return bool(b) and all(x['priceCents'] == 0 for x in b)
PLAUSIBLE_MIN_CENTS = 100

before = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
summary = []; disp = collections.Counter(); sweep_hits = []; reported = []; listed = []; residue_removed = 0
for t in pop:
    R = RUL[t['pk']]; kind = R['kind']
    v = ev['perPk'][str(t['pk'])]; ok = [p for p in v['probes'] if not p['error']]; present = [p for p in ok if not p['absent']]
    zb = [p for p in present if zero_base_reading(p, t['name'])]; sampled = [p for p in present if p not in zb]
    old = dict(price=t.get('price'), label=t.get('priceLabel'), conf=t.get('priceConfidence'), unit=(t.get('_unknownFields') or {}).get('priceUnit'))
    rec = dict(pk=t['pk'], name=t['name'], kind=kind, source=R['source'], old=old['price'], oldLabel=old['label'], oldConf=old['conf'], oldUnit=old['unit'],
               ruledPrice=R.get('ruledPrice'), ruledTier=R.get('ruledTier'), s40Hold=R.get('s40Hold'), readings=len(present), zeroBaseExcluded=len(zb), sampled=len(sampled))
    snapshot = json.dumps(t, sort_keys=True, ensure_ascii=False)
    def stamp():
        global residue_removed
        t['priceSource'] = SOURCE; t['priceEnrichmentSource'] = ENRICH_SOURCE; t['priceEnrichmentAt'] = ts; t['priceVerifiedAt'] = STAMP_DAY
        uf = t.get('_unknownFields')
        if uf and 'priceSource' in uf: del uf['priceSource']; residue_removed += 1
        if uf is not None and not uf: del t['_unknownFields']
    def set_unit(unit):
        uf = t.get('_unknownFields') or {}
        if unit: uf['priceUnit'] = unit
        else: uf.pop('priceUnit', None)
        if uf: t['_unknownFields'] = uf
        elif '_unknownFields' in t: del t['_unknownFields']
    def report(why, detail):
        """Reported, not written: the row stays byte-identical."""
        rec.update(disposition=f'REPORTED:{why}', detail=detail); disp[f'REPORTED:{why}'] += 1; reported.append(rec); summary.append(rec)
    evid = lambda: f"{len(sampled)}/{len(DATES)} open dated readings{f' ({honour_closed} closed-date $0 readings of the ruled tier excluded, R-zero-base)' if honour_closed else ''} ({sum(1 for p in sampled if p.get('dateValid'))} date-valid){f', {len(zb)} zero-base closed-date reading(s) excluded (R-zero-base)' if zb else ''}{f', {len(DATES)-len(ok)} probe error(s)' if len(ok) < len(DATES) else ''}, {len(collections.Counter(key(p) for p in sampled))} ladder shape(s)"
    # ---------------- no sampled reading ----------------
    if not sampled:
        d = 'UNSAMPLED' if ok else 'PROBE_ERROR'
        if False and kind == 'figure':   # s51 ruling packet: UNSAMPLED is standard — stamp low, dated; low never releases
            report(d, f"ruled tier \"{R.get('ruledTier')}\" ${R.get('ruledPrice')} ({R['source']}) could not be checked: {'absent from price-preview items[] on all ' + str(len(ok)) + ' probes' if ok else 'probe errors on all dates'}{f' ({len(zb)} zero-base closed-date readings)' if zb else ''}; stored figure left as ruled — empty availability is a date verdict, a fresh ruling is not unpublished on absence of evidence")
            continue
        stamp(); t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = 'unsampled' if ok else 'probe_error'
        stored = 'null' if old['price'] is None else f"${old['price']}"
        t['priceBasis'] = f"UNSAMPLED: absent from price-preview items[] on {len(ok)}/{len(DATES)} dated probes ({', '.join(DATES)}){f', {len(zb)} zero-base closed-date reading(s) excluded (R-zero-base)' if zb else ''}{f', {len(DATES)-len(ok)} probe error(s)' if len(ok) < len(DATES) else ''}; stored {stored}{f' ({old['label']})' if old['label'] else ''} retained unpublished pending a live reading (empty availability is a date verdict, not a liveness verdict){f'; prior: {R['source']}' if kind != 's40hold' else f'; prior: s40 HOLD {R.get('s40Hold')}'}"
        t['priceTiers'] = [dict(singular=x.get('singular'), plural=x.get('plural'), note=x.get('note') or '', priceCents=x.get('priceCents'), price=x.get('price'), minPartySize=x.get('minPartySize')) for x in (t.get('priceBreakdown') or [])]
        rec.update(disposition=d, new=t.get('price'), probeErrors=[p['error'] for p in v['probes'] if p['error']]); disp[d] += 1; summary.append(rec); continue
    counts = collections.Counter(key(p) for p in sampled); maj_key = counts.most_common(1)[0][0]; maj = next(p for p in sampled if key(p) == maj_key)
    cur = maj['liveCurrency']; tiers = maj['tiers']
    def cross_date(name, readings=None):
        """per-reading price of the named tier: cents, 0 (closed date — R-zero-base), or None (absent)"""
        out = []
        for p in (readings if readings is not None else sampled):
            m = [x for x in p['tiers'] if x['singular'] == name or norm(x['singular']) == norm(name)]
            out.append(min(x['priceCents'] for x in m) if m else None)
        return out
    rt = None; rp = None; honour_closed = 0
    if kind == 'figure':
        rt = R.get('ruledTier'); rp = R.get('ruledPrice')
        if rt is None:   # #135 relabel: figure ruled, tier unnamed → a per-person (base) tier carrying the ruled figure names it
            cl0 = classify_ladder(tiers, t['name']); cands = [x for x, c in cl0 if c == 'base' and abs(x['priceCents'] / 100 - (rp or 0)) < 0.005]
            if not cands:   # s51 ruling packet: the figure sits on a non-person tier → live unit chain (tier label → description → product name); live unit WINS over the #135 "per adult" relabel; nothing → HELD, named
                same = [x for x in tiers if abs(x['priceCents'] / 100 - (rp or 0)) < 0.005 and x['priceCents'] > 0]
                if not same:
                    hold('unnamed_tier_figure_gone', f"HELD (#135 relabel, figure gone): ruled figure ${rp} \"{R['ruledLabel']}\" ({R['source']}) names no tier and no live tier carries it; ladder {fmt(tiers)}; floor stamped unpublished; {evid()}; live {cur}", cheapest([x for x in tiers if x['priceCents'] > 0] or tiers)); summary.append(rec); continue
                anchor = same[0]; unit, src = unit_chain_live(anchor['singular'], t)
                if not unit:
                    hold('unit_underivable', f"HELD (unit underivable): #135 relabel \"{R['ruledLabel']}\" ${rp} sits on live tier \"{anchor['singular']}\" ({[c for x, c in cl0 if x is anchor][0]}), not a person tier; the live unit chain (tier label → description → product name) yields nothing; floor stamped unpublished pending a named ruling; ladder {fmt(tiers)}; {evid()}; live {cur}", anchor, keep_unit=False); summary.append(rec); continue
                rd = cross_date(anchor['singular'])
                if any(c is None for c in rd):
                    hold('ruled_tier_intermittent', f"HELD (live unit tier intermittent): \"{anchor['singular']}\" absent on {sum(1 for c in rd if c is None)} of {len(rd)} dates; {evid()}", anchor); summary.append(rec); continue
                rec['unitChain'] = src
                release(anchor, unit, 'live-unit', f"s51 ruling packet — live unit wins over the #135 \"{R['ruledLabel']}\" relabel: live tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} anchors, label verbatim, unit \"{unit}\" ({src}); the per adult label was a unit error; ladder {fmt(tiers)}; {evid()}; live USD", anchor['singular'], f"RULED 2026-08-26 (s51 packet) over {R['source']}: ")
                summary.append(rec); continue
            rt = cands[0]['singular']; rec['tierResolvedFromFigure'] = rt
        rd = cross_date(rt); P = [p for p, c in zip(sampled, rd) if c]; Z = sum(1 for c in rd if c == 0); A = sum(1 for c in rd if c is None)
        if not P:
            if Z and not A: report('TIER_ZERO', f"ruled tier \"{rt}\" ${rp} ({R['source']}) reads $0 on every sampled date ({Z} closed-date readings); {evid()}; a $0 whole-unit reading is the private/charter model, not a price — stored figure left as ruled, listed for ruling"); continue
            if A == len(rd):
                renamed = [x for x in tiers if x['priceCents'] > 0 and abs(x['priceCents'] / 100 - rp) < 0.005 and not never_class(x, tiers)]
                rr = cross_date(renamed[0]['singular']) if len(renamed) == 1 else []
                if len(renamed) == 1 and all(c is not None for c in rr) and all(abs(c / 100 - rp) < 0.005 for c in rr if c) and any(rr):   # $0 readings are closed dates (R-zero-base)
                    anchor = renamed[0]; rec['renamedFrom'] = rt; sampled = [p for p, c in zip(sampled, rr) if c]; honour_closed = sum(1 for c in rr if c == 0)
                    release(anchor, anchor['singular'], 'renamed-tier', f"s51 ruling (Flying Tiger, 2026-08-26) — tier renamed live: ruled tier \"{rt}\" ${rp} ({R['source']}) is gone, live tier \"{anchor['singular']}\" carries the identical figure on every open date → D-621 whole-boat re-anchor; the tier label \"{anchor['singular']}\" contains the unit (derivation source, quoted verbatim) → published as private boat, unit = label verbatim; ladder {fmt(tiers)}; {evid()}; live USD", 'private boat', f"RULED 2026-08-26 (s51 packet) over {R['source']}: ", keep_conf='high')
                    summary.append(rec); continue
                report('TIER_GONE', f"ruled tier \"{rt}\" ${rp} ({R['source']}) is not on any of the {len(sampled)} sampled readings; live ladder now {fmt(tiers)}; stored figure left as ruled — needs a ruling (wrong-anchor precedent)"); continue
            report('TIER_ZERO_OR_ABSENT', f"ruled tier \"{rt}\" ${rp} ({R['source']}) reads $0 on {Z} and is absent on {A} of {len(rd)} sampled dates; live ladder {fmt(tiers)}; stored figure left as ruled, listed for ruling"); continue
        if A:
            hold('ruled_tier_intermittent', f"HELD (ruled tier intermittent): ruled tier \"{rt}\" ${rp} ({R['source']}) is absent on {A} of {len(rd)} sampled dates (reads {[(u(c) if c else ('closed' if c == 0 else 'absent')) for c in rd]}); floor ${u(cheapest([x for x in tiers if x['priceCents'] > 0] or tiers)['priceCents'])} stamped unpublished pending a ruling; ladder {fmt(tiers)}; {evid()}; live {cur}", cheapest([x for x in tiers if x['priceCents'] > 0] or tiers)); summary.append(rec); continue
        honour_closed = Z; sampled = P   # closed-date ($0) readings of the ruled tier are excluded (R-zero-base); the majority ladder is chosen among open dates
        counts = collections.Counter(key(p) for p in sampled); maj_key = counts.most_common(1)[0][0]; maj = next(p for p in sampled if key(p) == maj_key)
        cur = maj['liveCurrency']; tiers = maj['tiers']
    classes = classify_ladder(tiers, t['name']); rec['tiers'] = [dict(singular=x['singular'], note=x.get('note') or '', price=u(x['priceCents']), min=x.get('min'), cls=c, never=never_class(x, tiers)) for x, c in classes]
    base = [x for x, c in classes if c == 'base']; group = [x for x, c in classes if c == 'group']; nz = [x for x in tiers if x['priceCents'] > 0]
    implicit = [x for x, c in classes if c == 'base_implicit' and x['priceCents'] > 0]; conflict = [x for x, c in classes if c == 'conflict' and x['priceCents'] > 0]
    never_nz = [x for x, c in classes if c == 'never' and x['priceCents'] > 0]
    cheapest = lambda xs: min(xs, key=lambda x: x['priceCents'])
    skipped = lambda: ', '.join(f"{x['singular']} ${u(x['priceCents'])} [{c}]" for x, c in classes if c != 'base' and x['priceCents'] > 0)
    def write_tiers():
        t['priceBreakdown'] = [dict(id=c['id'], singular=c['singular'], plural=c['plural'], note=c['note'], priceCents=c['priceCents'], price=u(c['priceCents']), minPartySize=c['min']) for c in tiers]
        t['priceIncludesBookingFees'] = maj['includeFees']; t['priceIncludesTaxes'] = maj['includeTaxes']
        t['priceTiers'] = [dict(singular=c['singular'], plural=c['plural'], note=c['note'] or '', priceCents=c['priceCents'], price=u(c['priceCents']), minPartySize=c['min']) for c in tiers]
    def hold(status, basis, floor, keep_unit=False):
        stamp(); write_tiers(); t['currency'] = SITE_CUR if cur == SITE_CUR else t.get('currency'); t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = status
        t['price'] = u(floor['priceCents']); t['priceLabel'] = floor['singular']; t['priceBasis'] = basis
        if not keep_unit: set_unit(None)
        rec.update(disposition='HELD', hold=status, new=t['price'], label=floor['singular']); disp[f'HELD:{status}'] += 1
        if status not in ('d482_ambiguous', 'no_base_tier', 'd484_no_unit', 'd484_unit_conflict', 'hire_accessory', 'mixed_verdict'): listed.append(rec)
    def release(anchor, unit, rule, basis, gate_label, prefix='', keep_conf=None):
        reads = cross_date(anchor['singular']); closed = sum(1 for c in reads if c == 0); prices = {c for c in reads if c}
        if None in reads:
            return hold('mixed_verdict', f"HELD (mixed verdict across dates): anchor \"{anchor['singular']}\" absent on {sum(1 for c in reads if c is None)} of {len(sampled)} sampled dates (reads {[(u(c) if c else ('closed' if c == 0 else 'absent')) for c in reads]}); floor ${u(cheapest(nz)['priceCents'])} stamped unpublished; would have been {rule}; ladder {fmt(tiers)}; {evid()}; live {cur}", cheapest(nz))
        assert prices, ('anchor reads $0 on every sampled date', t['pk'], anchor['singular'])
        n_read = len(sampled) - closed
        if anchor['priceCents'] <= PLAUSIBLE_MIN_CENTS:
            return hold('implausible_floor', f"HELD (P-floor): anchor \"{anchor['singular']}\" ${u(anchor['priceCents'])} is at or below $1 — a placeholder/selector, not a fare (a size-{len(nz)} tier set makes D-482 agreement vacuous); would have been {rule}; ladder {fmt(tiers)}; {evid()}; live {cur}", cheapest(nz))
        season = '' if not closed else f"; {closed} reading(s) where \"{anchor['singular']}\" is $0 excluded as closed dates (R-zero-base)"
        if len(prices) > 1:   # R-season: present on every open date at different prices → cross-date floor anchors as From
            floor_c = min(prices); rd = ' / '.join(('closed' if c == 0 else str(u(c))) for c in reads)
            season += f"; R-season: \"{anchor['singular']}\" reads {rd} across {len(sampled)} dated probes, cross-date floor ${u(floor_c)} anchors as From (majority reading ${u(anchor['priceCents'])})"
            anchor = dict(anchor, priceCents=floor_c); rule = rule + '+R-season'
        stamp(); write_tiers(); conf = 'high' if n_read >= 2 else 'medium'
        unchanged_ruled = keep_conf is not None and old['price'] == u(anchor['priceCents'])
        if unchanged_ruled and conf != keep_conf: season += f"; {n_read} open-date reading(s) — figure unchanged from the ruling, ruled confidence {keep_conf} retained (not re-derived from a date verdict)"; conf = keep_conf
        t['currency'] = SITE_CUR; t['price'] = u(anchor['priceCents']); t['priceLabel'] = gate_label; t['priceConfidence'] = conf; t['priceEnrichmentStatus'] = 'high'
        t['priceBasis'] = prefix + basis + season + (f"; single open-date reading → medium" if conf == 'medium' else f"; anchor identical on all {n_read} open sampled dates" if len(prices) == 1 else '')
        set_unit(unit)
        if ADDON_LABEL.search(anchor['singular']) or ADDON_SELF.search(anchor.get('note') or ''): sweep_hits.append((t['pk'], anchor['singular'], anchor.get('note')))
        changed = old['price'] != t['price']; d = f"{rule}:{'repriced' if changed else 'unchanged'}"
        rec.update(disposition=d, rule=rule, new=t['price'], label=gate_label, tier=anchor['singular'], unit=unit, conf=conf, renders=(gate_label == 'per adult' and conf in ('high', 'medium')) or (gate_label == 'private boat' and conf == 'high')); disp[d] += 1
    # machine anchor (for concordance on honoured rows, and as the verdict on machine rows)
    def machine():
        if not nz: return ('zero_price', None)
        if cur != SITE_CUR: return ('D-620', None)
        if conflict and not base: return ('HELD:d484_unit_conflict', None)
        if implicit and not base and not group: return ('HELD:d484_no_unit', None)
        if base and group and hybrid_couple(base, group): return ('D-614', hybrid_couple(base, group))
        if base and group and r1_ladder(base, group): return ('s48-R1', r1_ladder(base, group)[1])
        if base:
            anchor = cheapest(base); pos0 = next((x for x, c in classes if c in ('base', 'group') and x['priceCents'] > 0), None)
            if pos0 is not None and pos0['priceCents'] != anchor['priceCents']: return ('HELD:d482_ambiguous', None)
            return ('D-624', anchor)
        if group:
            g = [x for x in group if not ACCESSORY.search(x['singular'])] if RENTAL_NAME.search(t['name']) and not ACCESSORY.search(t['name']) else group
            if not g: return ('HELD:hire_accessory', None)
            return ('D-614/D-621', cheapest(g))
        if len(nz) == 1 and never_nz and not implicit and not conflict: return ('single-tier', nz[0])
        return ('HELD:no_base_tier', None)
    m_rule, m_anchor = machine(); rec['machine'] = dict(rule=m_rule, tier=m_anchor['singular'] if m_anchor else None, price=u(m_anchor['priceCents']) if m_anchor else None)
    # ---------------- HONOUR branch ----------------
    if kind == 'figure':
        live = [x for x in tiers if (x['singular'] == rt or norm(x['singular']) == norm(rt)) and x['priceCents'] > 0]
        assert live, ('ruled tier missing from the open-date majority ladder', t['pk'], rt)
        anchor = min(live, key=lambda x: x['priceCents']); nc = never_class(anchor, tiers)
        rec['closedDateReadings'] = honour_closed
        if nc:
            hold('ruled_tier_now_never', f"HELD (ruled tier now classifies never-anchor under the settled rules: {', '.join(nc)}): ruled tier \"{rt}\" ${rp} ({R['source']}) reads ${u(anchor['priceCents'])} live; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished pending a ruling; ladder {fmt(tiers)}; {evid()}; live {cur}", cheapest(nz)); summary.append(rec); continue
        if cur != SITE_CUR:
            hold(f'non_usd_currency:{cur}', f"HELD (D-620): live details.currency {cur} ≠ site USD; ruled tier \"{rt}\" reads {cur} {u(anchor['priceCents'])}; {evid()}", anchor); summary.append(rec); continue
        agree = m_anchor is not None and (m_anchor['singular'] == anchor['singular'])
        rec['classifierAgrees'] = agree
        if not agree: listed.append(dict(rec, listedAs='classifier-disagreement'))
        prefix = f"HONOURED {R['source']}: ruled tier \"{rt}\" ${rp} looked up by name on every sampled reading; "
        basis = (f"reads ${u(anchor['priceCents'])} live — {'unchanged' if abs(anchor['priceCents'] / 100 - rp) < 0.005 else f'DRIFT from ruled ${rp}, repriced from live'}; label \"{R['ruledLabel']}\"{f' + unit \"{R['ruledUnit']}\"' if R.get('ruledUnit') else ''} kept from the ruling; "
                 f"classifier {'agrees' if agree else 'DISAGREES'} ({m_rule}{f' → \"{m_anchor['singular']}\" ${u(m_anchor['priceCents'])}' if m_anchor else ''}){f'; not anchoring: {skipped()}' if skipped() else ''}; ladder {fmt(tiers)}; {evid()}; live USD")
        release(anchor, R.get('ruledUnit'), 'honoured', basis, R['ruledLabel'], prefix, keep_conf=R.get('ruledConf') or old['conf'])
        summary.append(rec); continue
    # ---------------- MACHINE branch (s40 HOLD-only, nulls, 11993) ----------------
    prior = f"prior: s40 HOLD {R.get('s40Hold')} (tier seen \"{R.get('s40TierSeen')}\")" if kind == 's40hold' else f"prior: {R['source']}"
    prefix = f"{prior}; re-probed under the settled rule set: "
    if not nz:
        stamp(); write_tiers(); t['price'] = None; t['priceLabel'] = None; t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = 'zero_price'; t['currency'] = SITE_CUR if cur == SITE_CUR else t.get('currency'); set_unit(None)
        t['priceBasis'] = prefix + f"zero_price: every live tier is $0 on the majority reading ({' / '.join(x['singular'] for x in tiers)}); {evid()}; live {cur}"
        rec.update(disposition='zero_price', new=None); disp['zero_price'] += 1
    elif cur != SITE_CUR:
        anchor = cheapest(base or nz); stamp(); write_tiers(); set_unit(None)
        t['currency'] = cur; t['price'] = u(anchor['priceCents']); t['priceLabel'] = anchor['singular']; t['priceConfidence'] = 'low'; t['priceEnrichmentStatus'] = f"non_usd_currency:{cur}"
        t['priceBasis'] = prefix + f"HELD (D-620): live details.currency {cur} ≠ site USD; true amount {cur} {t['price']} ({anchor['singular']}) stamped, unpublished; {evid()}"
        rec.update(disposition='D-620', new=t['price'], currency=cur); disp['D-620'] += 1
    elif conflict and not base:
        hold('d484_unit_conflict', prefix + f"HELD (D-484 unit conflict): tier(s) {', '.join(f'\"{x['singular']}\" ${u(x['priceCents'])} (note: {x.get('note') or ''})' for x in conflict)} carry a party-shaped label with a per-person note — two units asserted at once; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished pending a ruling; ladder {fmt(tiers)}; {evid()}; live USD", cheapest(nz))
    elif implicit and not base and not group:
        hold('d484_no_unit', prefix + f"HELD (D-484 no asserted person unit): ladder {fmt(tiers)} names no adult/base or party tier — {', '.join(f'\"{x['singular']}\"' for x in implicit[:4])}{' …' if len(implicit) > 4 else ''} is a duration/thing token, not a unit; floor ${u(cheapest(nz)['priceCents'])} ({cheapest(nz)['singular']}) stamped unpublished pending a ruling; {evid()}; live USD", cheapest(nz))
    elif base and group and hybrid_couple(base, group):
        anchor = hybrid_couple(base, group); gl = 'private boat' if is_vessel(t, anchor) else anchor['singular']
        release(anchor, anchor['singular'], 'D-614', f"D-614 hybrid ladder: couple tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} is the smallest bookable unit and anchors with the tier label verbatim as unit; per-person tiers ({', '.join(f'{x['singular']} ${u(x['priceCents'])}' for x in base)}) do not anchor; ladder {fmt(tiers)}; {evid()}; live USD", gl, prefix)
    elif base and group and r1_ladder(base, group):
        n, anchor = r1_ladder(base, group); unit = f"per person, {anchor['singular']}"
        release(anchor, unit, 's48-R1', f"s48-R1 per-head rate ladder (price per head falls as band grows; 1-person tier ${u(cheapest(base)['priceCents'])} is the dearest, not a From anchor): largest band \"{anchor['singular']}\" ${u(anchor['priceCents'])} per person anchors with unit \"{unit}\"; ladder {fmt(tiers)}; {evid()}; live USD", 'per adult', prefix)
    elif base:
        anchor = cheapest(base)
        pos0 = next((x for x, c in classes if c in ('base', 'group') and x['priceCents'] > 0), None)
        if pos0 is not None and pos0['priceCents'] != anchor['priceCents']:
            hold('d482_ambiguous', prefix + f"HELD (D-482 ambiguous full-fare set): position-0 eligible tier \"{pos0['singular']}\" ${u(pos0['priceCents'])} ≠ discount-exclusion pick \"{anchor['singular']}\" ${u(anchor['priceCents'])}; floor ${u(cheapest(nz)['priceCents'])} stamped unpublished; ladder {fmt(tiers)}; {evid()}; live USD", cheapest(nz))
        else:
            bs = band_size(anchor['singular']); unit = f"per person, {anchor['singular']}" if bs and bs >= 2 and PARTY_BAND.search(anchor['singular']) else None
            release(anchor, unit, 'D-624', f"D-624 cheapest adult/base per-person tier \"{anchor['singular']}\" ${u(anchor['priceCents'])}{f' of {len(base)} base tiers (D-625)' if len(base) > 1 else ''}, published as per adult{f'; unit \"{unit}\"' if unit else ''}{f'; not anchoring: {skipped()}' if skipped() else ''}; ladder {fmt(tiers)}; {evid()}; live USD", 'per adult', prefix)
    elif group and RENTAL_NAME.search(t['name']) and not ACCESSORY.search(t['name']) and not [x for x in group if not ACCESSORY.search(x['singular'])]:
        hold('hire_accessory', prefix + f"HELD (hire/rental rule): no non-accessory hire tier in ladder {fmt(tiers)}; floor ${u(cheapest(nz)['priceCents'])} ({cheapest(nz)['singular']}) stamped unpublished; {evid()}; live USD", cheapest(nz))
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
        release(anchor, unit, rule, f"{how}; no standalone adult/base per-person tier{f'; not anchoring: {skipped()}' if skipped() else ''}; ladder {fmt(tiers)}; {evid()}; live USD", gl, prefix)
    elif len(nz) == 1 and never_nz and not implicit and not conflict and not ADDON_LABEL.search(nz[0]['singular']) and not ADDON_SELF.search(nz[0].get('note') or '') and not NOT_A_PRICE.search(nz[0]['singular']):
        anchor = nz[0]; gl = 'per adult' if PER_PERSON.search(anchor.get('note') or '') or BASE.search(anchor['singular']) else ('private boat' if is_vessel(t, anchor) and GROUP.search(anchor['singular']) else anchor['singular'])
        release(anchor, anchor['singular'] if gl != 'per adult' else None, 'single-tier', f"single-tier product (s49 wave-2 rule: the sole tier is the entire audience): tier \"{anchor['singular']}\" ${u(anchor['priceCents'])} anchors; published as {gl}; {evid()}; live USD", gl, prefix)
    else:
        floor = cheapest(nz); unnamed = [x for x, c in classes if c == 'unnamed' and x['priceCents'] > 0]
        hold('no_base_tier', prefix + f"HELD (no adult/base tier): live ladder {fmt(tiers)} has no anchorable tier ({', '.join(f'{x['singular']} [{'/'.join(never_class(x, tiers))}]' for x in never_nz)}{'; ' if never_nz and unnamed else ''}{', '.join(f'{x['singular']} [unnamed extra]' for x in unnamed)}); floor ${u(floor['priceCents'])} ({floor['singular']}) stamped unpublished pending a ruling; {evid()}; live USD", floor)
    if kind == 's40hold' and rec.get('disposition', '').split(':')[0] in ('D-624', 'D-614', 'D-621', 's48-R1', 'single-tier', 'D-624+R-season', 'D-614+R-season', 'D-621+R-season', 's48-R1+R-season', 'single-tier+R-season'): rec['s40HoldReleased'] = True
    summary.append(rec)
assert not sweep_hits, ('ABORT: add-on-shaped anchor tier(s)', sweep_hits)
after = {t['pk']: hashlib.sha256(json.dumps(t, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for t in rows}
changed = [pk for pk in after if after[pk] != before[pk]]; outside = [pk for pk in changed if pk not in pop_set]
assert not outside and len(rows) == len(before), ('rows outside population changed', outside)
rep_pks = {r['pk'] for r in reported}
assert all(after[pk] == before[pk] for pk in rep_pks), 'a reported-not-written row was modified'
untouched = [t['pk'] for t in pop if after[t['pk']] == before[t['pk']] and t['pk'] not in rep_pks]
assert not untouched, ('population rows without a fresh stamp and not reported', untouched)
assert all(t.get('priceSource') == SOURCE for t in pop if t['pk'] not in rep_pks)
out = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
result = dict(stampedAt=ts, population=len(pop), rowsChanged=len(changed), reportedNotWritten=len(reported), residuePriceSourceRemoved=residue_removed, disposition=dict(disp),
              s40HoldReleased=sum(1 for r in summary if r.get('s40HoldReleased')), classifierDisagreements=sum(1 for r in summary if r.get('classifierAgrees') is False),
              sha256=dict(before=hashlib.sha256(raw).hexdigest(), after=hashlib.sha256(out.encode()).hexdigest()), reported=reported, listedForRuling=listed, summary=summary)
print(json.dumps({k: result[k] for k in ('stampedAt', 'population', 'rowsChanged', 'reportedNotWritten', 'residuePriceSourceRemoved', 'disposition', 's40HoldReleased', 'classifierDisagreements', 'sha256')}, indent=1), 'EXECUTE' if execute else 'DRY RUN')
if execute:
    open(DATA, 'w', encoding='utf-8').write(out); json.dump(result, open(f'{EV}/apply-summary.json', 'w'), indent=1, ensure_ascii=False); print('WROTE', DATA)
elif os.environ.get('DRY_OUT'):
    json.dump(result, open(os.environ['DRY_OUT'], 'w'), indent=1, ensure_ascii=False)
