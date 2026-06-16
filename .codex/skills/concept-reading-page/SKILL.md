---
name: concept-reading-page
description: Generate, refine, or maintain Concept Reading Lab knowledge-topic pages in the reading-lab-pages project. Use when Codex is asked to choose an interesting concept, create a concept payload, render a new HTML topic page, update the local index/navigation, refine the knowledge-page template or CSS, or verify the quiet paper-like concept reading UI.
---

# Concept Reading Page

Use this project skill for one deep knowledge-topic page in `reading-lab-pages`, or for template/UI refinements that affect those pages. The target experience is a quiet, editorial, paper-like reading page that teaches a concept through tension, criteria, real-world mapping, and careful source notes.

Default to Page Mode when the user says "generate", "create", "新增", "建立", or asks Codex to pick a random interesting topic. Default to UI Refinement Mode when the user comments on layout, padding, template structure, visual hierarchy, mobile behavior, or shared CSS.

## Mode Selection

- Use **Page Mode** to create one payload JSON, render one complete topic HTML page, and update library navigation.
- Use **Batch Page Mode** when the user asks for multiple concept pages in one request.
- Use **Topic Discovery Mode** when the user asks for a random/interesting topic without naming one.
- Use **UI Refinement Mode** when changing `knowledge-page.css`, `knowledge-topic-template.html`, spacing, section order, card treatment, or responsive behavior.
- Use **Maintenance Mode** when syncing links, homepage cards, section anchors, or source notes across existing pages.

## Source Policy

- Prefer stable, reputable sources: primary texts, encyclopedias, official or academic pages, and durable explainers.
- Browse before writing if the topic is unfamiliar, niche, source-sensitive, or if links/citations are needed.
- Do not over-cite inside prose. Keep source cards transparent and compact.
- Mark engineering, psychology, and application sections as teaching synthesis when they combine multiple sources or local reasoning.
- Avoid unsupported claims about origin/history. If origin is uncertain, state the uncertainty or omit the historical claim.

## Page Mode

1. If no topic is provided, choose one non-duplicate concept that contrasts with existing pages and maps well to engineering, judgment, systems, psychology, or philosophy.
2. Read [references/content-model.md](references/content-model.md) before writing the page.
3. Use an existing finished page as the nearest visual/content pattern:
   - `topics/ship-of-theseus.html` for paradox/identity topics.
   - `topics/goodharts-law.html` for metrics/systems topics.
   - `topics/chestertons-fence.html` for principle/engineering-judgment topics.
4. First create `data/concept-payloads/<topic-slug>.json`. Use lowercase hyphen-case slugs. New or modified payloads must include `contentBrief` with `pressurePoint`, `smallestScenario`, `sourcePlan`, `transferTargets`, `commonMisreading`, `readerQuestions`, and `sectionIntents`.
5. Render the payload with `scripts/render_concept_page.py` to `topics/<topic-slug>.html`. Do not place generated concept pages in the project root.
6. Keep the section ids stable: `core`, `setup`, `lenses`, `psychology`, `applications`, `misreadings`, `questions`, `sources`.
7. Keep topbar navigation concise and global only: `首頁`, `待生成`, `模板`. Do not add individual concept pages to the topbar.
8. Update the payload `indexEntry` with the new concept metadata: `id`, `title`, `subtitle`, `href`, contiguous `order`, `type`, `domain`, `focus`, `thesis`, and searchable `tags`. `href` should point to `./topics/<topic-slug>.html`, then rerun `scripts/render_concept_page.py --sync-index`.
9. If the topic came from `data/concept-suggestions.json`, remove or replace that backlog entry.
10. Update `index.html` only when the homepage shell itself changes. The normal library card/search rendering comes from `topic-index.js` and `index-page.js`.
11. Keep shared topic-page UI in `knowledge-page.css`; keep homepage/backlog UI in `index-page.css`. Do not add inline CSS.
12. Verify structure, JavaScript parsing, and visual rendering before reporting completion.

