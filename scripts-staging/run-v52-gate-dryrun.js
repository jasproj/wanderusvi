#!/usr/bin/env node
/**
 * v5.2 Cat-D dominant-gate dry-run.
 *
 * Reads tours-data.json, isolates priceConfidence === 'low' tours
 * (expected: 156), evaluates each through extract_price_v52, and
 * writes a structured pass/fail report. NO writes to tours-data.json
 * — this script is read-only against the master file.
 *
 * Page text source:
 *   - Cached samples in scripts-staging/v52-audit-samples.json (30
 *     tours; pricingExcerpt + headExcerpt already on disk).
 *   - Live re-fetch via Playwright for the remaining ~126 tours.
 *
 * Flag: --dry-run-v52-gate-only  (required; refuses to run otherwise)
 *
 * Output: scripts-staging/v52-gate-dryrun.md
 *         scripts-staging/v52-gate-dryrun-raw.json (per-tour records)
 */

const fs = require('fs');
const path = require('path');
const { extract_price_v52 } = require('./extract-price-v5.2');

const TOURS_FILE = 'tours-data.json';
const SAMPLES_FILE = 'scripts-staging/v52-audit-samples.json';
const REPORT_FILE = 'scripts-staging/v52-gate-dryrun.md';
const RAW_FILE = 'scripts-staging/v52-gate-dryrun-raw.json';

// Audit categories from scripts-staging/v52-audit-report.md §5.
const AUDIT_CATEGORY = {
  // B — tiered packages or value range
  '607195': 'B', '607221': 'B', '660757': 'B', '274477': 'B',
  // D — capture correct, lacks anchor verb
  '211096': 'D', '211088': 'D', '211022': 'D', '564306': 'D',
  '464992': 'D', '614944': 'D', '615132': 'D', '424739': 'D',
  '521254': 'D', '424388': 'D', '369332': 'D', '615474': 'D',
  '601987': 'D', '212044': 'D', '487206': 'D',
  // E — would-be FP (add-on / surcharge)
  '170659': 'E', '170656': 'E',
  // F — no public price
  '194421': 'F', '161648': 'F', '340838': 'F', '292330': 'F',
  '114303': 'F', '334293': 'F',
  // G — other shape issues
  '200902': 'G', '185836': 'G', '102397': 'G',
};

function ensureFlag() {
  if (!process.argv.includes('--dry-run-v52-gate-only')) {
    console.error('Refusing to run without --dry-run-v52-gate-only flag.');
    console.error('This script is read-only by contract; the flag forces explicit intent.');
    process.exit(2);
  }
}

function loadLowTours() {
  const data = JSON.parse(fs.readFileSync(TOURS_FILE, 'utf8'));
  const tours = data.tours || data;
  return tours.filter(t => t.priceConfidence === 'low');
}

function loadCachedSamples() {
  if (!fs.existsSync(SAMPLES_FILE)) return new Map();
  const arr = JSON.parse(fs.readFileSync(SAMPLES_FILE, 'utf8'));
  const map = new Map();
  for (const s of arr) {
    if (!s.error) {
      // Reconstruct best-effort full text from concatenated excerpts.
      // The audit fetcher captured pricingExcerpt (~1500 chars from
      // "Pricing" forward) and headExcerpt (first 600 chars). For the
      // gate's purposes — distinct $-values + ±40 char window — the
      // pricingExcerpt is the relevant region.
      const merged = [s.headExcerpt, s.pricingExcerpt]
        .filter(Boolean)
        .join(' ');
      map.set(String(s.id), merged);
    }
  }
  return map;
}

