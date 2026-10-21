# BT Smör website — working rules

Read `HANDOFF.md` first. It is the brief. This file is the short version of the rules you must not break.

## Source of truth
- Visual design → `design/artboards/*.dc.html` (inline `style="…"` values are the spec; ignore the `<x-dc>` / `<helmet>` / `<sc-for>` wrapper tags).
- Tokens → `tokens/tokens.css` (use it as-is) and `tokens/tokens.json`.
- Behaviour → `reference/prototype/site.template.html` (logic only; its colours/shadows/cards are obsolete).

## Hard rules
1. **Three colours only:** `#0A0A0A` black, `#FFD21F` yellow, `#FFFFFF` white. No orange/red/cobalt/pink/cream.
2. **No cards, drop shadows, rounded panels or gradients.** Structure with 1px hairline rules on a 12 / 8 / 4-column grid (desktop 1440 / tablet 768 / mobile 390).
3. Display type is the `BT Smör` variable font. Drive it with `--m` (MELT), `--b` (BUBL), `--s` (SLMP) — see `tokens.css`. Axis tags are uppercase. Features: `ss01` (double-storey a), `ss02` (square dots).
4. Don't claim glyph coverage beyond A–Z a–z 0–9, basic punctuation and Æ Ø Å æ ø å Ä Ö É ä ö é.
5. Don't invent prices, licence terms, contact details, stats or legal copy — leave clearly marked placeholders and list them for the client.
6. Respect `prefers-reduced-motion`; hover effects need a tap equivalent on touch; real semantic controls and visible focus.
7. Update CSS custom properties from one `requestAnimationFrame` loop; only for elements in view.

## Before you call something done
- Screenshot every section at 1440, 768 and 390 and compare against the artboards.
- QA the font in Chrome, Safari, Firefox and Windows — it uses overlapping contours and has only been verified in headless Chrome.
- Run the checklist in `HANDOFF.md` §9.
- Report anything you couldn't verify, and anything you had to guess.

## Out of scope unless asked
Changing the font (`font-source/` exists if needed), changing the palette, adding libraries for effects the prototype already does with plain JS.
