from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "topic-index.js"
PAYLOAD_DIR = ROOT / "data" / "concept-payloads"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def js_array_to_json(text: str) -> list[dict]:
    match = re.search(r"window\.CONCEPT_INDEX\s*=\s*(\[.*?\]);", text, re.S)
    if not match:
        raise ValueError("Cannot find window.CONCEPT_INDEX in topic-index.js")

    array_text = match.group(1)
    array_text = re.sub(r"(?m)^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', array_text)
    return json.loads(array_text)


def extract_between(text: str, start_pattern: str, end_tag: str, label: str) -> str:
    start = re.search(start_pattern, text, re.S)
    if not start:
        raise ValueError(f"Cannot find {label} start")
    content_start = start.end()
    end = text.find(end_tag, content_start)
    if end < 0:
        raise ValueError(f"Cannot find {label} end")
    return normalize_block(text[content_start:end])


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


def extract_text(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError(f"Cannot find {label}")
    return match.group(1).strip()


def payload_from_entry(entry: dict) -> dict:
    href = entry["href"].removeprefix("./")
    html_path = ROOT / href
    html = read_text(html_path)

    slug = entry["id"]
    return {
        "target": {
            "slug": slug,
            "outputPath": href.replace("\\", "/"),
        },
        "indexEntry": entry,
        "page": {
            "documentTitle": extract_text(r"<title>(.*?)</title>", html, "document title"),
            "bodyClass": extract_text(r'<body class="([^"]+)">', html, "body class"),
            "heroHtml": extract_between(
                html,
                r'<header class="hero" id="top">\s*',
                "\n  </header>",
                "hero",
            ),
            "mainHtml": extract_between(
                html,
                r'<main class="main-shell">\s*',
                "\n  </main>",
                "main",
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap payload JSON files from rendered concept pages.")
    parser.add_argument("--check", action="store_true", help="Validate extraction without writing payload files.")
    args = parser.parse_args()

    entries = js_array_to_json(read_text(INDEX_PATH))
    payloads = [payload_from_entry(entry) for entry in entries]

    if args.check:
        print(f"would extract {len(payloads)} payloads")
        return 0

    for payload in payloads:
        path = PAYLOAD_DIR / f"{payload['target']['slug']}.json"
        write_json(path, payload)
        print(f"wrote {path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
