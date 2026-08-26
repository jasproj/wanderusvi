// s50 PR-A fixture proof: priceUnit render port, both dynamic paths, before/after.
// Usage: node verify-priceunit.mjs <before-ref> <after-ref>   (refs resolved via git show)
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
const [beforeRef, afterRef] = process.argv.slice(2);
const show = (ref, f) => ref === 'WORKTREE' ? fs.readFileSync(f, 'utf8') : execFileSync('git', ['show', `${ref}:${f}`], { encoding: 'utf8', maxBuffer: 1 << 28 });
const data = JSON.parse(show(afterRef, 'tours-data.json'));
const FIXTURE_PK = 2101; // first live per-adult row: gets a synthetic priceUnit in the "with" run
const fixture = (rows) => rows.map(r => r.pk === FIXTURE_PK ? { ...r, _unknownFields: { ...(r._unknownFields || {}), priceUnit: 'per adult · up to 6 guests' } } : r);
const rows = data.tours;
const live = rows.filter(t => t.status !== 'inactive' && !t.bookingDead);

function elem() { const e = { innerHTML: '', hidden: false, textContent: '', style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {},
  addEventListener() {}, getAttribute(k) { return e._a?.[k] ?? null; }, setAttribute() {}, appendChild() {}, querySelector: () => elem(), querySelectorAll: () => [], value: '' }; return e; }

function runApp(ref, tours) {
  const ctx = { console: { log() {}, warn() {}, error() {} }, window: {}, localStorage: { getItem: () => null, setItem() {} }, sessionStorage: { getItem: () => null, setItem() {} }, gtag() {}, setTimeout() {}, URLSearchParams,
    document: { addEventListener() {}, getElementById: () => elem(), querySelector: () => elem(), querySelectorAll: () => [], createElement: () => elem(), body: elem() },
    fetch: () => new Promise(() => {}) };
  ctx.window = ctx; vm.createContext(ctx);
  vm.runInContext(show(ref, 'app.js'), ctx, { filename: 'app.js' });
  return tours.map(t => ctx.createTourCard(t)).join('\n');
}
async function runActivity(ref, tag, preferPerSeat, tours) {
  const grid = elem(); grid._a = { 'data-activity-tag': tag, 'data-activity-label': tag.toLowerCase(), 'data-prefer-per-seat': preferPerSeat ? 'true' : 'false' };
  const status = elem(), browse = elem();
  const ctx = { console: { log() {}, warn() {}, error() {} },
    document: { getElementById: (id) => ({ 'activity-tours-grid': grid, 'activity-tours-status': status, 'activity-browse-all': browse })[id] || null },
    fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ tours }) }), setTimeout };
  ctx.window = ctx; vm.createContext(ctx);
  vm.runInContext(show(ref, 'activity-tours.js'), ctx, { filename: 'activity-tours.js' });
  await new Promise(r => setTimeout(r, 20));
  return grid.innerHTML;
}
const count = (html, re) => (html.match(re) || []).length;
const PAGES = [['Snorkel', true], ['Kayak', true], ['Jet Ski Tour', false], ['Fishing', false], ['Zipline', false]];
const out = { fixturePk: FIXTURE_PK, live: live.length, app: {}, activity: {} };
for (const [label, tours] of [['without', live], ['with', fixture(live)]]) {
  const b = runApp(beforeRef, tours), a = runApp(afterRef, tours);
  out.app[label] = { cards_before: count(b, /<article class="tour-card"/g), cards_after: count(a, /<article class="tour-card"/g),
    price_before: count(b, /<div class="tour-price">/g), price_after: count(a, /<div class="tour-price">/g),
    small_before: count(b, /<small>/g), small_after: count(a, /<small>/g), identical: a === b,
    fixtureBadge_after: (a.match(/<div class="tour-price">[^<]*<small>[^<]*<\/small><\/div>/) || [null])[0] };
}
for (const [tag, pps] of PAGES) {
  for (const [label, tours] of [['without', live], ['with', fixture(live)]]) {
    const b = await runActivity(beforeRef, tag, pps, tours), a = await runActivity(afterRef, tag, pps, tours);
    out.activity[`${tag}/${label}`] = { cards_before: count(b, /<article/g), cards_after: count(a, /<article/g),
      price_before: count(b, /tour-price/g), price_after: count(a, /tour-price/g), small_after: count(a, /<small>/g), identical: a === b,
      fixtureBadge_after: (a.match(/<div class="tour-price">[^<]*<small>[^<]*<\/small><\/div>/) || [null])[0] };
  }
}
console.log(JSON.stringify(out, null, 1));
