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

## hero-photo-2.jpg — Jeep interior framing a bay through the windscreen
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
- 🚫 **RETIRED FROM ALL PAGES 2026-08-02. Do not reuse anywhere on this site.**
  Two independent reasons, either sufficient:
  1. **Wrong territory.** It was live as the **St Croix island card on `index.html`** —
     a Curaçao vessel representing a USVI island on the homepage.
  2. **Third-party brand.** "BlueFinn Charters" and their URL are printed large on the
     hull. That is an unaffiliated operator's advertising, in an island slot, on a site
     whose whole proposition is USVI operators.
- **Live in:** nothing. The St Croix card now ships with **no image** — no local asset
  genuinely depicts St Croix, and a near-match is a worse defect than no image.
- The file is retained, not deleted, so this record stays checkable.

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
- **Live in: 19 files** as of 2026-08-02 — every page's `og:image` / `twitter:image`,
  plus JSON-LD `publisher.logo.url` on the 7 blog posts (see open item 4). It became
  the site's single social-preview and publisher-logo asset when the 404
  `og-image.png` references were repointed here.
- ⚠️ It is a **wide brand card with baked-in text**, not a logo and not a photograph.
  It works as `og:image`; as `publisher.logo.url` it is serviceable but `logo.png`
  would be the more correct asset if anyone wants to split the two later.

## hero-banner.png / hero-banner.webp / footer-badge*.png|webp / logo*.png|webp / favicon*
- **Provenance: UNRECORDED.** Brand/logo assets, added 2026-04-24 and 2026-05-02.
- Presumed first-party WanderUSVI artwork. Not verified here.
- **Live in:** `index.html` (`hero-banner.webp`); badge/logo/favicon assets sitewide.

---

## Item log — ✅ resolved, or still open

1. ✅ **RESOLVED 2026-08-02** — hero-photo-3.jpg (Curaçao, BlueFinn-branded) removed
   from the St Croix homepage card. The card now ships with no image; no local asset
   depicts St Croix. The file is retired, not deleted.
2. **`hero-photo-1.jpg` is the global `FALLBACK_IMAGE` — 66 catalogue records have no
   image of their own and therefore render a St Thomas harbour photo**, whichever
   island the record belongs to, with the tour name as alt. Alt text on the two pages
   that reference the file directly was corrected on 2026-08-02; **the fallback itself
   is unchanged and remains a live wrong-island risk.** Not addressed in that PR.
3. **`about-mission.jpg` is captioned "Francis Bay, St. John" on `about.html`** with
   no recorded source. Verify or soften.
4. ✅ **RESOLVED 2026-08-02** — `https://wanderusvi.com/og-image.png` (404, no such
   file) replaced with `images/og-image.jpg` in all **27** references: 12 `og:image`,
   8 `twitter:image`, and 7 blog posts as JSON-LD `publisher.logo.url`.
   Corrected 2026-08-03 — this entry previously read "23 references … 8 pages as
   `og:image` + `twitter:image`", which assumed every page carried both tags.
   **It does not.** `og:image` appears on **12** pages but only **8** carry a
   matching `twitter:image`. The four unpaired pages — `advertise.html`,
   `index.html`, `snorkeling.html`, `whale-watching.html` — have `og:image`
   with no `twitter:image`. Not addressed here; recorded so the count is not
   re-derived from the wrong assumption.
   These 27 are the references **repointed off `og-image.png` on 2026-08-02**, not
   a running total. A later PR added `og:image` + `twitter:image` to
   `blog/best-time-to-visit-usvi.html` as net-new tags, so grepping the tree today
   measures 13 / 9 / 7 = 29. That is not a contradiction of this entry.

## Rule

Local assets only. Do not hotlink a third-party host for page imagery — six
Wikimedia URLs were removed on 2026-08-02, five of which had never existed on
Commons at all. If no honest local match exists, ship the card as text.

## Blog card images (added 2026-09-02, s55)

All from Pexels (free license, attribution not required but recorded):

- `images/blog/best-diving-usvi.jpg` — Pexels photo 31717403 by Thomas Judge — https://www.pexels.com/photo/31717403/
- `images/blog/things-to-do-st-croix.jpg` — Pexels photo 31376012 by Jesus Rivera Rosa — https://www.pexels.com/photo/31376012/
- `images/blog/hiking-st-john-virgin-islands.jpg` — Pexels photo 39313566 by Karen Susi — https://www.pexels.com/photo/39313566/
- `images/blog/things-to-do-st-john.jpg` — Pexels photo 15163667 by Matt Barnard — https://www.pexels.com/photo/15163667/
- `images/blog/best-beaches-usvi.jpg` — Pexels photo 7052741 by Richard Issa Bockari — https://www.pexels.com/photo/7052741/
- `images/blog/things-to-do-st-thomas.jpg` — Pexels photo 34650333 by Arian Fernandez — https://www.pexels.com/photo/34650333/
- `images/blog/kayak-paddleboard-usvi-beginners.jpg` — Pexels photo 35875761 by Gilbert Castaño B — https://www.pexels.com/photo/35875761/
- `images/blog/best-time-to-visit-usvi.jpg` — Pexels photo 11807182 by Katie Cerami — https://www.pexels.com/photo/11807182/
- `images/blog/st-thomas-vs-st-john-vs-st-croix.jpg` — Pexels photo 7054604 by Joe Kritz — https://www.pexels.com/photo/7054604/
- `images/blog/top-snorkeling-usvi.jpg` — Pexels photo 38787825 by Samson Bush — https://www.pexels.com/photo/38787825/
- `images/blog/usvi-night-activities-guide.jpg` — Pexels photo 4316233 by Steshka Croes — https://www.pexels.com/photo/4316233/
- `images/blog/best-shore-excursions-st-thomas-cruise-ship.jpg` — Pexels photo 15305866 by Diego F. Parra — https://www.pexels.com/photo/15305866/
- `images/blog/best-snorkeling-tours-st-john-for-beginners.jpg` — Pexels photo 36132584 by Zack Gilbert — https://www.pexels.com/photo/36132584/
- `images/blog/best-snorkeling-tours-st-thomas-for-beginners.jpg` — Pexels photo 35010455 by Gavin Fregona — https://www.pexels.com/photo/35010455/
- `images/blog/kayak-and-snorkel-with-sea-turtles-st-john-usvi.jpg` — Pexels photo 28800349 by Markos Torpillas — https://www.pexels.com/photo/28800349/
