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
STOCK_TEMPLATE_TEXT_PATTERNS = (
    re.compile(r"^先抓住這題真正的壓力點$"),
    re.compile(r"^為什麼人會被這題拉走$"),
    re.compile(r"^把它帶回現實場景$"),
    re.compile(r"^把它帶回工程現場$"),
    re.compile(r"^兩個容易走偏的讀法$"),
    re.compile(r"^把它變成你的判斷工具$"),
    re.compile(r"^這裡的心理連結是教學性整理"),
    re.compile(r"^接著可以順讀"),
    re.compile(r"^本頁主軸來自"),
    re.compile(r"工程映射則是依"),
    re.compile(r"^如果想把這頁"),
    re.compile(r"^如果要把這頁"),
    re.compile(r"^先把 .+ 壓到最小情境$"),
    re.compile(r"^用三個角度拆開 .+$"),
    re.compile(r"^只要把 .+ 縮小到一個日常選擇，大腦偷懶的地方就會變得很清楚。$"),
    re.compile(r"^這一段的重點不是湊例子，而是讓概念真的能回到你下一次要做的判斷裡。$"),
    re.compile(r"^這類概念最常被用來喊口號；真正有用的地方，往往被口號剛好蓋住。$"),
    re.compile(r"^把它變成你的追問工具$"),
    re.compile(r"^為什麼人和團隊會在這題上失手$"),
    re.compile(r"^把心理層次看清楚，才能避免把錯全怪在個人意志薄弱。$"),
    re.compile(r"^下面兩個問題很適合拿去對照最近的設計、會議或決策。$"),
    re.compile(r"^你要如何確認那不是剛好、不是被回饋扭曲、也不是把問題轉移到更後面？$"),
    re.compile(r"^這張卡幫你把主題放回更大的理論背景，避免把它讀成單一口號或孤立趣題。$"),
    re.compile(r"^.+ 最有用的地方，不在表態，而在幫你排出一個追問順序：哪些前提要先查，哪些代價不能晚點才承認。$"),
    re.compile(r"^.+ 真正提供的不是立場，而是一組追問順序：先查 .+，再看 .+，最後確認 .+ 是否真的站得住。$"),
    re.compile(r"^.+ 這條線不是在替原則補標語，而是在逼你看清楚：一旦優先保 .+，還有什麼代價會被一起推進來。$"),
    re.compile(r"^.+ 最難落地的地方，不在原則本身，而在現場通常有更快、更省事、看起來更不會得罪人的捷徑。$"),
    re.compile(r"^這條原則的價值，要放回 .+、.+ 這些真要做決策的場景裡才看得出來；離開場景就只剩口號。$"),
    re.compile(r"^最常見的誤讀，是把 .+ 當立場標語，而不是拿來安排追問順序。$"),
    re.compile(r"^下面兩個問題的目的，不是替原則再包裝一次，而是逼你在 .+ 或 .+ 這些現場情境裡先問對前提。$"),
    re.compile(r"^本頁先用 .+ 條目說清楚原則本身，再用 .+ 補上它為什麼在 .+ 裡特別容易被誤用。$"),
    re.compile(r"^先讓原則落在一次真的要做判斷的場景，才能看出 .+ 和 .+ 到底誰該先被問、.+ 又要怎麼被確認。$"),
    re.compile(r"^本頁把 .+ 往 .+ 延伸的部分，屬於依照上述概念結構展開的教學性 synthesis。$"),
    re.compile(r"^延伸閱讀可以和.+對照，看看它如何補強.+留下的壓力，或把問題改寫成另一種版本。$"),
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
MEDIUM_REPEAT_MIN_LEN = 12
MEDIUM_REPEAT_MAX_LEN = 35
MEDIUM_REPEAT_RATE = 0.05
MEDIUM_REPEAT_MIN_FILES = 5


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


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def sentence_like_units(segment: str) -> list[str]:
    parts = re.split(r"(?<=[。！？；.!?])\s+", segment)
    units: list[str] = []
    for part in parts:
        text = re.sub(r"\s+", " ", part).strip().rstrip("。！？；.!? ")
        if text:
            units.append(text)
    return units


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def check_payload_content_quality(errors: list[str]) -> None:
    repeated: dict[str, set[str]] = {}
    medium_repeated: dict[str, set[str]] = {}
    placeholder_hits: list[str] = []
    stock_phrase_hits: list[str] = []
    payload_count = 0

    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        payload_count += 1

        for segment in payload_text_segments(payload):
            for pattern in PLACEHOLDER_TEXT_PATTERNS:
                if pattern.search(segment):
                    placeholder_hits.append(f"{rel(path)}: {segment}")
                    break

            for pattern in STOCK_TEMPLATE_TEXT_PATTERNS:
                if pattern.search(segment):
                    stock_phrase_hits.append(f"{rel(path)}: {segment}")
                    break

            if len(segment) >= 36 and segment not in ALLOWED_REPEATED_TEXT:
                repeated.setdefault(segment, set()).add(rel(path))

            for unit in sentence_like_units(segment):
                if unit in ALLOWED_REPEATED_TEXT:
                    continue
                if not contains_cjk(unit):
                    continue
                if MEDIUM_REPEAT_MIN_LEN <= len(unit) <= MEDIUM_REPEAT_MAX_LEN:
                    medium_repeated.setdefault(unit, set()).add(rel(path))

    placeholder_hits = dedupe_keep_order(placeholder_hits)
    stock_phrase_hits = dedupe_keep_order(stock_phrase_hits)
    duplicate_hits = [
        f"{text} ({', '.join(sorted(paths))})"
        for text, paths in repeated.items()
        if len(paths) > 1
    ]
    medium_repeat_threshold = max(MEDIUM_REPEAT_MIN_FILES, int(payload_count * MEDIUM_REPEAT_RATE))
    medium_duplicate_hits = [
        f"{text} ({len(paths)} files: {', '.join(sorted(paths)[:8])}{' ...' if len(paths) > 8 else ''})"
        for text, paths in medium_repeated.items()
        if len(paths) >= medium_repeat_threshold
    ]

    if placeholder_hits:
        errors.append("Placeholder or empty-template text found:\n" + "\n".join(placeholder_hits))
    if stock_phrase_hits:
        preview = "\n".join(stock_phrase_hits[:40])
        if len(stock_phrase_hits) > 40:
            preview += "\n..."
        errors.append(
            "Stock template phrasing found. Rewrite these into topic-specific language instead of repeating house formulas:\n"
            + preview
        )
    if duplicate_hits:
        errors.append("Repeated long payload text found:\n" + "\n".join(duplicate_hits[:20]))
    if medium_duplicate_hits:
        errors.append(
            f"Repeated medium-length payload text found (possible house formula; threshold {medium_repeat_threshold} files):\n"
            + "\n".join(medium_duplicate_hits[:20])
        )
    if not placeholder_hits and not stock_phrase_hits and not duplicate_hits and not medium_duplicate_hits:
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
