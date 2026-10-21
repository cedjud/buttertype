# BT Smör — typeface presentation website: hand-off

Build the production website for **BT Smör**, a variable typeface made for Norway. This document is the brief. Read it fully, then read `CLAUDE.md`.

---

## 1. What you are building

A foundry-style typeface presentation site (structural reference: off-type.com — ruled rows, metadata columns beside giant specimen lines, hairline dividers, stark colour, no cards).

The typeface is the star and it is **interactive**: three variable axes let the letters melt from razor-sharp to a puddle. The site must show that off with live controls and scroll-linked effects.

**Source of truth**
| For… | Use… |
|---|---|
| Visual design, layout, spacing, copy | `design/artboards/*.dc.html` (28 artboards — see §6) |
| Colours, type, grid, axis values | `tokens/tokens.json` and `tokens/tokens.css` |
| Font files and their behaviour | `fonts/` + §3 below |
| Scroll-linked / interactive behaviour | `reference/prototype/site.template.html` (**behaviour only — its visual style is outdated, see §7**) |
| Changing the font itself | `font-source/` |

**Status:** the artboards were authored as design markup and have **not been rendered or pixel-checked** (the tool used discourages it). Treat measurements as intent. Use your own screenshots to verify the build against the artboard values.

---

## 2. Package contents

```
HANDOFF.md                    this file
CLAUDE.md                     short working rules for the repo
tokens/tokens.json            colours, type scale, axes, breakpoints
tokens/tokens.css             @font-face, @property axis registration, .bt/.label/.rule helpers
fonts/BTSmor.woff2            644 KB — use this on the web
fonts/BTSmor-Variable.ttf     1.5 MB — master variable font
fonts/BTSmor-Solid.ttf        static, MELT 0
fonts/BTSmor-Puddle.ttf       static, MELT 100
design/artboards/*.dc.html    28 design artboards (desktop 1440, tablet 768, mobile 390)
design/canvas.json            artboard names, sizes, canvas layout
reference/prototype/site.template.html   working scroll-effect prototype (old visual style)
reference/specimen.png        render of the font at four MELT values
font-source/smor.py, smor2.py   Python generator for the font (fonttools, shapely, pillow)
```

Reading the `.dc.html` artboards: they are plain HTML with inline styles, using a few custom tags (`<x-dc>`, `<helmet>`, `<sc-for list="{{…}}">`) and a small `renderVals()` script that supplies data. Ignore the wrapper; the inline `style="…"` values (font sizes, paddings, borders, grid templates, colours) are the spec. Font URLs like `/_blob/…` are placeholders for the font files in `fonts/`.

---

## 3. The font

**Family:** `BT Smör` (PostScript `BTSmor-Regular`, version 2.000). One style, three variable axes. Heavy geometric sans in the spirit of GT Walsheim / Otto Baumberger's poster lettering. At default it has **sharp corners** (flat-cut terminals, mitred joins, diagonal terminals cut horizontal/vertical). As MELT rises the corners round off, drips form, letters lean and sink, a puddle spreads under each glyph and bubbles rise.

### Axes
| Tag | Name | Min | Default | Max | Does |
|---|---|---|---|---|---|
| `MELT` | Meltiness | 0 | **0** | 100 | sharp → rounded → drips → puddle |
| `BUBL` | Bubbles | 0 | **100** | 100 | foam, floating bubble rings, sizzle droplets (only visible when MELT is high) |
| `SLMP` | Slump | 0 | **100** | 100 | how much glyphs lean, droop, sink and squash; lower = more readable when melted |

Named instances: Solid `0/100/100`, Soft `33/100/100`, Gooey `66/100/100`, Puddle `100/100/100`, Calm Puddle `100/40/20`, Hot Pan `100/100/0` (MELT/BUBL/SLMP).

Rough stage thresholds along MELT: corners start rounding immediately and are fully round by ~70; drips grow ~5–85; puddle ~28–92; bubbles ~45–100 (scaled by BUBL).

