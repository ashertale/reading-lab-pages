# Concept Reading Lab

一個用靜態 HTML 建立的概念深讀原型。它把悖論、心理偏誤、系統思考與工程判斷整理成可搜尋、可比較、可繼續生成的閱讀頁。

## 架構總覽

```text
data/concept-payloads/<topic-slug>.json
data/concept-suggestions.json
  -> render step
  -> topics/<topic-slug>.html
  -> topic-index.js
  -> index.html / backlog.html
```

核心設計是把「可審核內容」、「生成頁面」、「首頁索引」和「介面行為」分開：

- `data/concept-payloads/*.json`：概念頁的可審核輸入，先整理文案、metadata、來源與 section 內容。
- `data/concept-suggestions.json`：尚未生成為完整頁面的候選主題，供 backlog 使用。
- `topics/*.html`：由 payload/render step 產生的概念深讀頁，保留固定 Reading Path。
- `topic-index.js`：首頁搜尋、排序、隨機閱讀與閱讀順序共用的索引。
- `index.html`：概念閱讀庫入口，只負責搜尋、排序與隨機閱讀。
- `backlog.html`：候選主題入口，獨立呈現尚未生成的 backlog。
- `index-page.js`：依 `topic-index.js` 渲染首頁清單。
- `backlog-page.js`：依 `topic-index.js` 渲染候選主題。
- `knowledge-page.css`：概念頁共用的安靜紙感閱讀 UI。
- `index-page.css`：首頁與 backlog desk 專用版面。

## 目前頁面

- `topics/ship-of-theseus.html`：悖論 / 思想實驗。
- `topics/goodharts-law.html`：指標悖論 / 系統思考。
- `topics/chestertons-fence.html`：判斷原則 / 制度啟發。
- `topics/cobra-effect.html`：系統思考 / 誘因失真。
- `topics/occams-razor.html`：判斷原則 / 模型選擇。
- `topics/prisoners-dilemma.html`：博弈 / 合作困境。
- `knowledge-topic-template.html`：render 新概念頁時參考的 HTML 骨架。

## 新增概念頁流程

1. 先建立 `data/concept-payloads/<topic-slug>.json`，讓主題內容可先被 review。
2. 依 payload render 出 `topics/<topic-slug>.html`，並保留 `core`、`setup`、`lenses`、`psychology`、`applications`、`misreadings`、`questions`、`sources` section id。
3. 在 payload 的 `indexEntry` 新增概念 metadata，`href` 指向 `./topics/<topic-slug>.html`，並保持 `order` 連續。
4. 若候選題已生成，從 `data/concept-suggestions.json` 移除或改寫為下一批候選題。
5. Topbar 只放全站入口：`首頁`、`待生成`、`模板`。不要把每個概念頁放進 topbar。
6. 檢查首頁、backlog 與新增頁面的桌面、窄版截圖。

Render 既有 payload：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\render_concept_page.py data\concept-payloads --sync-index
```

## 驗證建議

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py
```

這個驗證入口會檢查：

- `topic-index.js`、`index-page.js`、`backlog-page.js` 是否能被 JS parser 接受。
- `topics/*.html` 與 `topic-index.js` 是否和 payload / suggestions JSON 同步。
- `--check --sync-index` 是否沒有寫入副作用。
- HTML section 開關數、頁內 anchor target、概念頁必要 section 是否完整。
- CSS/HTML 是否出現禁用的 viewport type pattern：`font-size: *vw`、`clamp(`、負 `letter-spacing`。
- `data/concept-payloads/*.json` 與 `topics/*.html` 是否一一對齊。
