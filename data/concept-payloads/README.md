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
  "contentBrief": {
    "pressurePoint": "獎勵制度如果只量表面成果，會把解法推成製造更多問題的誘因。",
    "smallestScenario": "團隊用問題數量當獎勵依據，結果現場開始製造或保留更多可回報的問題。",
    "sourcePlan": [
      "核心來源說明 cobra effect 的誘因反轉故事",
      "相鄰來源補充 perverse incentive 或 unintended consequences"
    ],
    "transferTargets": ["產品指標設計", "製造測試獎懲"],
    "commonMisreading": "誤以為這只是在說人會鑽漏洞，而不是制度把漏洞變成理性選擇。",
    "readerQuestions": [
      "這個指標被最佳化後，現場會不會製造更多原本要消除的東西？",
      "誰能從表面數字變好、但實際問題變多之中得到好處？"
    ],
    "sectionIntents": {
      "core": "先指出獎勵和真實目標之間的張力。",
      "setup": "用最小故事呈現誘因如何反向生長。",
      "lenses": "拆開指標、行為回應與外部代價。",
      "psychology": "說明為什麼團隊容易相信可量化改善。",
      "applications": "轉到工程、產品與製造現場的指標設計。",
      "misreadings": "校正把問題簡化成個人道德的讀法。",
      "questions": "讓讀者檢查指標被最佳化後的副作用。",
      "sources": "交代故事來源、相鄰概念與教學整理邊界。"
    }
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
- 新增或修改 payload 時必須有 `contentBrief`。它不是顯示內容，而是生成前的品質合約，驗證器會檢查它是否具備不可互換的壓力點、最小情境、來源計畫、轉移場景、誤讀、讀者問題與每個 section 的意圖。
- 外框結構可以固定，但 `h2`、`section-lede`、`micro-note`、`sources` 說明、`Reference` 收尾都必須是 topic-specific，不要跨頁複用 `先抓住這題真正的壓力點`、`把它帶回現實場景`、`接著可以順讀...` 這類句型。
- 批次新增也不能用句型工廠填頁。每頁先寫自己的 pressure point、最小情境、失敗邊界、來源計畫，再進 payload。
- 禁用可替換句架，例如 `X 常不是抽象風險...`、`X 如果沒被提前畫出來...`、`X 一旦被低估...`、`把情境縮到一次普通判斷後...`。這些會被新/改 payload 的內容檢查擋下。
- 驗證器會把新/改 payload 和整個 corpus 做跨頁相似度與同 section 句架檢查；如果整頁或特定 section 太像既有頁，必須重寫，而不是只換幾個名詞。
- 若來源或應用段落是教學性 synthesis，要在 `sources` 裡明說。

常用指令：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\render_concept_page.py data\concept-payloads --sync-index
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py
```

若要掃描所有既有 payload 的制式句型舊債：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py --strict-content
```