### OpenType features (CSS `font-feature-settings`)
- `ss01` — double-storey **a** for a, å, ä
- `ss02` — **square dots** for i, j, ä, ö, Ä, Ö and `. , : ; ! ?`

### Coverage and metrics
- A–Z, a–z (real lowercase), 0–9, `. , : ; ! ? - – — ' " ( ) / + =`, and **Æ Ø Å æ ø å Ä Ö É ä ö é**. 108 glyphs including alternates.
- **Not covered:** ü ß š ž and anything else — don't promise wider language support. No kerning. Unhinted.
- UPM 1000 · cap height 720 · x-height 540 · ascender 760 · descender −200. `hhea` ascent 950 / descent −300 (tall on purpose: puddles, drips and bubbles).
- Advance widths grow ~5% from MELT 0→100 (via gvar phantom points), and puddles extend beyond the advance so neighbouring puddles merge into one pool along a line.

### Using it in CSS
Use `tokens/tokens.css`. The key trick: register `--m/--b/--s` with `@property`, drive them as numbers, and CSS can **transition** font-variation-settings (hover-to-melt).

```css
.word { --m: 0; --b: 100; --s: 100; }
.word:hover { --m: 100; }                      /* with .bt-hover for the transition */
/* equivalent raw form */
font-variation-settings: "MELT" 42, "BUBL" 100, "SLMP" 100;
font-feature-settings: "ss01", "ss02";
```

### Things that will bite you
1. **Axis tags are uppercase** (`"MELT"`), custom axes are case-sensitive.
2. **Overlapping contours.** The font is built from overlapping strokes (OVERLAP_SIMPLE set) so it can morph. Modern browsers/OSes handle it. I verified rendering in headless Chrome (FreeType) only — **please QA in Safari, Firefox and Windows/DirectWrite.** Report seams or holes.
3. **Giant lines need breathing room.** At high MELT, drips/puddle fall below the baseline and bubbles float above the cap height. Give display lines `padding-bottom ≈ .08em`, don't clip with `overflow:hidden` on the line itself.
4. **Performance.** Each glyph is ~1,000 points × several variation tuples. Animating one big headline is fine; animating dozens of large glyphs per frame is not. Only update visible elements; update the custom property, not the whole style string; throttle with `requestAnimationFrame`.
5. **Hover doesn't exist on touch.** Wherever the artboards say "hover to melt", mobile copy says "tap" — implement tap-to-toggle.
6. Honour `prefers-reduced-motion`: keep scroll-linked state user-driven but drop autoplay loops (marquee drift, auto-drift, sweeps).
7. `font-display: block` for the display face.
8. The UI faces (Familjen Grotesk, DM Mono) come from Google Fonts. Self-host them if the site can't call Google.

---

## 4. Design language (non-negotiable)

- **Colours: black `#0A0A0A`, yellow `#FFD21F`, white `#FFFFFF` — nothing else.** No orange, red, cobalt, pink or cream. (Earlier iterations used them; the client dropped them.)
- **No cards, no drop shadows, no rounded panels, no gradients.** The only round shapes are the circular stickers in "In use" and the typeface's own dots.
- **Everything sits on 1px hairline rules.** Sections are divided into rows and columns by lines, not boxes. On yellow the guide lines are `rgba(10,10,10,.22)`; on black the rules are solid yellow; on white solid black.
- **Grid:** 12 columns on desktop (1440), 8 on tablet (768), 4 on mobile (390). The Hero draws the column lines visibly behind the word.
- **Metadata columns:** a narrow left column (220px desktop / 190px tablet) holds number, name and MELT value; the specimen takes the remaining width. On mobile these stack.
- **Type:** display = BT Smör. Body = Familjen Grotesk 15–20px / 1.4. Labels = DM Mono 11–12px, uppercase, tracking `.08–.09em`.
- **Sliders** are drawn as a 2px line with a 20px square marker (yellow fill, 2px black border) — never round thumbs.
- Section colour map: Hero **yellow**, Melt stages **black**, Axes **white**, Æ Ø Å **black**, Features **yellow**, Glyphs **white**, Tester **black** (stage is yellow), In use **white**, Specs **black**, Licence **white**.

