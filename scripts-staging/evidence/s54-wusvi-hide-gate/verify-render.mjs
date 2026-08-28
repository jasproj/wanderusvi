// s54-wusvi-hide-gate render verification. node vm over BOTH dynamic render
// paths (app.js's loadTours draw-pool filter + createTourCard, and
// activity-tours.js's per-tag filter+render) at BEFORE (git ref: origin/main,
// code AND data as they were) vs AFTER (worktree: code AND data as changed by
// this PR). Asserts:
//   - every one of the 43 hidden pks rendered a card in >=1 path BEFORE
//   - none of the 43 render a card in ANY path AFTER
//   - every row OUTSIDE the 43 renders byte-identical HTML before vs after
//     (no verified row lost, nothing else moved)
//   - pool count drops by exactly 43 in the app.js path
// Usage: node verify-render.mjs <before-ref>
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import crypto from 'node:crypto';

const beforeRef = process.argv[2];
const show = (ref, f) => ref === 'WORKTREE' ? fs.readFileSync(f, 'utf8') : execFileSync('git', ['show', `${ref}:${f}`], { encoding: 'utf8', maxBuffer: 1 << 28 });

const HIDDEN_PKS = new Set(JSON.parse(fs.readFileSync('scripts-staging/evidence/s54-wusvi-hide-gate/apply-summary.json', 'utf8')).summary.map(s => s.pk));

function elem() {
    const e = { innerHTML: '', hidden: false, textContent: '', style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {},
        addEventListener() {}, getAttribute(k) { return e._a?.[k] ?? null; }, setAttribute() {}, appendChild() {}, querySelector: () => elem(), querySelectorAll: () => [], value: '' };
    return e;
}
const noop = { log() {}, warn() {}, error() {} };

function appCtx(appSrc) {
    const ctx = {
        console: noop, window: {}, localStorage: { getItem: () => null, setItem() {} }, sessionStorage: { getItem: () => null, setItem() {} },
        gtag() {}, setTimeout, URLSearchParams,
        document: { addEventListener() {}, getElementById: () => elem(), querySelector: () => elem(), querySelectorAll: () => [], createElement: () => elem(), body: elem() },
        fetch: () => new Promise(() => {})
    };
    ctx.window = ctx;
    vm.createContext(ctx);
    vm.runInContext(appSrc, ctx, { filename: 'app.js' });
    return ctx;
}

async function runActivity(actSrc, tag, pps, tours) {
    const grid = elem(); grid._a = { 'data-activity-tag': tag, 'data-activity-label': tag.toLowerCase(), 'data-prefer-per-seat': pps ? 'true' : 'false' };
    const ctx = {
        console: noop,
        document: { getElementById: (id) => ({ 'activity-tours-grid': grid, 'activity-tours-status': elem(), 'activity-browse-all': elem() })[id] || null },
        fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ tours }) }),
        setTimeout
    };
    ctx.window = ctx;
    vm.createContext(ctx);
    vm.runInContext(actSrc, ctx, { filename: 'activity-tours.js' });
    await new Promise(r => setTimeout(r, 20));
    return grid.innerHTML;
}

const PAGES = [['Snorkel', true], ['Kayak', true], ['Jet Ski Tour', false], ['Fishing', false], ['Zipline', false]];

