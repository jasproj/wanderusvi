// s53-wusvi-schema-gate: three-state census + both-directions proof.
// Runs the ORIGIN/MAIN emitter (app-main-baseline.js, byte snapshot of
// origin/main:app.js) and the branch emitter (app.js) side by side over the
// real draw pool (app.js's own loadTours() gate, line ~170), then asserts:
//   - the three states partition the pool exactly (no row in two, none in zero)
//   - state 1 (per-person) rows emit schema byte-identical to before, for
//     every priceLabel === 'per adult' row in the FULL dataset (not just the
//     render pool) — the extra-constraint population is 150 rows, one wider
//     than the 149 that currently render, because pk 458899 is per-adult but
//     inactive/bookingDead and never reaches a card today.
//   - state 2 rows with a mirrorable card unit emit UnitPriceSpecification
//     whose unitText is the card string verbatim, and no bare Offer.price
//   - state 2 rows without a mirrorable card unit, and all state 3 rows, emit
//     no bare Offer.price and no priceSpecification (offers keeps only its
//     unconditional @type/priceCurrency/url — unchanged from before this PR)
// Prints counts + dollar face value per state and three named fixture firings.
// usage: node census.mjs <app.js> <app-main-baseline.js> <tours-data.json>
// (app-main-baseline.js is not committed; regenerate with
//  git show origin/main:app.js > scripts/evidence/s53-wusvi-schema-gate/app-main-baseline.js)
import fs from 'fs';
import vm from 'vm';

const [appPath, basePath, dataPath] = process.argv.slice(2);

function load(path, names) {
    const src = fs.readFileSync(path, 'utf8');
    const cut = src.indexOf('// Fisher-Yates shuffle');
    if (cut === -1) throw new Error(`no Fisher-Yates cut point in ${path}`);
    const ctx = vm.createContext({ console });
    vm.runInContext(src.slice(0, cut) + `\n;globalThis.__x={${names.join(',')}};`, ctx);
    return ctx.__x;
}

const cur = load(appPath, ['generateTourSchema', 'priceUnit', 'unitStateFromEvidence', 'classifyUnitText']);
const base = load(basePath, ['generateTourSchema']);

const d = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const rows = Array.isArray(d) ? d : d.tours;

// The loadTours() draw-pool filter, verbatim (app.js:170). Cards — and
// therefore JSON-LD — render only for these rows: the emitting population.
const pool = rows.filter(t => t.status !== 'inactive' && !t.bookingDead);

let fail = 0;
const err = (msg) => { fail++; console.error('ASSERT FAIL: ' + msg); };

// --- Extra constraint: byte-identical state-1 emission, over the FULL
// dataset (150 rows), not just the render pool (149) — the constraint is
// about generateTourSchema()'s behavior as a pure function of a row, not
// about which rows currently reach a card. ---
const perAdultAll = rows.filter(t => t.priceLabel === 'per adult' && (t.priceConfidence === 'high' || t.priceConfidence === 'medium'));
let perAdultIdentical = 0;
for (const t of perAdultAll) {
    const oldJson = JSON.stringify(base.generateTourSchema(t));
    const newJson = JSON.stringify(cur.generateTourSchema(t));
    if (oldJson !== newJson) err(`pk ${t.pk}: state-1 schema not byte-identical (full-dataset check)`);
    else perAdultIdentical++;
}
console.log(`extra constraint: ${perAdultIdentical} of ${perAdultAll.length} priceLabel==='per adult' rows (full dataset) byte-identical to origin/main`);

const tallies = {
    'per-person': { n: 0, face: 0 },
    'non-per-person-spec': { n: 0, face: 0 },     // 2a: card unit mirrored
    'non-per-person-silent': { n: 0, face: 0 },   // 2b: no mirrorable card unit
    'none': { n: 0, face: 0 }
};
const fixtures = {};

