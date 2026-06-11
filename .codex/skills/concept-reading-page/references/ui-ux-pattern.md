# UI/UX Pattern

Use this reference before changing topic page layout, shared CSS, responsive behavior, or homepage/library presentation.

## Visual Language

- Preserve the quiet paper reading feel: off-white surfaces, subtle grid texture, low-contrast ink, muted sage/blue/rose accents.
- Use large serif titles only in the hero. Keep card headings compact.
- Keep border radius at 8px or less.
- Use fine borders and restrained shadows.
- Avoid nested cards, decorative blobs, marketing copy, hero illustrations, or unrelated visual assets.

## Layout Expectations

- Topic pages use a sticky topbar, two-column hero, left Reading Path, and article column.
- The hero aside should stay compact: metadata rows plus the three-word `knowledge-map`.
- `Core Tension` should read as a callout connected to the Orientation paragraph.
- Card grids should breathe: prefer enough padding/gap over dense repeated cards.
- Tables should be used for comparison, not decoration.
- Homepage discovery uses `index.html`, `topic-index.js`, `index-page.js`, and `index-page.css`: keep the library searchable and data-driven instead of hand-maintaining repeated cards.
- Backlog discovery uses `backlog.html`, `topic-index.js`, `backlog-page.js`, and `index-page.css`; keep candidate topics out of the homepage.
- Homepage should stay focused on search/sort/random entry. Do not add Reading Path or Content Contract panels there.

## Responsive Rules

- At tablet/mobile widths, collapse hero, grids, and source cards to one column.
- Protect mixed Chinese/English strings with `min-width: 0` and `overflow-wrap: anywhere`.
- Keep mobile card padding generous enough for dense prose.
- Do not scale type with viewport width.
- Do not introduce `clamp()` type rules or negative letter spacing.

## Navigation

- Keep topbar labels short and global: `首頁`, `待生成`, `模板`.
- Do not put individual concept pages in the topbar. Use `index.html` search for full discovery.
- Keep rendered concept pages under `topics/`.
- Keep section ids stable so Reading Path links remain predictable.
- Keep homepage counts, search metadata, and suggested backlog topics aligned through `topic-index.js`.

## Verification Checklist

Run static checks:

- Opening and closing `<section>` counts match.
- No `font-size:.*vw`, `clamp\(`, or `letter-spacing: -`.
- New topic link appears in topbar/navigation where expected.

Run visual checks:

- Desktop screenshot around 1365px wide.
- Narrow screenshot around 500px wide.
- For homepage/library changes, include a screenshot tall enough to show the library cards.
- Inspect screenshots for overlap, cropped text, squeezed cards, or incoherent hierarchy.