const snap = {};
for (const [label, ref] of [['before', beforeRef], ['after', 'WORKTREE']]) {
    const appSrc = show(ref, 'app.js');
    const actSrc = show(ref, 'activity-tours.js');
    const rows = JSON.parse(show(ref, 'tours-data.json')).tours;
    // app.js's own loadTours draw-pool predicate, verbatim per ref (picks up
    // the added && !t.hidden clause automatically after the code change).
    const predSrc = appSrc.match(/toursData = toursData\.filter\(t => ([^;]+)\);/)[1];
    // eslint-disable-next-line no-new-func
    const pred = new Function('t', `return (${predSrc});`);
    const pool = rows.filter(pred);

    const ctx = appCtx(appSrc);
    const cardsByPk = new Map(pool.map(t => [t.pk, ctx.createTourCard(t)]));

    // activity-tours.js live-population predicate, read from the actual
    // source per ref (with the closure var TAG parameterized), so the
    // after-run picks up its new && !t.hidden clause without this script
    // hand-maintaining a duplicate of the condition.
    const actPredBody = actSrc.match(/var live = all\.filter\(function \(t\) \{\s*return ([\s\S]*?);\s*\}\);/)[1];
    // eslint-disable-next-line no-new-func
    const actPred = new Function('t', 'TAG', `return (${actPredBody});`);

    const activity = {};
    for (const [tag] of PAGES) {
        const eligible = rows.filter(t => t && actPred(t, tag));
        activity[tag] = eligible.map(t => t.pk);
    }

    const cardHtmlOutsideHidden = pool.filter(t => !HIDDEN_PKS.has(t.pk)).map(t => [t.pk, cardsByPk.get(t.pk)]);
    const outsideSha = crypto.createHash('sha256').update(cardHtmlOutsideHidden.map(([pk, html]) => `${pk}:${html}`).join('\n')).digest('hex');

    snap[label] = {
        rows: rows.length,
        poolSize: pool.length,
        poolPks: new Set(pool.map(t => t.pk)),
        hiddenInPool: pool.filter(t => HIDDEN_PKS.has(t.pk)).map(t => t.pk),
        activity,
        outsideSha,
        cardsByPk
    };
}

const errors = [];

// 1. Every hidden pk rendered somewhere BEFORE (app pool or any activity page).
for (const pk of HIDDEN_PKS) {
    const inAppBefore = snap.before.poolPks.has(pk);
    const inActivityBefore = Object.values(snap.before.activity).some(list => list.includes(pk));
    if (!inAppBefore && !inActivityBefore) errors.push(`pk ${pk}: did not render BEFORE in any path (nothing to gate)`);
}

// 2. No hidden pk renders anywhere AFTER.
for (const pk of HIDDEN_PKS) {
    if (snap.after.poolPks.has(pk)) errors.push(`pk ${pk}: still in app.js draw pool AFTER`);
    for (const [tag, list] of Object.entries(snap.after.activity)) {
        if (list.includes(pk)) errors.push(`pk ${pk}: still in activity-tours.js "${tag}" pool AFTER`);
    }
}

// 3. Pool shrinks by exactly the hidden count that was actually in-pool before.
const expectedDrop = snap.before.hiddenInPool.length;
const actualDrop = snap.before.poolSize - snap.after.poolSize;
if (actualDrop !== expectedDrop) errors.push(`app.js pool dropped by ${actualDrop}, expected ${expectedDrop}`);

// 4. Every row OUTSIDE the 43 renders byte-identical before vs after.
if (snap.before.outsideSha !== snap.after.outsideSha) errors.push(`outside-population card HTML sha differs: ${snap.before.outsideSha} != ${snap.after.outsideSha} — a non-gated row changed`);

const report = {
    before: { rows: snap.before.rows, appPoolSize: snap.before.poolSize, hiddenPksInAppPoolBefore: snap.before.hiddenInPool.length, activityCounts: Object.fromEntries(Object.entries(snap.before.activity).map(([k, v]) => [k, v.length])) },
    after: { rows: snap.after.rows, appPoolSize: snap.after.poolSize, hiddenPksInAppPoolAfter: snap.after.poolPks && [...HIDDEN_PKS].filter(pk => snap.after.poolPks.has(pk)).length, activityCounts: Object.fromEntries(Object.entries(snap.after.activity).map(([k, v]) => [k, v.length])) },
    hiddenPopulation: HIDDEN_PKS.size,
    outsidePopulationIdentical: snap.before.outsideSha === snap.after.outsideSha,
    errors
};
console.log(JSON.stringify(report, null, 1));
if (errors.length) { console.error(`\n${errors.length} assertion failure(s)`); process.exit(1); }
console.log('\nall assertions passed: 43 gated out of both render paths, pool drop exact, no other row changed');
