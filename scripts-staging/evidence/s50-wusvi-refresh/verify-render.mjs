// s50 PR-B render verification: node vm over BOTH dynamic render paths (app.js createTourCard, activity-tours.js strip)
// at a fixed renderer (HEAD) with tours-data.json BEFORE (git ref) vs AFTER (worktree). Decomposes every price element
// by gate branch and counts priceUnit badges. Usage: node verify-render.mjs <before-data-ref>
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
const beforeRef = process.argv[2];
const show = (ref, f) => ref === 'WORKTREE' ? fs.readFileSync(f, 'utf8') : execFileSync('git', ['show', `${ref}:${f}`], { encoding: 'utf8', maxBuffer: 1 << 28 });
const APP = fs.readFileSync('app.js', 'utf8'), ACT = fs.readFileSync('activity-tours.js', 'utf8');
const POP = new Set(JSON.parse(fs.readFileSync('scripts-staging/evidence/s50-wusvi-refresh/population.json', 'utf8')).pks);
function elem() { const e = { innerHTML: '', hidden: false, textContent: '', style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {},
  addEventListener() {}, getAttribute(k) { return e._a?.[k] ?? null; }, setAttribute() {}, appendChild() {}, querySelector: () => elem(), querySelectorAll: () => [], value: '' }; return e; }
const noop = { log() {}, warn() {}, error() {} };
function appCtx() { const ctx = { console: noop, window: {}, localStorage: { getItem: () => null, setItem() {} }, sessionStorage: { getItem: () => null, setItem() {} }, gtag() {}, setTimeout() {}, URLSearchParams,
  document: { addEventListener() {}, getElementById: () => elem(), querySelector: () => elem(), querySelectorAll: () => [], createElement: () => elem(), body: elem() }, fetch: () => new Promise(() => {}) };
  ctx.window = ctx; vm.createContext(ctx); vm.runInContext(APP, ctx, { filename: 'app.js' }); return ctx; }
async function runActivity(tag, pps, tours) {
  const grid = elem(); grid._a = { 'data-activity-tag': tag, 'data-activity-label': tag.toLowerCase(), 'data-prefer-per-seat': pps ? 'true' : 'false' };
  const ctx = { console: noop, document: { getElementById: (id) => ({ 'activity-tours-grid': grid, 'activity-tours-status': elem(), 'activity-browse-all': elem() })[id] || null },
    fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ tours }) }), setTimeout };
  ctx.window = ctx; vm.createContext(ctx); vm.runInContext(ACT, ctx, { filename: 'activity-tours.js' });
  await new Promise(r => setTimeout(r, 20)); return grid.innerHTML;
}
function decompose(html) {
  const m = html.match(/<div class="tour-price">[^<]*(?:<small>[^<]*<\/small>)?<\/div>/g) || [];
  const d = { priceElements: m.length, privateBoat: 0, perAdult: 0, priceOnRequest: 0, checkAvailability: 0, withUnit: 0 };
  for (const x of m) { if (x.includes('· private boat')) d.privateBoat++; else if (x.includes(' per adult')) d.perAdult++; else if (x.includes('Price on request')) d.priceOnRequest++; else if (x.includes('Check availability')) d.checkAvailability++; if (x.includes('<small>')) d.withUnit++; }
  d.offers = (html.match(/"@type":"Offer","price":/g) || []).length;
  return d;
}
const PAGES = [['Snorkel', true], ['Kayak', true], ['Jet Ski Tour', false], ['Fishing', false], ['Zipline', false]];
const out = {};
for (const [label, ref] of [['before', beforeRef], ['after', 'WORKTREE']]) {
  const rows = JSON.parse(show(ref, 'tours-data.json')).tours;
  const live = rows.filter(t => t.status !== 'inactive' && !t.bookingDead);
  const ctx = appCtx();
  const cards = live.map(t => [t, ctx.createTourCard(t)]);
  const all = decompose(cards.map(c => c[1]).join('\n'));
  const inPop = decompose(cards.filter(c => POP.has(c[0].pk)).map(c => c[1]).join('\n'));
  const outPop = cards.filter(c => !POP.has(c[0].pk)).map(c => c[1]).join('\n');
  out[label] = { rows: rows.length, live: live.length, cards: cards.length, app_all: all, app_population: inPop, app_outsidePopulationSha: (await import('node:crypto')).createHash('sha256').update(outPop).digest('hex').slice(0, 16), activity: {} };
  for (const [tag, pps] of PAGES) { const h = await runActivity(tag, pps, live); out[label].activity[tag] = { cards: (h.match(/<article/g) || []).length, ...decompose(h) }; }
}
out.outsidePopulationIdentical = out.before.app_outsidePopulationSha === out.after.app_outsidePopulationSha;
console.log(JSON.stringify(out, null, 1));