---

## 5. Responsive rules

| Size | Design width | Applies | Layout notes |
|---|---|---|---|
| Desktop | 1440 | ≥ 1024 | 12-col, metadata column + specimen rows, side-by-side panels. Fluid between ~1024 and ~1600; scale specimen sizes with `clamp()` against viewport width, don't just hold the px values. |
| Tablet | 768 | 640–1023 | 8-col; Hero word stacks "BT" / "Smör" at 250px; rows keep the 190px metadata column; Axes become wide rows (not 3 columns); tester stage sits above the controls. |
| Mobile | 390 | < 640 | 4-col, everything stacked in single ruled column; Hero word stacks at 128px; nav collapses to logo + "Menu" (full-screen menu artboard); sticker grid 2-up; glyph grid 5-up. |

Specimen words were sized from measured advance widths so they fit their column — keep them on one line (`white-space: nowrap`) and size them from the container, not the viewport alone. Measured widths at MELT 0→100 (em): `BT Smör` 3.95→4.15, `Smør` 2.64→2.77, `Smör` 2.49→2.61, `smelter` 3.81→4.00, `brødskiva` 5.15→5.41, `Meny` 2.54→2.67.

---

## 6. Pages and artboards

Site order: **Hero → Melt stages → Axes → Æ Ø Å → Features → Glyphs → Tester → In use → Specs & Licence → Footer.** Anchor nav: Melt · Axes · Æ Ø Å · Glyphs · Tester · Specs · Licence (+ "Test the font →" and Licence as the black end-cap).

| Section | Desktop 1440 | Tablet 768 | Mobile 390 |
|---|---|---|---|
| Hero | `Main` (900) | `Tablet-Hero` (1024) | `Mobile-Hero` (844) + `Mobile-Menu` (844) |
| Melt stages | `Melt` (1040) | `Tablet-Melt` (1092) | `Mobile-Melt` (1412) |
| Axes | `Axes` (820) | `Tablet-Axes` (1200) | `Mobile-Axes` (1740) |
| Æ Ø Å | `Norge` (820) | `Tablet-Norge` (900) | `Mobile-Norge` (1650) |
| Features | `Features` (1000) | `Tablet-Features` (1260) | `Mobile-Features` (1400) |
| Glyphs | `Glyphs` (1190) | `Tablet-Glyphs` (2142) | `Mobile-Glyphs` (2750) |
| Tester | `Tester` (852) | `Tablet-Tester` (1010) | `Mobile-Tester` (1266) |
| In use | `InUse` (1100) | `Tablet-InUse` (1340) | `Mobile-InUse` (2450) |
| Specs & Licence | `Specs` (1410) | `Tablet-Specs` (2194) | `Mobile-Specs` (2924) |

Artboard heights are the heights of the comps, not constraints — let the real page flow.

