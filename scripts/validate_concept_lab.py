from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = ROOT / "topics"
PAYLOAD_DIR = ROOT / "data" / "concept-payloads"
TOPIC_INDEX_PATH = ROOT / "topic-index.js"
REQUIRED_TOPIC_SECTION_IDS = ("core", "setup", "lenses", "psychology", "applications", "misreadings", "questions", "sources")
SKIP_DIRS = {".git", ".superpowers", ".vscode", "__pycache__"}
FORBIDDEN_STYLE_PATTERNS = (
    re.compile(r"font-size\s*:[^;\n]*vw", re.I),
    re.compile(r"clamp\s*\(", re.I),
    re.compile(r"letter-spacing\s*:\s*-", re.I),
)
PLACEHOLDER_TEXT_PATTERNS = (
    re.compile(r"\[[^\]]+\]"),
    re.compile(r"這裡說明"),
    re.compile(r"這個主題凸顯"),
    re.compile(r"可以帶回現實"),
    re.compile(r"待補"),
    re.compile(r"TBD", re.I),
)
ALLOWED_REPEATED_TEXT = {
    "Reading Path",
    "Read For",
    "Core Tension",
    "Key Point",
    "Orientation",
    "Setup",
    "Lenses",
    "Psychology",
    "Applications",
    "Misreadings",
    "Questions",
    "Sources",
    "Reference",
    "下一步",
    "打開模板",
    "來源與整理方式",
    "讀法總覽",
    "問題設定",
    "判準透鏡",
    "心理連結",
    "現實映射",
    "誤讀校正",
    "延伸提問",
    "來源",
    "校正",
}


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_node() -> Path:
    env_node = os.environ.get("NODE")
    if env_node and Path(env_node).exists():
        return Path(env_node)

    path_node = shutil.which("node")
    if path_node:
        return Path(path_node)

    bundled = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin"
    bundled_node = bundled / ("node.exe" if os.name == "nt" else "node")
    if bundled_node.exists():
        return bundled_node

    raise RuntimeError("Cannot find Node.js. Set NODE to the node executable path.")


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip()


def check_js_parse(errors: list[str]) -> None:
    js_code = """
const fs = require('fs');
for (const file of ['topic-index.js', 'index-page.js', 'backlog-page.js']) {
  new Function(fs.readFileSync(file, 'utf8'));
}
console.log('js parse ok');
"""
    try:
        node = find_node()
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    code, output = run([str(node), "-e", js_code])
    if code:
        errors.append(f"JS parse failed:\n{output}")
        return
    print(output)


def check_render_sync(errors: list[str]) -> None:
    before = sha256(TOPIC_INDEX_PATH)
    code, output = run([
        sys.executable,
        str(ROOT / "scripts" / "render_concept_page.py"),
        "data/concept-payloads",
        "--check",
        "--sync-index",
    ])
    if output:
        print(output)
    if code:
        errors.append("render_concept_page.py --check --sync-index failed")
        return

    after = sha256(TOPIC_INDEX_PATH)
    if before != after:
        errors.append("topic-index.js changed during --check")
    else:
        print(f"check hash unchanged: {after}")


def html_files() -> list[Path]:
    return sorted(ROOT.glob("*.html")) + sorted(TOPICS_DIR.glob("*.html"))


def ids_in_html(text: str) -> set[str]:
    return {match.group("id") for match in re.finditer(r"id=(['\"])(?P<id>[^'\"]+)\1", text)}


def anchor_targets_in_html(text: str) -> set[str]:
    return {match.group("target") for match in re.finditer(r"<a\b[^>]*href=(['\"])#(?P<target>[^'\"]+)\1", text, re.I)}


def check_html_structure(errors: list[str]) -> None:
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        open_sections = text.count("<section")
        close_sections = text.count("</section>")
        print(f"{rel(path)} sections {open_sections}/{close_sections}")
        if open_sections != close_sections:
            errors.append(f"{rel(path)} has mismatched section tags: {open_sections}/{close_sections}")

        ids = ids_in_html(text)
        missing_anchors = sorted(anchor_targets_in_html(text) - ids)
        if missing_anchors:
            errors.append(f"{rel(path)} has missing anchor targets: {', '.join(missing_anchors)}")

        if path.parent == TOPICS_DIR:
            missing_sections = [section_id for section_id in REQUIRED_TOPIC_SECTION_IDS if section_id not in ids]
            if missing_sections:
                errors.append(f"{rel(path)} missing required sections: {', '.join(missing_sections)}")