## Batch Page Mode

Use Batch Page Mode for any request that creates more than one concept page.

- Treat each page as its own real article. Do not use a prose generator, throwaway script, or copy/paste scaffold that fills many pages with parallel empty wording.
- Before writing payloads, choose a diverse batch: mix topic families, page types, engineering mappings, and source plans. Avoid adding five pages that all teach the same shape with different labels.
- Draft a one-line pressure point for every topic first. If two pressure points sound interchangeable, revise the topic or framing before creating files.
- Before writing payloads, draft a per-topic content brief: pressure point, smallest concrete scenario, source plan, engineering/product transfer, common misreading, and two reader questions. Do not start from a prose template and fill blanks.
- Store that brief in the payload as `contentBrief`; the validator treats this as a content contract for new or modified payloads.
- Give every page distinct `core`, `setup`, `lenses`, `applications`, `misreadings`, and `questions`. The Reading Path structure may repeat; the ideas, examples, and verbs should not.
- In `questions`, prefer a strong `h2` plus prompt cards. Do not add a bridge `section-lede` unless it carries genuinely irreplaceable topic-specific information; if it reads like glue copy, omit it.
- Reuse section ids only. Do not inherit another page's section `h2`, `section-lede`, `micro-note`, or `Reference` sentence stem just because the structure matches.
- Source cards must be topic-specific. Do not reuse a generic "synthesis note" unless it names what was synthesized for that exact topic.
- If automation is used, restrict it to mechanical file creation, indexing, rendering, or candidate listing. Do not let a script invent broad boilerplate prose across many pages.
- Treat `scripts/generate_concept_batch.py` as a legacy planning/catalog helper only. It is blocked by default from writing publishable payloads because it contains old template-prose stems.
- After rendering, skim the new pages side by side for repeated sentences, repeated card titles, vague filler, and mobile hero overflow before final verification.

## Dry-Run Mode

Use Dry-Run Mode when the user asks to test, simulate, audit, or review the page-generation flow without creating a page.

Dry-run output should include:

- Chosen candidate topic and why it stresses the template differently from existing pages.
- Proposed slug, page type, nearest existing pattern, and source plan.
- Draft hero thesis, three-word map, Reading Path section intent, and source cards.
- Payload JSON path, rendered HTML path, and navigation/index changes that would be needed if the page were actually created, especially the `topic-index.js` entry.
- Verification commands and screenshots that would be run after creation.
- Any risks in the skill, template, or codebase discovered during the simulation.

Do not create the payload JSON or topic HTML file in Dry-Run Mode unless the user explicitly asks to proceed.

## Topic Discovery Mode

Choose a topic that gives the template a new stress test, not just another page with the same shape.

Good topic families:

- Philosophical paradoxes: identity, ethics, knowledge, choice.
- Systems and incentives: metrics, feedback loops, unintended consequences.
- Engineering judgment principles: refactoring, safety margins, change risk, tradeoffs.
- Cognitive and decision patterns: bias, uncertainty, model error, attention.

Selection checks:

- Avoid duplicating the existing library.
- Prefer concepts with a crisp central tension.
- Prefer concepts that can produce concrete engineering/application examples.
- Prefer topics with stable public sources.

## UI Refinement Mode

Read [references/ui-ux-pattern.md](references/ui-ux-pattern.md) before changing CSS or layout.

Preserve the current visual language:

- Calm paper-like surface, fine grid texture, restrained sage/blue/rose accents.
- Editorial hierarchy with large serif topic title, compact metadata, and a left Reading Path.
- 8px or smaller radius, fine borders, restrained shadows, no nested cards.
- No decorative blobs, marketing sections, hero illustrations, or competing navigation systems.

When refining layout:

- Make Core Tension feel like a continuation of Orientation, not a sudden unrelated banner.
- Use padding and gap to make dense knowledge cards breathable.
- Keep mobile text readable and prevent horizontal overflow.
- Do not use viewport-scaled font sizes, `clamp()` for type, or negative letter spacing.

## Content Rules

- Teach the concept, not just its definition.
- Start with the pressure point: what intuition, criterion, or practical habit does the topic disturb?
- Give each section a distinct job. Do not repeat the same explanatory frame across cards.
- In batch work, no page may be a thin template wearing a new title. If a paragraph could be moved to another page unchanged, rewrite it with topic-specific tension, evidence, and consequences.
- Avoid placeholder prose such as "這裡說明", "這個主題凸顯", "可以帶回現實", or other sentences that describe the template instead of the concept.
- Avoid house-style stock phrasing reused across many pages, including headings like "先抓住這題真正的壓力點" and stems like "這裡的心理連結是教學性整理：", "接著可以順讀...", or "本頁主軸來自...工程映射則是依...". If the sentence could fit ten other topics with light noun swaps, rewrite it.
- Avoid generated formula stems such as "X 常不是抽象風險，而是會穿過具體接口、排程或權限邊界", "X 如果沒被提前畫出來，就很容易在現場才以更貴的形式出現", "X 一旦被低估，局部看似沒事的設計很快就會變成穩定性壓力", or "把情境縮到一次普通判斷後，X 會怎麼替你省事...". These are template leakage even when the nouns are accurate.
- Also reject newer batch-style frames such as "只要把 X 放回真實判斷，最先出現的就是這個張力", "真正要讀懂 X，得先把它放回『...』開始的現場", "這裡不把 X 當成單一答案", "X 常被做歪，往往不是因為沒聽過原理", "把 X 放進『...』這種現場最容易讀出它的手感", "這一節把 X 收束成可以帶回現場的追問", "若要把這頁往外推一步", "本頁先用 A 釐清 X 的主線", or "本頁把 X 拉到 A、B 這兩類場景". These are not acceptable house style; they are template leakage.
- The `questions` section is especially prone to template glue such as "下面兩個問題很適合..." or "這兩個追問會...". Do not rewrite those into softer boilerplate; remove the bridge line and let the question prompts do the teaching.
- Treat the validator as a floor, not a license. Passing `scripts/validate_concept_lab.py` does not make repeated sentence frames acceptable if a human can still recognize the template behind them.
- Use applications as transfer, not decoration. For this project, engineering or product examples are especially valuable.
- Keep common misreadings concrete and corrective.
- Keep source notes honest about what is sourced and what is synthesis.

## Verification

Always run fresh verification before claiming completion:

- Count opening/closing `<section>` tags for all changed HTML pages, including any newly created page and `index.html`.
- Search for forbidden type patterns: `font-size:.*vw`, `clamp\(`, and `letter-spacing: -`.
- Confirm section anchors exist for the Reading Path.
- Run the content lint in `scripts/validate_concept_lab.py`; fix placeholder prose, duplicated long text, and stock template sentence stems before reporting completion.
- The default content lint blocks generated-formula stems, missing/weak `contentBrief`, cross-page similarity, and repeated section sentence frames in new or modified payloads. Use `scripts/validate_concept_lab.py --strict-content` when deliberately auditing existing pages for formulaic legacy copy.
- Parse `topic-index.js`, `index-page.js`, and `backlog-page.js` when the homepage, backlog, or index data changes.
- Use browser/headless screenshots for at least desktop and a narrow viewport when layout changes or a new page is created.
- If the in-app Browser is unavailable, use local Chrome/Edge headless and state that fallback in the final answer.

Useful PowerShell checks:

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py
```

## References

- Read [references/content-model.md](references/content-model.md) for the page anatomy and writing expectations.
- Read [references/ui-ux-pattern.md](references/ui-ux-pattern.md) for visual style, spacing, responsive behavior, and screenshot verification.