async function fetchPageText(browser, url) {
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  });
  const page = await ctx.newPage();
  try {
    await page.goto(url, { timeout: 30000, waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
    const text = await page.evaluate(() => document.body.innerText);
    return text.replace(/\s+/g, ' ');
  } finally {
    await page.close();
    await ctx.close();
  }
}

(async () => {
  ensureFlag();

  const lows = loadLowTours();
  console.log(`Low-confidence tours found: ${lows.length}`);
  if (lows.length !== 156) {
    console.warn(`Expected 156, got ${lows.length} — proceeding anyway.`);
  }

  const cached = loadCachedSamples();
  console.log(`Cached audit samples: ${cached.size}`);

  // Decide whether to fetch live for the rest.
  const needFetch = lows.filter(t => !cached.has(String(t.id)));
  console.log(`Tours needing live fetch: ${needFetch.length}`);

  let browser = null;
  if (needFetch.length > 0) {
    const { chromium } = require('playwright');
    browser = await chromium.launch({ headless: true });
  }

  const records = [];
  for (let i = 0; i < lows.length; i++) {
    const t = lows[i];
    const id = String(t.id);
    let pageText = cached.get(id);
    let source = 'cached';

    if (!pageText && browser) {
      try {
        pageText = await fetchPageText(browser, t.bookingLink);
        source = 'live';
      } catch (err) {
        records.push({
          id,
          name: t.name,
          capturedPrice: t.price,
          priceLabel: t.priceLabel,
          auditCategory: AUDIT_CATEGORY[id] || null,
          source: 'fetch-error',
          error: String(err).slice(0, 200),
          gate: { passed: false, criterionFailed: 'fetch-error' },
        });
        if ((i + 1) % 10 === 0) console.log(`  [${i+1}/${lows.length}] (errored)`);
        continue;
      }
    }

    if (!pageText) {
      records.push({
        id,
        name: t.name,
        capturedPrice: t.price,
        priceLabel: t.priceLabel,
        auditCategory: AUDIT_CATEGORY[id] || null,
        source: 'missing',
        gate: { passed: false, criterionFailed: 'no-page-text' },
      });
      continue;
    }

    // Run v5.2: re-runs v5.4 + applies gate if low.
    const result = extract_price_v52(pageText);
    records.push({
      id,
      name: t.name,
      capturedPrice: t.price,
      priceLabel: t.priceLabel,
      auditCategory: AUDIT_CATEGORY[id] || null,
      source,
      reExtractPrice: result.price,
      reExtractConfidence: result.priceConfidence,
      reExtractLabel: result.priceLabel,
      priceSource: result.priceSource || null,
      gate: result.gateResult || null,
    });

    if ((i + 1) % 10 === 0) console.log(`  [${i+1}/${lows.length}] processed`);
  }

  if (browser) await browser.close();

  fs.writeFileSync(RAW_FILE, JSON.stringify(records, null, 2));
  console.log(`✓ Raw records → ${RAW_FILE}`);

  // Summary
  const pass = records.filter(r => r.gate && r.gate.passed);
  const fail = records.filter(r => !(r.gate && r.gate.passed));
  console.log(`\nGate PASS: ${pass.length}`);
  console.log(`Gate FAIL: ${fail.length}`);

  // Audit cross-reference
  const auditChecks = Object.keys(AUDIT_CATEGORY);
  const violations = [];
  for (const id of auditChecks) {
    const cat = AUDIT_CATEGORY[id];
    const rec = records.find(r => r.id === id);
    if (!rec) continue;
    if (cat === 'E' && rec.gate && rec.gate.passed) {
      violations.push({ id, cat, rec });
    }
  }

  console.log(`\nCat E policy violations: ${violations.length}`);
  if (violations.length > 0) {
    console.log('==== ZERO-FP POLICY VIOLATION ====');
    for (const v of violations) {
      console.log(`  ${v.id} (${v.rec.name}): captured ${v.rec.capturedPrice}, gate PASSED`);
    }
  }

  // Build markdown report
  const lines = [];
  lines.push('# v5.2 Dominant-Price Gate — Dry-Run Report');
  lines.push('');
  lines.push(`**Generated:** ${new Date().toISOString()}`);
  lines.push(`**Branch:** \`feat/usvi-v52-dominant-gate\``);
  lines.push(`**Mode:** \`--dry-run-v52-gate-only\` (no writes to tours-data.json)`);
  lines.push('');
  lines.push('## 1. Inputs');
  lines.push('');
  lines.push(`- Low-confidence tours evaluated: **${lows.length}**`);
  lines.push(`- Page-text source: **${cached.size}** from cached audit samples + **${needFetch.length}** fresh Playwright fetches`);
  lines.push(`- Extractor: \`scripts-staging/extract-price-v5.2.js\` (v5.4 + Cat-D gate)`);
  lines.push('');
  lines.push('## 2. Gate criteria');
  lines.push('');
  lines.push('1. v5.4 captured a price (`price !== null`)');
  lines.push('2. Distinct `$N` values in page text ≤ **2**');
  lines.push('3. Captured price is one of those distinct values (literal match)');
  lines.push('4. No disqualifier token in ±40 char window: `deposit|fee|surcharge|tax|tip|gratuity|add-on|addon|child|kids|junior|senior|discount`');
  lines.push('');
  lines.push('## 3. Headline counts');
  lines.push('');
  lines.push(`- Gate **PASS** (would graduate low → medium): **${pass.length}**`);
  lines.push(`- Gate **FAIL** (would remain low): **${fail.length}**`);
  lines.push('');

  // FAIL histogram
  const failHist = {};
  for (const r of fail) {
    const k = r.gate ? String(r.gate.criterionFailed) : 'no-gate';
    failHist[k] = (failHist[k] || 0) + 1;
  }
  lines.push('### 3a. FAIL histogram by criterion');
  lines.push('');
  lines.push('| Criterion | Count | Meaning |');
  lines.push('|---|---:|---|');
  const labels = {
    '1': 'Crit 1 — no captured price (v5.4 returned null)',
    '2': 'Crit 2 — > 2 distinct $-values in page',
    '3': 'Crit 3 — captured price not literally present in page',
    '4': 'Crit 4 — disqualifier token in ±40 char window',
    'fetch-error': 'Fetch error (network / Playwright)',
    'no-page-text': 'No page text available',
    'no-gate': 'Gate did not run',
  };
  for (const k of Object.keys(failHist).sort()) {
    lines.push(`| ${k} | ${failHist[k]} | ${labels[k] || k} |`);
  }
  lines.push('');

  // Audit cross-reference
  lines.push('## 4. Audit cross-reference (sanity checks)');
  lines.push('');
  lines.push(`Cross-checking the 30 sampled tours from \`v52-audit-report.md\` against gate decisions.`);
  lines.push('');
  lines.push('| Audit ID | Cat | Expected | Gate decision | Crit failed | Notes |');
  lines.push('|---|---|---|---|---|---|');
  const expectedByCat = { B: 'FAIL', D: 'PASS (most)', E: 'FAIL (zero-FP)', F: 'FAIL', G: 'mixed' };
  for (const id of Object.keys(AUDIT_CATEGORY)) {
    const cat = AUDIT_CATEGORY[id];
    const rec = records.find(r => r.id === id);
    if (!rec) {
      lines.push(`| ${id} | ${cat} | ${expectedByCat[cat]} | — | — | not found in low set |`);
      continue;
    }
    const gateLabel = rec.gate && rec.gate.passed ? '**PASS**' : 'FAIL';
    const crit = rec.gate ? rec.gate.criterionFailed ?? '—' : '—';
    let note = '';
    if (cat === 'E' && rec.gate && rec.gate.passed) note = '⚠ **ZERO-FP VIOLATION**';
    if (cat === 'D' && !(rec.gate && rec.gate.passed)) note = `D blocked by crit ${crit}`;
    lines.push(`| ${id} | ${cat} | ${expectedByCat[cat]} | ${gateLabel} | ${crit} | ${note} |`);
  }
  lines.push('');
  lines.push(`**Cat E policy violations:** ${violations.length}` + (violations.length > 0 ? ' — see §6 below.' : ' — none.'));
  lines.push('');

  // Sample PASSes
  lines.push('## 5. Sample PASSes (first 5)');
  lines.push('');
  for (const r of pass.slice(0, 5)) {
    lines.push(`### ${r.id} — ${r.name}`);
    lines.push('');
    lines.push(`- captured price: **$${r.capturedPrice}**`);
    lines.push(`- distinct $-values: ${JSON.stringify(r.gate.distinctDollarValues)}`);
    lines.push(`- matched token: \`${r.gate.capturedMatchToken}\``);
    lines.push(`- ±40 char window:`);
    lines.push('');
    lines.push('  ```');
    lines.push('  ' + (r.gate.contextWindow || '').replace(/\s+/g, ' ').slice(0, 200));
    lines.push('  ```');
    lines.push('');
  }

  // Sample FAILs by criterion
  lines.push('## 5b. Sample FAILs (one per criterion, up to 5)');
  lines.push('');
  const seenCrit = new Set();
  for (const r of fail) {
    const c = r.gate ? String(r.gate.criterionFailed) : 'no-gate';
    if (seenCrit.has(c)) continue;
    seenCrit.add(c);
    if (seenCrit.size > 5) break;
    lines.push(`### ${r.id} — ${r.name}`);
    lines.push('');
    lines.push(`- criterion failed: **${c}** — ${labels[c] || c}`);
    lines.push(`- captured price: $${r.capturedPrice}`);
    if (r.gate) {
      lines.push(`- distinct $-values: ${JSON.stringify(r.gate.distinctDollarValues)}`);
      if (r.gate.disqualifierToken) lines.push(`- disqualifier hit: \`${r.gate.disqualifierToken}\``);
      if (r.gate.contextWindow) {
        lines.push(`- window:`);
        lines.push('');
        lines.push('  ```');
        lines.push('  ' + r.gate.contextWindow.slice(0, 200));
        lines.push('  ```');
      }
    }
    lines.push('');
  }

  // Violations detail (if any)
  if (violations.length > 0) {
    lines.push('## 6. ZERO-FP POLICY VIOLATIONS');
    lines.push('');
    lines.push('These tours were classified as Cat E ("would-be FP") in the audit but PASSED the v5.2 gate. Promoting them would violate v5.4\'s zero-false-positive contract.');
    lines.push('');
    for (const v of violations) {
      lines.push(`### ⚠ ${v.id} — ${v.rec.name}`);
      lines.push('');
      lines.push(`- captured price: **$${v.rec.capturedPrice}** (audited: add-on / surcharge, not a real per-tour price)`);
      lines.push(`- distinct $-values: ${JSON.stringify(v.rec.gate.distinctDollarValues)}`);
      lines.push(`- matched token: \`${v.rec.gate.capturedMatchToken}\``);
      lines.push(`- ±40 char window:`);
      lines.push('');
      lines.push('  ```');
      lines.push('  ' + (v.rec.gate.contextWindow || '').slice(0, 200));
      lines.push('  ```');
      lines.push('');
    }
    lines.push('### Required follow-up before any --live run');
    lines.push('');
    lines.push('Extend `DISQUALIFIER_TOKENS` (or change criterion 4 mechanism) to catch the patterns above. Candidate additions based on these two cases:');
    lines.push('');
    lines.push('- `additional`, `extra`, `option`, `optional`, `rental` (matches "Rental gear ... is +$20")');
    lines.push('- `+$` literal pattern (a `$N` immediately preceded by `+` is almost always an add-on)');
    lines.push('- `nitrox`, `certification` (domain-specific, scuba)');
    lines.push('');
    lines.push('Alternative: tighten criterion 2 to require **= 1** distinct $-value (sharper but narrower).');
    lines.push('');
  }

  fs.writeFileSync(REPORT_FILE, lines.join('\n'));
  console.log(`✓ Report → ${REPORT_FILE}`);
  console.log(`\nDry-run complete. Awaiting --live approval.`);
})();