def iter_source_files(suffixes: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        parts = set(path.relative_to(ROOT).parts)
        if parts & SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


def check_forbidden_styles(errors: list[str]) -> None:
    hits: list[str] = []
    for path in iter_source_files((".html", ".css")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern in FORBIDDEN_STYLE_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{rel(path)}:{line_number}: {line.strip()}")

    if hits:
        errors.append("Forbidden style patterns found:\n" + "\n".join(hits))
    else:
        print("forbidden style patterns: none")


def check_payload_topic_alignment(errors: list[str]) -> None:
    payload_outputs: set[Path] = set()
    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel(path)} invalid JSON: {exc}")
            continue

        target = payload.get("target", {})
        if not isinstance(target, dict) or not target.get("outputPath"):
            errors.append(f"{rel(path)} missing target.outputPath")
            continue

        output_path = ROOT / str(target["outputPath"])
        payload_outputs.add(output_path.resolve())

    topic_files = {path.resolve() for path in TOPICS_DIR.glob("*.html")}
    missing_topics = sorted(payload_outputs - topic_files)
    orphan_topics = sorted(topic_files - payload_outputs)

    if missing_topics:
        errors.append("Payloads reference missing topic files: " + ", ".join(rel(path) for path in missing_topics))
    if orphan_topics:
        errors.append("Topic files without payloads: " + ", ".join(rel(path) for path in orphan_topics))

    if not missing_topics and not orphan_topics:
        print(f"payload/topic alignment ok: {len(payload_outputs)} topics")


def payload_text_segments(payload: dict) -> list[str]:
    values: list[str] = []
    index_entry = payload.get("indexEntry", {})
    page = payload.get("page", {})

    if isinstance(index_entry, dict):
        for key in ("title", "subtitle", "type", "domain", "focus", "thesis"):
            value = index_entry.get(key)
            if isinstance(value, str):
                values.append(value)
        tags = index_entry.get("tags")
        if isinstance(tags, list):
            values.extend(tag for tag in tags if isinstance(tag, str))

    if isinstance(page, dict):
        for key in ("documentTitle", "bodyClass", "heroHtml", "mainHtml"):
            value = page.get(key)
            if isinstance(value, str):
                values.extend(re.findall(r">([^<>]+)<", value))

    cleaned: list[str] = []
    for value in values:
        text = re.sub(r"\s+", " ", value).strip()
        if text:
            cleaned.append(text)
    return cleaned


def check_payload_content_quality(errors: list[str]) -> None:
    repeated: dict[str, set[str]] = {}
    placeholder_hits: list[str] = []

    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        for segment in payload_text_segments(payload):
            for pattern in PLACEHOLDER_TEXT_PATTERNS:
                if pattern.search(segment):
                    placeholder_hits.append(f"{rel(path)}: {segment}")
                    break

            if len(segment) >= 36 and segment not in ALLOWED_REPEATED_TEXT:
                repeated.setdefault(segment, set()).add(rel(path))

    duplicate_hits = [
        f"{text} ({', '.join(sorted(paths))})"
        for text, paths in repeated.items()
        if len(paths) > 1
    ]

    if placeholder_hits:
        errors.append("Placeholder or empty-template text found:\n" + "\n".join(placeholder_hits))
    if duplicate_hits:
        errors.append("Repeated long payload text found:\n" + "\n".join(duplicate_hits[:20]))
    if not placeholder_hits and not duplicate_hits:
        print("payload content quality: ok")


def main() -> int:
    errors: list[str] = []
    check_js_parse(errors)
    check_render_sync(errors)
    check_html_structure(errors)
    check_forbidden_styles(errors)
    check_payload_topic_alignment(errors)
    check_payload_content_quality(errors)

    if errors:
        print("\nValidation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nconcept lab validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