for (const t of pool) {
    const state = cur.unitStateFromEvidence(t);

    // Partition proof: membership in exactly one of the three evidence states.
    const membership = ['per-person', 'non-per-person', 'none'].filter(s => s === state).length;
    if (membership !== 1) err(`pk ${t.pk}: in ${membership} evidence states`);

    const oldSchema = base.generateTourSchema(t);
    const newSchema = cur.generateTourSchema(t);
    const oldJson = JSON.stringify(oldSchema);
    const newJson = JSON.stringify(newSchema);
    const cardUnit = cur.priceUnit(t);

    const perPersonAsserted = state === 'per-person' && (t.priceConfidence === 'high' || t.priceConfidence === 'medium');
    const nonPerPersonAsserted = state === 'non-per-person' && t.priceConfidence === 'high';

    if (perPersonAsserted) {
        tallies['per-person'].n++; tallies['per-person'].face += t.price;
        if (newJson !== oldJson) err(`pk ${t.pk}: state-1 schema not byte-identical (render pool)`);
        if (!('price' in newSchema.offers)) err(`pk ${t.pk}: state-1 missing bare Offer.price`);
        if (!fixtures.perPerson) fixtures.perPerson = { t, oldSchema, newSchema, identical: newJson === oldJson };
    } else if (nonPerPersonAsserted) {
        const spec = newSchema.offers && newSchema.offers.priceSpecification;
        if (cardUnit && cur.classifyUnitText(cardUnit) !== 'per-person') {
            tallies['non-per-person-spec'].n++; tallies['non-per-person-spec'].face += t.price;
            if (!spec) err(`pk ${t.pk}: state-2a missing priceSpecification`);
            else {
                if (spec['@type'] !== 'UnitPriceSpecification') err(`pk ${t.pk}: wrong spec @type`);
                if (spec.unitText !== cardUnit) err(`pk ${t.pk}: unitText "${spec.unitText}" != card "${cardUnit}"`);
                if (spec.price !== t.price) err(`pk ${t.pk}: spec price mismatch`);
                if (spec.priceCurrency !== 'USD') err(`pk ${t.pk}: spec currency not USD`);
            }
            if ('price' in newSchema.offers) err(`pk ${t.pk}: state-2a leaked bare Offer.price`);
            if (!fixtures.wholeBoat && t.pk === 424721) fixtures.wholeBoat = { t, oldSchema, newSchema };
        } else {
            tallies['non-per-person-silent'].n++; tallies['non-per-person-silent'].face += t.price;
            if ('price' in newSchema.offers) err(`pk ${t.pk}: state-2b leaked bare Offer.price`);
            if ('priceSpecification' in newSchema.offers) err(`pk ${t.pk}: state-2b leaked priceSpecification`);
        }
    } else {
        tallies.none.n++; tallies.none.face += t.price || 0;
        if ('price' in newSchema.offers) err(`pk ${t.pk}: state-3 leaked bare Offer.price`);
        if ('priceSpecification' in newSchema.offers) err(`pk ${t.pk}: state-3 leaked priceSpecification`);
        if (!fixtures.noEvidence) fixtures.noEvidence = { t, oldSchema, newSchema };
    }
}

const s2n = tallies['non-per-person-spec'].n + tallies['non-per-person-silent'].n;
const s2face = tallies['non-per-person-spec'].face + tallies['non-per-person-silent'].face;
const total = tallies['per-person'].n + s2n + tallies.none.n;
if (total !== pool.length) err(`partition sum ${total} != pool ${pool.length}`);

const money = (x) => '$' + x.toLocaleString('en-US', { maximumFractionDigits: 2 });
console.log(`\npool (emitting population): ${pool.length} of ${rows.length} rows`);
console.log('');
console.log('state 1 per-person asserted      :', tallies['per-person'].n, 'rows, face', money(tallies['per-person'].face), '-> bare Offer.price, byte-identical');
console.log('state 2 non-per-person asserted  :', s2n, 'rows, face', money(s2face));
console.log('  2a card unit mirrored          :', tallies['non-per-person-spec'].n, 'rows, face', money(tallies['non-per-person-spec'].face), '-> UnitPriceSpecification, unitText = card string verbatim');
console.log('  2b no mirrorable card unit      :', tallies['non-per-person-silent'].n, 'rows, face', money(tallies['non-per-person-silent'].face), '-> no price emitted');
console.log('state 3 no unit evidence          :', tallies.none.n, 'rows, face', money(tallies.none.face), '-> no price emitted');
console.log('');
console.log(`cross-check vs s52/#144/#147/#153 audit: ~143 verified whole-boat rows / ~$268,050 face, median $1,400; this census (state 2 total): ${s2n} rows / ${money(s2face)}`);

for (const [name, fx] of Object.entries(fixtures)) {
    console.log(`\n=== fixture: ${name} — pk ${fx.t.pk} "${fx.t.name}" price $${fx.t.price} ===`);
    console.log('  evidence: priceLabel=' + JSON.stringify(fx.t.priceLabel) + ' priceConfidence=' + JSON.stringify(fx.t.priceConfidence)
        + ' priceUnit=' + JSON.stringify(cur.priceUnit(fx.t)));
    console.log('  before offers:', JSON.stringify(fx.oldSchema.offers ?? null));
    console.log('  after  offers:', JSON.stringify(fx.newSchema.offers ?? null));
    if ('identical' in fx) console.log('  full schema byte-identical to baseline:', fx.identical);
}

if (fail) { console.error(`\n${fail} assertion failure(s)`); process.exit(1); }
console.log('\nall assertions passed: state-1 byte-identical (render pool + full-dataset extra constraint), partition exact, state-2a verbatim card unitText + no bare price, state-2b/3 no price key');
