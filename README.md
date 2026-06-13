# Concept Reading Lab

一個用靜態 HTML 建立的概念深讀原型。它把悖論、心理偏誤、系統思考與工程判斷整理成可搜尋、可比較、可繼續生成的閱讀頁。

## 目前狀態

- `topics/`：目前已發布 200 個概念頁；實際數量應持續和 `data/concept-payloads/` 一一對齊。
- `data/concept-payloads/`：目前 200 份可審核 payload，對應 200 個已發布頁面。
- `data/concept-suggestions.json`：目前為空，可作為下一批 backlog 入口。

## 架構總覽

```text
data/concept-payloads/<topic-slug>.json
data/concept-suggestions.json
  -> scripts/render_concept_page.py --sync-index
  -> topics/<topic-slug>.html
  -> topic-index.js
  -> index.html / backlog.html
```

核心設計是把「可審核內容」、「生成頁面」、「首頁索引」和「介面行為」分開：

- `data/concept-payloads/*.json`：概念頁的可審核輸入，先整理文案、 metadata、來源與 section 內容。
- `data/concept-suggestions.json`：尚未生成為完整頁面的候選主題，供 backlog 使用。
- `topics/*.html`：由 payload/render step 產生的概念深讀頁，保留固定 Reading Path。
- `topic-index.js`：首頁搜尋、排序、隨機閱讀與閱讀順序共用的索引。
- `index.html`：概念閱讀庫入口，只負責搜尋、排序與隨機閱讀。
- `backlog.html`：候選主題入口；若 `concept-suggestions.json` 為空，這裡就會呈現空 backlog。
- `index-page.js`：依 `topic-index.js` 渲染首頁清單。
- `backlog-page.js`：依 `topic-index.js` 渲染候選主題。
- `knowledge-page.css`：概念頁共用的安靜紙感閱讀 UI。
- `index-page.css`：首頁與 backlog desk 專用版面。

## Scripts 分層

- `scripts/generate_concept_batch.py`：批次產生新概念的 payload，先建立可 review 的內容輸入，再交給 render/validate 流程處理。
- `scripts/render_concept_page.py`：從 payload render `topics/*.html`，並可同步更新 `topic-index.js`。
- `scripts/validate_concept_lab.py`：檢查 HTML、index、payload 對齊、JS parse 與禁用樣式模式。
- `scripts/bootstrap_existing_concept_payloads.py`：從既有 `topic-index.js` 與 `topics/*.html` 反推 payload。
- `scripts/archive/`：存放一次性或歷史性的批次生成輔助腳本，不是日常維護主流程。

## 新增概念頁流程

1. 先建立 `data/concept-payloads/<topic-slug>.json`，讓主題內容可先被 review。
   若要批次新增，可先用 `scripts/generate_concept_batch.py` 產出 payload，再逐份審查。
2. 依 payload render 出 `topics/<topic-slug>.html`，並保留 `core`、`setup`、`lenses`、`psychology`、`applications`、`misreadings`、`questions`、`sources` section id。
3. 在 payload 的 `indexEntry` 新增概念 metadata，`href` 指向 `./topics/<topic-slug>.html`，並保持 `order` 連續。
4. 若候選題已生成，從 `data/concept-suggestions.json` 移除或改寫為下一批候選題。
5. Topbar 只放全站入口：`首頁`、`待生成`、`模板`。不要把每個概念頁放進 topbar。
6. 檢查首頁、backlog 與新增頁面的桌面、窄版截圖。

Render 既有 payload：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\render_concept_page.py data\concept-payloads --sync-index
```

批次建立新 payload：

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\generate_concept_batch.py
```

## 驗證

```powershell
& 'C:\Users\CHEN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_concept_lab.py
```

這個驗證入口會檢查：

- `topic-index.js`、`index-page.js`、`backlog-page.js` 是否能被 JS parser 接受。
- `topics/*.html` 與 `topic-index.js` 是否和 payload / suggestions JSON 同步。
- `scripts/render_concept_page.py --check --sync-index` 是否沒有寫入副作用。
- HTML section 開關數、頁內 anchor target、概念頁必要 section 是否完整。
- CSS/HTML 是否出現禁用的 viewport type pattern：`font-size: *vw`、`clamp(`、負 `letter-spacing`。
- `data/concept-payloads/*.json` 與 `topics/*.html` 是否一一對齊。
