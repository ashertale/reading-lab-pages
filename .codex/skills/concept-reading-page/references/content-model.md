# Content Model

Use this reference when creating or substantially revising a Concept Reading Lab topic page.

New pages should be drafted as `data/concept-payloads/<slug>.json` first, then rendered to `topics/<slug>.html` with `scripts/render_concept_page.py`. The content model below describes both the JSON payload shape and the rendered page anatomy.

Current payloads keep page content as two HTML block strings:

- `page.heroHtml`: inserted inside `<header class="hero" id="top">`.
- `page.mainHtml`: inserted inside `<main class="main-shell">`.

This is deliberately conservative: it makes the generated output reviewable while avoiding a brittle over-modeled schema too early.

## Page Anatomy

Every topic page should keep this reading path:

1. `hero`: topic name, English/common label, thesis, read-for note, compact metadata, and three-word map.
2. `core`: Orientation lead-in, Core Tension callout, and three principle cards.
3. `setup`: minimal scenario, real difficulty, concept flow, and key point.
4. `lenses`: 2-4 ways to answer or interpret the same central problem, plus a comparison table when helpful.
5. `psychology`: why humans or teams are pulled into the mistake, paradox, or judgment pattern.
6. `applications`: concrete transfer into engineering, product, systems, organizations, or self-understanding.
7. `misreadings`: common fast but wrong interpretations, each with a correction.
8. `questions`: prompts that force the reader to choose criteria or apply the concept.
9. `sources`: concise source cards plus synthesis disclosure.

## Writing Standards

- Put the concept's pressure point before history.
- Make `thesis` a real question or claim, not a subtitle.
- Make `Read For` describe what judgment ability the reader should gain.
- Let `Core Tension` summarize the unresolved conflict after Orientation sets it up.
- Prefer specific situations over abstract nouns.
- Keep repeated cards parallel in function, not identical in phrasing.
- Use English technical terms where they are the real term of art, but explain them in Traditional Chinese.
- Keep page copy original. Do not paste long source text.

## Batch Quality Standards

When creating multiple pages in one request:

- Write each topic from its own pressure point. Do not start from one generic template and swap nouns.
- Keep only the structural anatomy shared. The examples, verbs, card titles, questions, and source notes must be topic-specific.
- Avoid repeated phrases such as "這頁要幫你看見" across every hero. Vary the sentence shape according to the topic's actual learning goal.
- Prefer fewer strong pages over many shallow pages. If time or context pressure would force generic prose, reduce scope or pause with a clear status.
- Review new payloads side by side before rendering. Look for identical long sentences, identical section leads, generic "工程整理" source cards, and applications that could fit any topic.
- If using a helper script, use it only to assemble already-written, topic-specific content. Do not use it as a blank-filling content template.

## Topic-Specific Emphasis

For paradox pages:

- Emphasize competing criteria and what each answer preserves or sacrifices.
- Use the table to compare answers.

For systems/incentive pages:

- Emphasize feedback loops, proxy goals, side effects, and failure modes.
- Use engineering/product examples early.

For principle/judgment pages:

- Emphasize when the principle applies, when it is misused, and what action it recommends.
- Use "before/after change" or "remove/replace" framing when useful.

For psychology/bias pages:

- Emphasize the mental shortcut, why it is useful, and where it breaks.
- Avoid reducing the whole topic to a label.

## Source Cards

Use three source cards when possible:

- Core source: original or canonical concept background.
- Neighbor/source: related law, theory, or adjacent concept.
- Synthesis note: what parts are teaching synthesis or engineering mapping.

Do not claim every application is directly sourced unless it is.

## Dry-Run Candidate Sketch

For dry-runs, sketch the page without writing the HTML:

- `topic`: Chinese name plus English/common name.
- `slug`: proposed hyphen-case filename.
- `pageType`: paradox, systems/incentive, principle/judgment, psychology/bias, or another clear type.
- `nearestPattern`: the existing rendered HTML page whose structure should guide the payload and render output.
- `hero`: draft thesis, Read For, metadata rows, and three-word map.
- `sections`: one sentence for each Reading Path section explaining its job.
- `sources`: three likely source cards and what each would support.
- `updates`: payload path, `topic-index.js` metadata, backlog changes, topbar/global navigation changes, and any source-note changes required if the page is created.
