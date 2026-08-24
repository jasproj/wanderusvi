#!/usr/bin/env bash
# Assert: nav uniformity across the converged set + claim-string hygiene.
#
# Converged set = every page with a .nav-desktop/.nav-mobile EXCEPT index.html
# (in-page anchors by design) and blog/* (own 3-link family, out of scope).
# about.html and blog.html are expected to differ from the base family by
# exactly one class="active" attribute on nav-desktop and are compared modulo
# that attribute.
#
# Exit 1 on any violation, 0 when clean.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_assert() {
    local root="$1"
    python3 - "$root" <<'PY'
import re, glob, hashlib, sys, os
root = sys.argv[1]
os.chdir(root)
pages = sorted(glob.glob('*.html') + glob.glob('blog/*.html') + glob.glob('partners/*.html'))
EXEMPT = {'index.html'}
fail = []

def norm(s):
    return re.sub(r'>\s+<', '><', re.sub(r'\s+', ' ', s)).strip()

for layer in ('nav-desktop', 'nav-mobile'):
    fams = {}
    for p in pages:
        if p in EXEMPT or p.startswith('blog/'):
            continue
        raw = open(p, encoding='utf-8', errors='replace').read()
        m = re.search(r'<nav class="%s"[^>]*>.*?</nav>' % layer, raw, re.S)
        if not m:
            continue
        # compare modulo the active attribute
        n = norm(m.group(0)).replace(' class="active"', '')
        fams.setdefault(hashlib.sha256(n.encode()).hexdigest()[:10], []).append(p)
    if len(fams) != 1:
        fail.append('%s: %d families (expected 1) -> %s'
                    % (layer, len(fams), {k: v for k, v in fams.items()}))
    else:
        print('  %s: 1 family across %d pages' % (layer, len(list(fams.values())[0])))

# active classes land where intended
for page, label in (('about.html', 'About'), ('blog.html', 'Blog')):
    raw = open(page, encoding='utf-8').read()
    m = re.search(r'<nav class="nav-desktop"[^>]*>.*?</nav>', raw, re.S)
    if not re.search(r'<a href="[^"]*"\s+class="active">%s</a>' % label, m.group(0)):
        fail.append('%s: nav-desktop missing active on %s' % (page, label))
    else:
        print('  %s: active on %s ok' % (page, label))

# related blocks identical across the three island pages
hs = {}
for p in ('st-thomas.html', 'st-john.html', 'st-croix.html'):
    raw = open(p, encoding='utf-8').read()
    b = re.search(r'<section class="related">.*?</section>', raw, re.S)
    hs[p] = hashlib.sha256(b.group(0).encode()).hexdigest()[:16] if b else 'MISSING'
if len(set(hs.values())) != 1:
    fail.append('related blocks differ: %s' % hs)
else:
    print('  related block: identical across 3 island pages (%s)' % list(hs.values())[0])

# banned claim strings anywhere in the tree
# '5,000' alone is too loose: private-charters-usvi.html quotes real charter
# fares of $15,000/$70,000. Match the claim, not the digits.
for needle in ('4 Islands', 'Join 5,000+', 'Hundreds', 'hundreds of US Virgin Islands tours'):
    hits = [p for p in pages if needle in open(p, encoding='utf-8', errors='replace').read()]
    if hits:
        fail.append('banned string %r present on: %s' % (needle, hits))
    else:
        print('  banned string %r: 0 occurrences' % needle)

# footer string uniform
FOOT = 'Your guide to US Virgin Islands tours.'
# 32, not 30: 30 pages carried the stale "hundreds of" wording, and two blog
# posts already shipped the corrected sentence at HEAD. Post-change the whole
# site is uniform on one footer string.
n = sum(1 for p in pages if FOOT in open(p, encoding='utf-8', errors='replace').read())
print('  footer string present on %d pages' % n)
if n != 32:
    fail.append('footer string on %d pages, expected 32' % n)

if fail:
    print('\nFAIL:')
    for f in fail:
        print('  - %s' % f)
    sys.exit(1)
print('\nUNIFORMITY OK')
PY
}

main() {
    local target="${1:-$REPO_ROOT}"
    echo "ASSERT nav+claims uniformity in: $target"
    run_assert "$target"
}

main "$@"
