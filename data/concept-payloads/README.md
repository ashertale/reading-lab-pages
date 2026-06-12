# Concept Payloads

新概念頁先在這裡建立 payload，再 render 到 `topics/<slug>.html`。

建議檔名：

```text
data/concept-payloads/<slug>.json
```

最小 contract：

```json
{
  "target": {
    "slug": "cobra-effect",
    "outputPath": "topics/cobra-effect.html"
  },
  "indexEntry": {
    "id": "cobra-effect",
    "title": "眼鏡蛇效應",
    "subtitle": "Cobra Effect",
    "href": "./topics/cobra-effect.html",
    "order": 4,
    "type": "系統思考 / 誘因失真",
    "domain": "系統與誘因",
    "focus": "Unintended incentives",
    "thesis": "當獎勵制度只看表面結果，解法可能反過來製造更多原本要消除的問題。",
    "tags": ["systems", "incentives", "unintended consequences"]
  },
  "page": {
    "documentTitle": "眼鏡蛇效應 | Concept Reading Lab",
    "bodyClass": "knowledge-page knowledge-cobra-effect",
    "heroHtml": "<div class=\"hero-inner\">...</div>",
    "mainHtml": "<aside class=\"compass\">...</aside><article class=\"article\">...</article>"
  }
}
```

原則：

- payload 放內容與 metadata，不放排版 CSS；目前 page body 採 `heroHtml` / `mainHtml` block 字串，供 renderer 填入固定外框。
- render 後的 HTML 放在 `topics/`，不要放在 repo root。
- `indexEntry.href` 一律使用 `./topics/<slug>.html`。
- `target.slug`、`indexEntry.id`、`target.outputPath` 與 `indexEntry.href` 必須指向同一個 slug。
- 外框結構可以固定，但 `h2`、`section-lede`、`micro-note`、`sources` 說明、`Reference` 收尾都必須是 topic-specific，不要跨頁複用 `先抓住這題真正的壓力點`、`把它帶回現實場景`、`接著可以順讀...` 這類句型。
- 若來源或應用段落是教學性 synthesis，要在 `sources` 裡明說。

常用指令：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\render_concept_page.py data\concept-payloads --sync-index
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py
```
