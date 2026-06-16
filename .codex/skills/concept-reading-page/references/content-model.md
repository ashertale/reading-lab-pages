# Content Model

Use this reference when creating or substantially revising a Concept Reading Lab topic page.

New pages should be drafted as `data/concept-payloads/<slug>.json` first, then rendered to `topics/<slug>.html` with `scripts/render_concept_page.py`. The content model below describes both the JSON payload shape and the rendered page anatomy.

Current payloads keep page content as two HTML block strings:

- `contentBrief`: a non-rendered quality contract required for new or modified payloads.
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

- New or modified payloads must include `contentBrief` with these keys:
  - `pressurePoint`: the central tension in one concrete sentence.
  - `smallestScenario`: a minimal situation where the concept actually bites.
  - `sourcePlan`: at least two source notes naming what each source supports.
  - `transferTargets`: at least two engineering, product, system, organization, or self-understanding contexts.
  - `commonMisreading`: one concrete wrong reading the page must correct.
  - `readerQuestions`: at least two real questions the reader can apply.
  - `sectionIntents`: one topic-specific intent sentence for every required section id: `core`, `setup`, `lenses`, `psychology`, `applications`, `misreadings`, `questions`, `sources`.
- Put the concept's pressure point before history.
- Make `thesis` a real question or claim, not a subtitle.
- Make `Read For` describe what judgment ability the reader should gain.
- Let `Core Tension` summarize the unresolved conflict after Orientation sets it up.
- Prefer specific situations over abstract nouns.
- Keep repeated cards parallel in function, not identical in phrasing.
- Keep only the page anatomy shared. The visible copy should not converge on one house formula for section titles, section ledes, micro-notes, source disclosures, or "next step" lines.
- In the `questions` section, the safest default is no `section-lede`. Use the `h2` plus prompt cards as the framing, and only keep a bridge line if removing it would lose truly topic-specific content.
- Treat stock stems as template leakage. Avoid recurring phrasing such as "先抓住這題真正的壓力點", "把它帶回現實場景", "把它變成你的判斷工具", "這裡的心理連結是教學性整理：", or "接著可以順讀...".
- Treat generated sentence frames as template leakage even when the substituted nouns are accurate. Do not use frames like "X 常不是抽象風險，而是會穿過具體接口、排程或權限邊界", "X 如果沒被提前畫出來，就很容易在現場才以更貴的形式出現", "X 一旦被低估，局部看似沒事的設計很快就會變成穩定性壓力", or "把情境縮到一次普通判斷後，X 會怎麼替你省事...".
- Treat the 2026-06 batch frames as template leakage too. Avoid sentence families like "只要把 X 放回真實判斷，最先出現的就是這個張力", "真正要讀懂 X，得先把它放回『...』開始的現場", "這裡不把 X 當成單一答案", "X 常被做歪，往往不是因為沒聽過原理", "把 X 放進『...』這種現場最容易讀出它的手感", "這一節把 X 收束成可以帶回現場的追問", "若要把這頁往外推一步", "本頁先用 A 釐清 X 的主線", and "本頁把 X 拉到 A、B 這兩類場景".
- Treat `questions` bridge lines like "下面兩個問題很適合...", "下面兩問適合...", "這組提問要你先...", or "這兩個追問會..." as template leakage. Prefer deleting that line over writing another generic bridge sentence.
- Use the validator as a backstop, not as permission to reuse an unlisted sentence frame. If the prose still reads like a fill-in-the-blank family, rewrite it before render.
- Use English technical terms where they are the real term of art, but explain them in Traditional Chinese.
- Keep page copy original. Do not paste long source text.

## Batch Quality Standards

When creating multiple pages in one request:

- Write each topic from its own pressure point. Do not start from one generic template and swap nouns.
- Before payload work, write a compact content brief for each topic: pressure point, smallest concrete scenario, source plan, transfer target, common misreading, and two reader questions. If this brief sounds reusable across pages, revise it before writing HTML.
- Keep only the structural anatomy shared. The examples, verbs, card titles, questions, and source notes must be topic-specific.
- Keep the section ids stable, but rewrite section headings and section-lede voice for each topic. Matching layout does not justify matching wording.
- Avoid repeated phrases such as "這頁要幫你看見" across every hero. Vary the sentence shape according to the topic's actual learning goal.
- Prefer fewer strong pages over many shallow pages. If time or context pressure would force generic prose, reduce scope or pause with a clear status.
- Review new payloads side by side before rendering. Look for identical long sentences, identical section leads, generic "工程整理" source cards, and applications that could fit any topic.
- If using a helper script, use it only to assemble already-written, topic-specific content. Do not use it as a blank-filling content template.
- Do not use `scripts/generate_concept_batch.py` to create publishable page prose. It is a legacy catalog/planning helper and is blocked by default because it contains old template stems.
- `scripts/validate_concept_lab.py` compares new or modified payloads against the existing corpus. If a page is too similar overall, or if a section repeats another page's sentence frame, rewrite the prose before rendering/reporting completion.

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
