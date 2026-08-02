# Image Attribution — wanderusvi

**This is the single attribution record for this repo.** `app.js` names it as such.
If a second one ever appears, that duplication is itself the defect — reconcile
before trusting either.

Each entry records what the source says, **what the image actually depicts**, and
**where it is referenced live**. Those three drift apart silently; the "Depicts"
line is the one to read before reusing a file.

Hero photos sourced from [Pexels](https://www.pexels.com) on 2026-04-24 under the
[Pexels License](https://www.pexels.com/license/).

---

## hero-photo-1.jpg — St Thomas harbour
- Photographer: [Arian Fernandez](https://www.pexels.com/@troopper84)
- Photo URL: https://www.pexels.com/photo/scenic-view-of-st-thomas-harbor-in-summer-34650321/
- Original dimensions: 11200×6300 · Final: 1920×1080 · Downloaded: 2026-04-24
- **Depicts:** hillside harbour town seen from the water, container terminal and a
  moored cargo ship in the left foreground. Consistent with the source claim.
- **Source slug vs depiction: MATCH.**
- **Live in:** `index.html` (St Thomas island card, and a `<img>` lower on the page),
  `app.js` (`FALLBACK_IMAGE` for every catalogue record with no image),
  `st-croix.html`, `snorkeling.html`, `fishing.html`, `jet-ski.html`, `kayak.html`,
  `blog/best-shore-excursions-st-thomas-cruise-ship.html`,
  `blog/best-snorkeling-tours-st-john-for-beginners.html`, `blog/index.html`.
- ⚠️ Because it is the global fallback it appears in many contexts. Any alt text
  claiming a different island is wrong — see the open items below.

## hero-photo-2.jpg — beach seen from inside a parked vehicle
- Photographer: [livin](https://www.pexels.com/@livin)
- Photo URL: https://www.pexels.com/photo/vehicle-interior-close-up-photography-2794001/
- Original dimensions: 6240×4160 · Final: 1920×1280 · Downloaded: 2026-04-24
- **Depicts:** the interior of a parked Jeep — dashboard, steering wheel with a
  visible Jeep roundel, rear-view mirror — framing a turquoise bay and white-sand
  beach through the windscreen. The beach occupies roughly the upper-right third
  of the frame; the vehicle interior is the dominant subject.
- **Source slug vs depiction: MATCH** (the slug describes the composition).
- **Previously recorded here as** "St John beach Virgin Islands", which described
  only the background and omitted the vehicle. Not a wrong-territory error — the
  two descriptions were describing different parts of the same frame — but the
  omission is why the file reads as a plain beach photo in any listing.
- **Beach identity NOT independently verified.** Visually consistent with Trunk Bay,
  St John, but the Pexels page asserts no location. Do not caption it as a named
  beach without confirming.
- **Live in:** `index.html` — St John island card background.

## hero-photo-3.jpg — chartered catamaran, Curaçao
- Photographer: [Wijs (Wise)](https://www.pexels.com/@wijs-wise-136435282)
- Photo URL: https://www.pexels.com/photo/catamaran-sailing-in-the-turquoise-waters-of-curacao-32330651/
- Original dimensions: 6000×4000 · Final: 1920×1280 · Downloaded: 2026-04-24
- **Depicts:** a white catamaran at anchor carrying passengers. The hull is printed
  **"BlueFinn Charters"** and **"www.bluefinncharters.com"** in large type, legible
  at full size. BlueFinn is a Curaçao operator.
- **Source slug vs depiction: MATCH** — the slug says Curaçao.
- ⚠️ **Previously recorded here as "Caribbean sailing catamaran", which dropped the
  country.** That omission is the whole defect: the file reads as generic Caribbean
  stock while the source explicitly says Curaçao.
- 🔴 **OPEN — not resolved in this PR, awaiting a ruling.** This file is live as the
  **St Croix island card on `index.html`**, i.e. a Curaçao vessel representing a USVI
  island on the homepage, carrying a named third-party operator's branding and URL.
- **Live in:** `index.html` — St Croix island card background.

---

## Undocumented — provenance not recorded at the time of addition

These are referenced by live pages but were never entered here. Source, licence and
photographer are **unknown**; nothing below is a licence claim. Do not treat absence
of a warning as clearance.

## about-mission.jpg
- **Provenance: UNRECORDED.** Added 2026-05-19 in `3c1b1cf`
  ("fix(about): localize body copy from Hawaii to US Virgin Islands"). Because that
  commit was a Hawaii→USVI conversion, the image's territory should be confirmed
  before reuse.
- **Depicts:** a calm bay with a curved white-sand beach, forested hillside behind,
  picnic tables and beachgoers under trees at the right. Caribbean in character.
- **Location NOT verified.** `about.html` captions it "Francis Bay, St. John — US
  Virgin Islands National Park". That claim is unsourced here.
- **Live in:** `about.html`.

## og-image.jpg
- **Provenance: UNRECORDED.** Added 2026-04-24 in `8f0cbe3`
  ("Add branded OG image and update og:image meta tags across site").
- **Depicts:** a composed brand card — "Wander US Virgin Islands / St. Thomas.
  St. John. St. Croix." set over an illustrated bay with moored sailboats, hibiscus
  and frangipani. Rendered/illustrated artwork, not a photograph of a real location.
- **Live in:** `index.html`, `snorkeling.html`, `whale-watching.html`,
  `advertise.html` (all as `og:image`), and
  `blog/best-shore-excursions-st-thomas-cruise-ship.html` uses hero-photo-1 instead.

## hero-banner.png / hero-banner.webp / footer-badge*.png|webp / logo*.png|webp / favicon*
- **Provenance: UNRECORDED.** Brand/logo assets, added 2026-04-24 and 2026-05-02.
- Presumed first-party WanderUSVI artwork. Not verified here.
- **Live in:** `index.html` (`hero-banner.webp`); badge/logo/favicon assets sitewide.

---

## Open items — recorded, not resolved in this PR

1. 🔴 **hero-photo-3.jpg is a Curaçao vessel in the St Croix homepage slot**, with a
   third-party operator's name and URL visible on the hull. Awaiting a ruling.
2. **Wrong-island alt text on hero-photo-1.jpg.** `index.html` and
   `blog/best-snorkeling-tours-st-john-for-beginners.html` both caption it
   "St Thomas harbour in summer" — correct for the file, wrong for a St John page.
   The same file is the global `FALLBACK_IMAGE`, so every catalogue record lacking
   an image renders a St Thomas harbour photo under its own name as alt.
3. **`about-mission.jpg` is captioned "Francis Bay, St. John" on `about.html`** with
   no recorded source. Verify or soften.
4. **JSON-LD `publisher.logo.url` is `https://wanderusvi.com/og-image.png` — a 404.**
   Present in the structured data of every blog post. The real asset is
   `images/og-image.jpg`; no `og-image.png` exists at the repo root.

## Rule

Local assets only. Do not hotlink a third-party host for page imagery — six
Wikimedia URLs were removed on 2026-08-02, five of which had never existed on
Commons at all. If no honest local match exists, ship the card as text.
