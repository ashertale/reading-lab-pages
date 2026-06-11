from __future__ import annotations

import argparse
import difflib
import json
import re
from html import escape
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD_DIR = ROOT / "data" / "concept-payloads"
DEFAULT_SUGGESTIONS_PATH = ROOT / "data" / "concept-suggestions.json"
TOPICS_DIR = ROOT / "topics"
TOPIC_INDEX_PATH = ROOT / "topic-index.js"
REQUIRED_INDEX_FIELDS = (
    "id",
    "title",
    "subtitle",
    "href",
    "order",
    "type",
    "domain",
    "focus",
    "thesis",
    "tags",
)
REQUIRED_PAGE_FIELDS = ("documentTitle", "bodyClass", "heroHtml", "mainHtml")
REQUIRED_SECTION_IDS = ("core", "setup", "lenses", "psychology", "applications", "misreadings", "questions", "sources")
REQUIRED_SUGGESTION_FIELDS = ("title", "type", "relation", "thesis")
HTML_ID_PATTERN = re.compile(r"id=(['\"])(?P<id>[^'\"]+)\1")
HTML_ANCHOR_PATTERN = re.compile(r"<a\b[^>]*href=(['\"])#(?P<target>[^'\"]+)\1", re.I)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_rel(path: str) -> str:
    return path.replace("\\", "/").removeprefix("./")


