# Archived Scripts

這裡存放一次性或歷史性的批次生成腳本。

原則：

- 日常維護以 `scripts/render_concept_page.py`、`scripts/validate_concept_lab.py`、`data/concept-payloads/*.json` 為主。
- `scripts/archive/` 內的腳本保留生成歷史與內容來源脈絡，不作為主要 maintenance workflow。
- `scripts/archive/concept-batches/` 目前視為本機歷史檔區，不納入版本控制，避免一次性生成碼持續放大 repo。
- 若未來需要再做批次生成，優先建立可重用流程，不要再把帶日期的一次性腳本直接放回 `scripts/` 根目錄。
