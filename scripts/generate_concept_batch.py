from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUGGESTIONS_PATH = ROOT / "data" / "concept-suggestions.json"
PAYLOAD_DIR = ROOT / "data" / "concept-payloads"
REQUIRED_SUGGESTION_FIELDS = ("title", "type", "relation", "thesis")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def load_suggestions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    raw = read_json(path)
    if not isinstance(raw, list):
        raise ValueError(f"{path}: suggestions must be a list")

    suggestions: list[dict[str, Any]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: suggestion {index} must be an object")
        missing = [field for field in REQUIRED_SUGGESTION_FIELDS if not item.get(field)]
        if missing:
            raise ValueError(f"{path}: suggestion {index} missing {', '.join(missing)}")
        suggestions.append(item)
    return suggestions


def published_slugs() -> set[str]:
    return {path.stem for path in PAYLOAD_DIR.glob("*.json")}


def suggestion_slug(suggestion: dict[str, Any]) -> str | None:
    slug = suggestion.get("slug")
    if not isinstance(slug, str):
        return None
    cleaned = slug.strip()
    return cleaned or None


def filtered_suggestions(
    suggestions: list[dict[str, Any]],
    *,
    topic_type: str | None,
    include_published: bool,
) -> list[dict[str, Any]]:
    published = published_slugs()
    items: list[dict[str, Any]] = []
    for suggestion in suggestions:
        if topic_type and suggestion["type"] != topic_type:
            continue
        slug = suggestion_slug(suggestion)
        if slug and slug in published and not include_published:
            continue
        items.append(suggestion)
    return items


def emit_table(suggestions: list[dict[str, Any]]) -> None:
    published = published_slugs()
    if not suggestions:
        print("no candidate suggestions in data/concept-suggestions.json")
        return

    for index, suggestion in enumerate(suggestions, start=1):
        slug = suggestion_slug(suggestion) or "-"
        status = "published" if slug in published else "backlog"
        print(
            f"{index:03d}\t{slug}\t{suggestion['title']}\t{suggestion['type']}\t"
            f"{status}\t{suggestion['relation']}\t{suggestion['thesis']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List Concept Reading Lab backlog suggestions from explicit JSON only. "
            "Payload generation was removed to prevent content-template leakage."
        )
    )
    parser.add_argument("--list-topics", action="store_true", help="List backlog suggestions without writing any payload.")
    parser.add_argument("--limit", type=int, help="Show only the first N suggestions after filtering.")
    parser.add_argument("--type", dest="topic_type", help="Filter suggestions by type field.")
    parser.add_argument("--include-published", action="store_true", help="Keep suggestions whose slug already exists as a payload.")
    parser.add_argument("--json", action="store_true", help="Output filtered suggestions as JSON.")
    parser.add_argument(
        "--suggestions-path",
        type=Path,
        default=DEFAULT_SUGGESTIONS_PATH,
        help="Path to the explicit suggestion list JSON.",
    )
    args = parser.parse_args()

    if not args.list_topics:
        parser.error(
            "Payload generation was removed. Maintain candidate ideas in data/concept-suggestions.json, "
            "write topic-specific payloads manually, then render with scripts/render_concept_page.py."
        )

    suggestions = load_suggestions(args.suggestions_path)
    items = filtered_suggestions(
        suggestions,
        topic_type=args.topic_type,
        include_published=args.include_published,
    )
    if args.limit is not None:
        items = items[: args.limit]

    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        emit_table(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