def payload_paths(inputs: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.json")))
        else:
            paths.append(path)
    return paths


def load_payload(path: Path) -> dict:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    validate_payload(payload, path)
    return payload


def load_suggestions(path: Path) -> list[dict]:
    if not path.exists():
        return []

    try:
        suggestions = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc

    if not isinstance(suggestions, list):
        raise ValueError(f"{path}: suggestions must be a list")

    for index, suggestion in enumerate(suggestions, start=1):
        if not isinstance(suggestion, dict):
            raise ValueError(f"{path}: suggestion {index} must be an object")
        for field in REQUIRED_SUGGESTION_FIELDS:
            if not suggestion.get(field):
                raise ValueError(f"{path}: suggestion {index} missing {field}")

    return suggestions


def html_ids(text: str) -> set[str]:
    return {match.group("id") for match in HTML_ID_PATTERN.finditer(text)}


def html_anchor_targets(text: str) -> set[str]:
    return {match.group("target") for match in HTML_ANCHOR_PATTERN.finditer(text)}


def validate_payload(payload: dict, path: Path) -> None:
    target = payload.get("target")
    page = payload.get("page")
    index_entry = payload.get("indexEntry")

    if not isinstance(target, dict):
        raise ValueError(f"{path}: target must be an object")
    if not isinstance(page, dict):
        raise ValueError(f"{path}: page must be an object")
    if not isinstance(index_entry, dict):
        raise ValueError(f"{path}: indexEntry must be an object")

    for field in ("slug", "outputPath"):
        if not target.get(field):
            raise ValueError(f"{path}: missing target.{field}")

    for field in REQUIRED_INDEX_FIELDS:
        if field not in index_entry:
            raise ValueError(f"{path}: missing indexEntry.{field}")

    if not isinstance(index_entry.get("order"), int):
        raise ValueError(f"{path}: indexEntry.order must be an integer")

    slug = str(target["slug"])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(f"{path}: target.slug must be lowercase hyphen-case")

    if index_entry.get("id") != slug:
        raise ValueError(f"{path}: indexEntry.id must match target.slug")

    output_path = normalize_rel(str(target["outputPath"]))
    expected_output_path = f"topics/{slug}.html"
    if output_path != expected_output_path:
        raise ValueError(f"{path}: target.outputPath must be {expected_output_path}")

    resolved_output = (ROOT / output_path).resolve()
    try:
        resolved_output.relative_to(TOPICS_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"{path}: target.outputPath must stay inside topics/") from exc

    expected_href = f"./{output_path}"
    if index_entry.get("href") != expected_href:
        raise ValueError(f"{path}: indexEntry.href must be {expected_href}")

    if not isinstance(index_entry.get("tags"), list) or not all(isinstance(tag, str) and tag.strip() for tag in index_entry["tags"]):
        raise ValueError(f"{path}: indexEntry.tags must be a list")

    for field in REQUIRED_PAGE_FIELDS:
        if not isinstance(page.get(field), str) or not page[field].strip():
            raise ValueError(f"{path}: missing page.{field}")

    main_html = page["mainHtml"]
    main_ids = html_ids(main_html)
    for section_id in REQUIRED_SECTION_IDS:
        if section_id not in main_ids:
            raise ValueError(f"{path}: page.mainHtml missing section id {section_id}")

    missing_anchor_targets = sorted(html_anchor_targets(main_html) - main_ids)
    if missing_anchor_targets:
        raise ValueError(f"{path}: page.mainHtml has missing anchor targets: {', '.join(missing_anchor_targets)}")


def render_payload(payload: dict) -> str:
    page = payload["page"]
    document_title = escape(page["documentTitle"])
    body_class = escape(page["bodyClass"], quote=True)
    hero_html = page["heroHtml"].strip()
    main_html = page["mainHtml"].strip()

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{document_title}</title>
  <link rel="stylesheet" href="../knowledge-page.css">
</head>
<body class="{body_class}">
  <nav class="topbar" aria-label="知識主題頁導覽">
    <div class="topbar-inner">
      <a class="brand" href="../index.html">Concept Reading Lab</a>
      <div class="topbar-links">
        <a href="../index.html">首頁</a>
        <a href="../backlog.html">待生成</a>
        <a href="../knowledge-topic-template.html">模板</a>
      </div>
    </div>
  </nav>

  <header class="hero" id="top">
{indent(hero_html, 4)}
  </header>

  <main class="main-shell">
{indent(main_html, 4)}
  </main>
</body>
</html>
"""


def indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    text = normalize_block(text)
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def normalize_block(text: str) -> str:
    lines = text.strip().splitlines()
    if len(lines) <= 1:
        return text.strip()

    indents = [
        len(line) - len(line.lstrip(" "))
        for line in lines[1:]
        if line.strip()
    ]
    remove = min(indents) if indents else 0
    if remove <= 0:
        return "\n".join(lines)

    normalized = [lines[0]]
    for line in lines[1:]:
        normalized.append(line[remove:] if line.startswith(" " * remove) else line.lstrip(" "))
    return "\n".join(normalized)


def write_or_check(payload: dict, check: bool) -> bool:
    output_path = (ROOT / normalize_rel(payload["target"]["outputPath"])).resolve()
    rendered = render_payload(payload)

    if check:
        if not output_path.exists():
            print(f"missing {output_path.relative_to(ROOT)}")
            return False
        current = read_text(output_path)
        if current != rendered:
            diff = difflib.unified_diff(
                current.splitlines(),
                rendered.splitlines(),
                fromfile=str(output_path.relative_to(ROOT)),
                tofile="rendered",
                lineterm="",
            )
            print("\n".join(list(diff)[:80]))
            return False
        print(f"ok {output_path.relative_to(ROOT)}")
        return True

    write_text(output_path, rendered)
    print(f"rendered {output_path.relative_to(ROOT)}")
    return True


def render_topic_index(payloads: list[dict], suggestions: list[dict]) -> str:
    entries = sorted((payload["indexEntry"] for payload in payloads), key=lambda item: (item["order"], item["id"]))
    orders = [entry["order"] for entry in entries]
    expected = list(range(1, len(entries) + 1))
    if orders != expected:
        raise ValueError(f"indexEntry.order must be contiguous: expected {expected}, got {orders}")

    return (
        "// Generated from data/concept-payloads/*.json and data/concept-suggestions.json. Edit source JSON, then rerun scripts/render_concept_page.py --sync-index.\n"
        f"window.CONCEPT_INDEX = {json.dumps(entries, ensure_ascii=False, indent=2)};\n\n"
        f"window.CONCEPT_SUGGESTIONS = {json.dumps(suggestions, ensure_ascii=False, indent=2)};\n"
    )


def sync_topic_index(payloads: list[dict], suggestions: list[dict]) -> None:
    generated = render_topic_index(payloads, suggestions)
    write_text(TOPIC_INDEX_PATH, generated)
    print(f"synced {TOPIC_INDEX_PATH.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Concept Reading Lab payload JSON files to HTML.")
    parser.add_argument("payloads", nargs="*", help="Payload JSON files or directories. Defaults to data/concept-payloads.")
    parser.add_argument("--check", action="store_true", help="Compare rendered output with existing files without writing.")
    parser.add_argument("--sync-index", action="store_true", help="Regenerate topic-index.js from payload and suggestion JSON files.")
    args = parser.parse_args()

    raw_inputs = args.payloads or [str(DEFAULT_PAYLOAD_DIR)]
    paths = payload_paths(raw_inputs)
    if not paths:
        raise ValueError("No payload JSON files found")

    payloads = [load_payload(path) for path in paths]
    ok = True
    for payload in payloads:
        ok = write_or_check(payload, args.check) and ok

    if args.sync_index:
        all_payloads = [load_payload(path) for path in payload_paths([str(DEFAULT_PAYLOAD_DIR)])]
        suggestions = load_suggestions(DEFAULT_SUGGESTIONS_PATH)
        if args.check:
            generated_index = render_topic_index(all_payloads, suggestions)
            current = read_text(TOPIC_INDEX_PATH)
            if generated_index != current:
                print("topic-index.js is not in sync")
                ok = False
            else:
                print("ok topic-index.js")
        else:
            sync_topic_index(all_payloads, suggestions)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
