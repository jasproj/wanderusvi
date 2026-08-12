// Live activity tours strip.
//
// Renders the top N distinct bookable tours for one activity tag, from the same
// catalogue index.html reads. Shipped first inline on snorkeling.html (PR #86);
// extracted here so the four activity pages that use it cannot drift apart —
// the dedupe below in particular has to behave identically on all of them.
//
// Configuration comes from the grid element's data attributes:
//   <div class="activity-tours" id="activity-tours-grid"
//        data-activity-tag="Kayak" data-activity-label="kayaking" hidden></div>
//   <p  class="activity-tours-status" id="activity-tours-status">…</p>
//   <a  id="activity-browse-all" href="index.html?activity=Kayak#tours-section">…</a>
(function () {
    var TOP_N = 3;

    var grid = document.getElementById('activity-tours-grid');
    var status = document.getElementById('activity-tours-status');
    var browse = document.getElementById('activity-browse-all');
    if (!grid || !status || !browse) return;

    var TAG = grid.getAttribute('data-activity-tag');
    var LABEL = grid.getAttribute('data-activity-label') || (TAG || '').toLowerCase();
    var PREFER_PER_SEAT = grid.getAttribute('data-prefer-per-seat') === 'true';
    if (!TAG) return;

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // Mirrors app.js formatPrice: a price is shown only where the extractor was
    // confident AND the catalogue confirms it's a per-adult rate, not a whole-
    // charter figure. Anything else gets the island-page "Check availability"
    // label rather than an invented number.
    function priceLabel(t) {
        var ok = t.priceLabel === 'per adult' && (t.priceConfidence === 'high' || t.priceConfidence === 'medium');
        if (ok && typeof t.price === 'number' && isFinite(t.price) && t.price > 0) {
            return 'From $' + t.price;
        }
        return 'Check availability';
    }

    function truncate(s, n) {
        s = String(s == null ? '' : s).replace(/\s+/g, ' ').trim();
        return s.length > n ? s.slice(0, n - 1) + '…' : s;
    }

    // ---- distinct-product dedupe -------------------------------------------
    //
    // The catalogue carries the same underlying trip resold by several
    // operators, with names differing only in filler. Two live examples:
    //
    //   "Turtle Cove Catamaran Snorkel & Sail Adventure at Little Buck Island
    //    St. Thomas"                                              (The VI Cat)
    //   "Turtle Cove Catamaran Snorkel & Sail Adventure to Little Buck Island"
    //                                              (St. Thomas Water Sports)
    //
    //   "Glow Boats LED Night Kayak from The Marriott Frenchman's Cove, USVI"
    //   "Glow Boats LED Night Kayak from The Marriott's Frenchman's Cove, USVI"
    //
    // Ranking by qualityScore alone put both halves of a pair in the top 3,
    // which reads as a broken listing. Normalising the name to a token set and
    // comparing with Jaccard collapses those while leaving genuinely different
    // products from one operator (Top Shot's "Half Day" / "Full Day" /
    // "3/4 Day Charter" score 0.5 against each other) separate.

    // Filler that varies between resellers of the same trip. Duration and size
    // words are deliberately NOT in this list — "half day" vs "full day" is a
    // real product difference and must survive normalisation.
    var STOPWORDS = {
        at: 1, to: 1, the: 1, from: 1, with: 1, and: 1, a: 1, an: 1, of: 1,
        in: 1, on: 1, for: 1, or: 1, by: 1,
        usvi: 1, vi: 1, st: 1, saint: 1, thomas: 1, john: 1, croix: 1,
        island: 1, islands: 1, tour: 1, tours: 1
    };

    function signature(name) {
        return String(name || '')
            .toLowerCase()
            .replace(/&/g, ' and ')
            .replace(/'s\b/g, '')        // Marriott's -> Marriott, Frenchman's -> Frenchman
            .replace(/[^a-z0-9]+/g, ' ')
            .trim()
            .split(' ')
            .filter(function (w) { return w && !STOPWORDS[w]; });
    }

    function jaccard(a, b) {
        if (!a.length || !b.length) return 0;
        var setA = {}, i, inter = 0, union = 0, seen = {};
        for (i = 0; i < a.length; i++) setA[a[i]] = 1;
        var setB = {};
        for (i = 0; i < b.length; i++) setB[b[i]] = 1;
        for (var k in setA) { seen[k] = 1; if (setB[k]) inter++; }
        for (var k2 in setB) seen[k2] = 1;
        for (var k3 in seen) union++;
        return union ? inter / union : 0;
    }

    // Same underlying product? Short names are matched strictly (exact token
    // set) because Jaccard is unreliable on 1-2 significant tokens.
    function sameProduct(a, b) {
        var sa = a._sig, sb = b._sig;
        if (sa.length < 3 || sb.length < 3) {
            return sa.length === sb.length && sa.join(' ') === sb.join(' ');
        }
        return jaccard(sa, sb) >= 0.6;
    }

    // Greedy pick over the quality-sorted list. Pass 1 requires both a distinct
    // product AND a distinct operator, so the strip does not become three
    // listings from one company. If that cannot fill TOP_N, pass 2 relaxes the
    // operator constraint but still refuses duplicate products.
    function pickDistinct(sorted, n, tiers) {
        var picked = [], usedCompanies = {};

        function conflicts(cand) {
            for (var i = 0; i < picked.length; i++) {
                if (sameProduct(picked[i], cand)) return true;
            }
            return false;
        }

        // sweep(list, preferDistinctOperator): take from `list` in order,
        // skipping duplicate products always, and duplicate operators only on
        // the operator-preferring sweep.
        function sweep(list, preferDistinctOperator) {
            for (var i = 0; i < list.length && picked.length < n; i++) {
                var c = list[i];
                if (picked.indexOf(c) !== -1) continue;
                var co = (c.company || '').trim().toLowerCase();
                if (preferDistinctOperator && co && usedCompanies[co]) continue;
                if (conflicts(c)) continue;
                picked.push(c);
                if (co) usedCompanies[co] = 1;
            }
        }

        // Without tiers this is the original two-pass behaviour: prefer a
        // distinct operator, then relax that to fill the slots.
        var groups = tiers && tiers.length ? tiers : [sorted];
        var g;
        for (g = 0; g < groups.length; g++) sweep(groups[g], true);
        for (g = 0; g < groups.length; g++) sweep(groups[g], false);
        return picked;
    }

    // Per-seat curation guard.
    //
    // Ranking purely by qualityScore surfaced whole-boat products inside
    // per-seat activity strips: snorkeling's third card was an ~$1,800
    // "Full Day (6 or 8 hours) Private Charter - Luxury Sailing Catamaran"
    // sitting beside two ~$100 per-person trips. That is a real, bookable
    // product — it is just not comparable merchandising.
    //
    // Opt in per page with data-prefer-per-seat="true". Charter-shaped
    // products are demoted to a second tier, so they appear only when there
    // are fewer than TOP_N distinct non-charter products to show. Nothing is
    // filtered out, and the distinct-product / distinct-operator rules apply
    // across both tiers exactly as before.
    //
    // Matched on the NAME only, never the company: "Kaos, 3/4 Day Fishing"
    // from Drift Charters is a per-seat product whose *operator* happens to be
    // called Charters. Matching company would have wrongly demoted it.
    //
    // Deliberately NOT enabled on fishing.html (4 of its 6 live records are
    // charter-shaped, because whole-boat IS the fishing product) or on
    // zipline.html (a single live record).
    var CHARTER_SHAPED = /private|charter|whole\s*boat|luxury/i;
    // ------------------------------------------------------------------------

    // Root-absolute: these pages sit at the site root today, but a relative path
    // would break the moment one moved into a subdirectory.
    fetch('/tours-data.json', { cache: 'no-cache' })
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(function (raw) {
            var all = Array.isArray(raw) ? raw : (raw && raw.tours) || [];

            // Two-signal liveness, same as app.js: status active AND not
            // bookingDead. A bookingUrl is required too — a card that cannot be
            // booked is not worth rendering.
            var live = all.filter(function (t) {
                return t
                    && t.status !== 'inactive'
                    && !t.bookingDead
                    && t.bookingUrl
                    && Array.isArray(t.tags)
                    && t.tags.indexOf(TAG) !== -1;
            });

            var total = live.length;

            var sorted = live.slice().sort(function (a, b) {
                return (b.qualityScore || 0) - (a.qualityScore || 0);
            });
            sorted.forEach(function (t) { t._sig = signature(t.name); });

            var tiers = null;
            if (PREFER_PER_SEAT) {
                var perSeat = [], charterish = [];
                sorted.forEach(function (t) {
                    (CHARTER_SHAPED.test(t.name || '') ? charterish : perSeat).push(t);
                });
                tiers = [perSeat, charterish];
            }

            var top = pickDistinct(sorted, TOP_N, tiers);

            if (!top.length) {
                status.textContent = 'Tours are loading slowly right now — browse the full list below.';
                console.warn('[activity-tours] no bookable ' + TAG + ' records found');
                return;
            }

            var collapsed = Math.min(total, TOP_N) - top.length;
            if (top.length < TOP_N) {
                console.warn('[activity-tours] only ' + top.length + ' distinct bookable ' +
                             TAG + ' product(s) available, expected ' + TOP_N +
                             ' (from ' + total + ' live record(s))');
            }
            if (collapsed > 0) {
                console.log('[activity-tours] dedupe collapsed ' + collapsed +
                            ' near-identical ' + TAG + ' product(s)');
            }
            if (PREFER_PER_SEAT) {
                var shown = top.filter(function (t) { return CHARTER_SHAPED.test(t.name || ''); }).length;
                console.log('[activity-tours] per-seat preference on: ' + tiers[1].length +
                            ' of ' + total + ' live ' + TAG + ' record(s) are charter-shaped, ' +
                            shown + ' in the top ' + TOP_N);
            }

            grid.innerHTML = top.map(function (t) {
                var name = esc(t.name || (TAG + ' tour'));
                // t.bookingUrl is emitted verbatim: it carries the asn=fhdn /
                // asn-ref / ref affiliate attribution and the real FareHarbor
                // item pk. Rewriting it would break payout.
                return '' +
                    '<article class="tour-card">' +
                        '<div class="tour-image">' +
                            '<img src="' + esc(t.image || '/images/hero-photo-1.jpg') + '" ' +
                                 'alt="' + name + '" loading="lazy" width="400" height="200" ' +
                                 'onerror="this.src=\'/images/hero-photo-1.jpg\'">' +
                            '<div class="tour-price">' + esc(priceLabel(t)) + '</div>' +
                        '</div>' +
                        '<div class="tour-content">' +
                            '<div class="tour-company">' + esc(t.company || '') + '</div>' +
                            '<h3 class="tour-title">' + name + '</h3>' +
                            '<p class="tour-desc">' + esc(truncate(t.description, 120)) + '</p>' +
                            '<a href="' + esc(t.bookingUrl) + '" target="_blank" rel="noopener noreferrer" ' +
                               'class="tour-book-btn book-now-btn" ' +
                               'data-tour-id="' + esc(t.id) + '" ' +
                               'data-tour-name="' + name + '">Check Availability →</a>' +
                        '</div>' +
                    '</article>';
            }).join('');

            grid.hidden = false;
            status.hidden = true;
            // Zipline has exactly one live record, so "1 zipline tours" is a
            // label this actually renders — not a hypothetical.
            browse.textContent = 'Browse ' + (total === 1 ? 'the ' : 'all ') + total + ' ' +
                                 LABEL + (total === 1 ? ' tour' : ' tours') + ' →';
            console.log('[activity-tours] rendered ' + top.length + ' distinct of ' +
                        total + ' live ' + TAG + ' tours');
        })
        .catch(function (err) {
            // Editorial content below is unaffected; only the live strip degrades.
            status.textContent = 'Tours are loading slowly right now — browse the full list below.';
            console.error('[activity-tours] load failed:', err && err.message);
        });
})();
