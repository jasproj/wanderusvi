// s53-wusvi-schema-gate: dump the unit-evidence vocabulary of the EMITTING
// population (the loadTours draw pool, app.js:170 gate applied literally) so
// the three-state classifier is built from this repo's own data, not from a
// guessed word list.
// usage: node vocab.mjs <app.js> <tours-data.json>
import fs from 'fs';
import vm from 'vm';

const [appPath, dataPath] = process.argv.slice(2);
const src = fs.readFileSync(appPath, 'utf8');
const d = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const rows = Array.isArray(d) ? d : d.tours;

const ctx = vm.createContext({ console, window: undefined, document: undefined });
vm.runInContext(
  src.slice(0, src.indexOf('// Fisher-Yates shuffle')) +
    '\n;globalThis.__x={priceUnit};',
  ctx
);
const { priceUnit } = ctx.__x;

// The loadTours() draw-pool filter, verbatim (app.js:170). Every row here is
// a card that renders, and every rendered card calls generateTourSchema().
const pool = rows.filter((t) => t.status !== 'inactive' && !t.bookingDead);
console.log(`pool (emitting population): ${pool.length} of ${rows.length} rows`);

const priceGated = (t) => t.priceLabel === 'per adult' && (t.priceConfidence === 'high' || t.priceConfidence === 'medium');
const today = pool.filter(priceGated);
const rest = pool.filter((t) => !priceGated(t));
console.log(`already bare-price-gated today (priceLabel === 'per adult', confidence high/medium): ${today.length}`);
console.log(`remaining rows (candidates for state 2/3): ${rest.length}`);

function anchorTier(t) {
  const pb = Array.isArray(t.priceBreakdown) ? t.priceBreakdown : [];
  return pb.find((p) => p.price === t.price) || null;
}

function tally(label, values) {
  const m = new Map();
  for (const v of values) m.set(v, (m.get(v) || 0) + 1);
  console.log(`\n== ${label} (${m.size} distinct) ==`);
  [...m.entries()]
    .sort((a, b) => b[1] - a[1])
    .forEach(([k, n]) => console.log(`${String(n).padStart(5)}  ${k}`));
}

tally('priceUnit (_unknownFields.priceUnit via priceUnit()) — rest only', rest.map((t) => priceUnit(t) || '<empty>'));
tally('priceLabel — rest only', rest.map((t) => (t.priceLabel || '<null>').trim() || '<empty>'));
tally('anchor tier singular — rest only', rest.map((t) => {
  const a = anchorTier(t);
  return a ? (a.singular || '<no-singular>').trim() : '<no-anchor-tier>';
}));
tally('priceConfidence — rest only', rest.map((t) => t.priceConfidence || '<null>'));
