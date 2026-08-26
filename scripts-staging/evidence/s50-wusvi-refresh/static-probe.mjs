// s50 ruling-packet probe: live figures for the 6 static-card divergence rows OUTSIDE the refresh population
// (HOLD/ruled rows — read-only evidence, nothing is written to tours-data.json). Same endpoint/dates/rate as the batch.
import fs from 'node:fs';
const DATES = ['2026-09-05', '2026-09-19', '2026-10-03', '2026-10-24']; const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';
const PKS = [377266, 660734, 664103, 411764, 274478, 98818];
const rows = JSON.parse(fs.readFileSync('tours-data.json', 'utf8')).tours.filter(t => PKS.includes(t.pk));
const bySn = new Map(); for (const t of rows) { const sn = t.bookingUrl.match(/\/book\/([^/]+)\//)[1]; bySn.set(sn, (bySn.get(sn) || []).concat(t.pk)); }
const out = { dates: DATES, requests: 0, perPk: {} }; for (const pk of PKS) out.perPk[pk] = { probes: [] };
for (const [sn, pks] of bySn) for (const date of DATES) {
  out.requests++; let j = null, err = null;
  try { const r = await fetch(`https://fareharbor.com/api/embed/${sn}/price-preview/per-item/v2/?item_pks=${pks.join(',')}&include_breakdown=yes&date=${date}`, { headers: { 'User-Agent': UA, Accept: 'application/json' } }); if (r.status !== 200) err = 'HTTP ' + r.status; else j = await r.json(); } catch (e) { err = String(e.message); }
  await new Promise(r => setTimeout(r, 1000));
  const items = new Map(((j && j.items) || []).map(it => [Number(it.id), it]));
  for (const pk of pks) { const it = items.get(pk); const p = { date, error: err, absent: !err && !it };
    if (it) { p.start_at = it.availability?.start_at || null; p.tiers = (it.price?.breakdown?.customer_types || []).map(c => ({ singular: c.singular, note: c.note, priceCents: c.price })); p.currency = j.details?.currency; }
    out.perPk[pk].probes.push(p); }
}
fs.writeFileSync('scripts-staging/evidence/s50-wusvi-refresh/static-probe.json', JSON.stringify(out, null, 1)); console.log('done', out.requests);