### What each section is
- **Hero** — yellow, 12-column guide lines behind the page. Nav strip (logo cell · "Mood" selector Solid/Soft/Gooey/Puddle · links · black Licence cell), a 4-cell metadata strip (incl. live `BUBL 100 · SLMP 100` and `MELT 000 · Solid` readout), the giant word, a copy line, a "Scroll to turn up the heat" cell and a black "Test the font →" CTA. The comps expose MELT/BUBL/SLMP as tweaks. **Background stays yellow** (earlier version shifted to orange — removed).
- **Melt stages** — four full-width ruled rows on black. Columns: number + stage name + MELT value | "Smør" at that MELT (0 / 33 / 66 / 100) | description. No cards.
- **Axes** — three ruled columns (MELT, BUBL, SLMP). Each: tag + range, a specimen field (yellow / black / white) showing the axis in action (MELT 70; BUBL at MELT 100; SLMP 20 at MELT 100/BUBL 40), description, square-marker slider.
- **Æ Ø Å** — black, three ruled columns with giant Æ, Ø, Å at MELT 0 / 40 / 72, code points and an example word each (ærlig, smør, på).
- **Features** — four ruled rows comparing the same text ("Dagbladet? Hei, Åre!") as Default, `ss01`, `ss02`, `ss01 + ss02`; a single "heat all rows" control.
- **Glyphs** — inspector (big Å, name, U+, three axis sliders, ss01/ss02 chips) + ruled glyph grid (12/8/5 columns) in groups Nordic, Uppercase, Lowercase, Figures, Punctuation with black group headers.
- **Tester** — control panel (preset text, size, tracking, leading, alignment, MELT, BUBL, SLMP, feature chips, 4 themes) + yellow stage with the editable text and a live CSS readout. Themes in the comps: yellow/black, black/yellow, white/black, black/white.
- **In use** — flat, flush mockups: butter wrapper, melting poster (lines at MELT 0/34/68/100), menu card (ss01 on headings), sticker row (circles).
- **Specs & Licence** — black specs (four metric numbers; Axes, Named instances, Features, Coverage tables) then white licence tiers: Trial, **Desktop (yellow)**, Web, Custom.
- **Footer** — *not drawn in the new system.* Black, a giant "Smør" that melts as the footer scrolls into view (see prototype), small mono legal row. Apply §4.

### Designed vs. only in the prototype
The prototype also contains pieces that were **not redrawn** in the black/yellow/white system. Rebuild them with §4's rules if you include them: the scroll-reveal **statement** ("Most typefaces stay the way you left them…" with counters), the two **velocity marquees** (heat follows scroll speed), the **XY playground** (drag a dot: MELT × SLMP, plus presets and auto-drift), and the pinned **horizontal Æ Ø Å gallery** (glyphs heat up as they pass screen centre — the comps show three static columns instead; use the gallery only on desktop if you want the effect).

---

## 7. Behaviour spec (from the prototype)

Read `reference/prototype/site.template.html` — one `frame()` loop on `requestAnimationFrame` drives everything. Port the *logic*, not the styling (it still uses orange/cobalt/pink, shadows and rounded cards — all forbidden now). To run it, replace `__FONT__` in the file with the base64 of `fonts/BTSmor.woff2`.

| Effect | How it works |
|---|---|
| **Hero scroll-melt** | Section is ~340vh with a sticky inner (`top: var(--nav-h)`). Progress `p = clamp((navH − rect.top) / (rect.height − pinHeight))`. `MELT = clamp(p / .9) × 100` on the hero word. Readout text updates. DOM bubbles (outlined circles) drift up and fade in with MELT. |
| **Melt stages scrub** (suggested) | Rows are static in the comps. Optional: drive each row's MELT from its vertical position in the viewport, or run the prototype's pinned 4-stage scrub. |
| **Axis cards** | Sliders drift with scroll position until the user touches one (`auto` flag), plus "Sweep"/"Sizzle" buttons that tween. BUBL "sizzle" oscillates the value quickly. |
| **Playground** | Pointer-captured XY pad → MELT (x) × SLMP (y). Preset chips tween over 700ms with ease-in-out. |
| **Glyph inspector** | Click a cell → big glyph, name, U+ code; sliders and ss01/ss02 chips act on the big glyph; chips disable when the glyph has no alternate (ss01 only a å ä; ss02 only i j ä ö Ä Ö and `. , : ; ! ?`). |
| **Tester** | Everything live: text is `contenteditable`; size/tracking/leading/align/axes/features/theme; "Animate MELT" loops `50 − 50·cos(t)`; Reset; a code block mirrors the CSS. |
| **Feature rows** | Same text in four rows, each with its own `font-feature-settings`; rows drift horizontally with scroll (alternating direction). |
| **Hover-to-melt** | `@property`-registered `--m` transitions to 100 on hover/focus (`.bt-hover`). Tap on touch. |
| **Footer word** | MELT = progress of the footer entering the viewport. |
| **Nav** | Scroll-spy highlights the current section; 1–2px progress bar at the nav's bottom edge (yellow on black, no gradient). |

Implementation tips: set axes by writing `--m/--b/--s` on the element, skip writes when the value changed < 0.15, use `IntersectionObserver` to pause off-screen work, and use `overflow-x: clip` (not `hidden`) on `html/body` so `position: sticky` keeps working.

---

## 8. Suggested build plan

1. Scaffold (framework is your call; a static site or Astro/Vite with no UI library is plenty). Self-host fonts, preload `BTSmor.woff2`.
2. Wire `tokens/tokens.css`; build primitives: ruled grid, metadata row, label, specimen line, slider marker, glyph cell, tier, table block.
3. Build desktop sections in site order against the artboards; then tablet and mobile.
4. Add behaviours from §7, one section at a time; add `prefers-reduced-motion` handling as you go.
5. QA (checklist below), then performance pass.

## 9. Acceptance checklist
- [ ] Only black, yellow, white. No shadows, rounded cards or gradients anywhere.
- [ ] Every section matches its artboard at 1440 / 768 / 390 (check spacing, rules, type sizes).
- [ ] BT Smör renders correctly in Chrome, Safari, Firefox and on Windows (no seams/holes); MELT 0 shows crisp sharp corners.
- [ ] Hero word melts smoothly on scroll without jank on a mid-range phone.
- [ ] ss01 and ss02 toggles work in the tester, glyph inspector and features rows.
- [ ] Æ Ø Å æ ø å render in the display face everywhere they appear.
- [ ] Tester: all controls work; text is editable; CSS readout stays in sync.
- [ ] Keyboard: all controls reachable, visible focus, sliders operable with arrows; real `<button>`, `<a>`, `<input>`/`<label>` elements.
- [ ] Contrast: all text meets 4.5:1 (3:1 for the giant display type).
- [ ] Reduced motion respected. No horizontal scroll at any width.
- [ ] Lighthouse performance reasonable; fonts preloaded; no layout shift from font loading.

---

## 10. Open items — placeholders you must not invent
- **Licence tiers have no prices, terms or checkout.** Buttons say "Ask for pricing / Request trial / Get in touch". Wire to whatever the client decides.
- **No contact details, domain, social links, legal text or analytics** were specified. Footer copy is placeholder ("© 2026 BT"; the foundry name behind "BT" was never given).
- **Trial download** isn't built — needs a decision (form? direct link? email gate?).
- The **menu prices** in "In use" (129,–, 49,–, …) and the poster/venue text are mock content for the mockups, not facts.
- Copy mentions GT Walsheim and Otto Baumberger as *inspiration only*. The outlines are original; check with the client before keeping those names in public copy.
- Font licensing for the Google-hosted UI faces (Familjen Grotesk, DM Mono) is the client's call if self-hosting.

## 11. Known gaps and risks
- Artboards unrendered/unverified (see §1); tablet and mobile heights are estimates.
- Font tested in headless Chrome only; no kerning; limited glyph coverage; large variation data (see §3).
- The prototype was tested at 1440×900 and 390×844 (headless Chrome): no console errors, no horizontal overflow. It has **not** been tested on real devices.
- Footer, statement, marquees and playground haven't been redrawn in the final visual system.

## 12. If the font needs to change
`font-source/smor2.py` (imports `smor.py`) generates the whole variable font: glyph skeletons, melt deformation, axes, `ss01`/`ss02`. Needs `pip install fonttools shapely pillow brotli`. Run `python3 smor2.py out.ttf` (it expects the two scripts side by side). Most-wanted improvements: a kerning pass (especially A V W T Y), more glyph coverage, and a lighter weight.
