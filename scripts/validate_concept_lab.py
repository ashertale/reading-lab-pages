from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from difflib import SequenceMatcher
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
GENERATED_FORMULA_TEXT_PATTERNS = (
    re.compile(r"^.+ 抓到的不是抽象名詞，而是大腦在 .+ 裡最常拿來省事的那一步。?$"),
    re.compile(r"^先抓 .+ 在哪一步接手$"),
    re.compile(r"^再看 .+ 被怎麼剪掉$"),
    re.compile(r"^最後查 .+ 如何把偏差變順手$"),
    re.compile(r"^.+ 往往在你還沒自覺前就先決定了要看哪些資訊。?$"),
    re.compile(r"^.+ 一旦被順手省略，錯判通常會看起來特別像合理直覺。?$"),
    re.compile(r"^.+ 常讓人覺得自己只是照常判斷，卻沒發現路徑已經被偷窄。?$"),
    re.compile(r"^把情境縮到一次普通判斷後，.+ 會怎麼替你省事、又怎麼順手砍掉 .+，都會清楚很多。?$"),
    re.compile(r"^.+ 指向的是大腦在 .+ 上最愛走的近路：短期省力，卻常順手把 .+ 壓得太窄。?$"),
    re.compile(r"^.+ 之所以難纏，是因為它剛好踩在大腦最想省時間的地方，所以看起來特別像自然反應。?$"),
    re.compile(r"^.+ 很常不是因為你不知道，而是因為當下那條省力路真的太順手、太像合理判斷。?$"),
    re.compile(r"^大腦遇到 .+ 時，通常不是故意犯錯，而是先用最快的近路把世界壓成可處理大小。?$"),
    re.compile(r"^.+ 最有用的時候，不是拿來貼標籤，而是去檢查 .+ 裡哪一步被省力機制偷走了。?$"),
    re.compile(r"^在 .+ 這種情境，.+ 常讓人把 .+ 當成可靠訊號，卻沒看見 .+ 已經被剪掉。?$"),
    re.compile(r"^.+ 常不是抽象風險，而是會穿過具體接口、排程或權限邊界。?$"),
    re.compile(r"^.+ 如果沒被提前畫出來，就很容易在現場才以更貴的形式出現。?$"),
    re.compile(r"^.+ 一旦被低估，局部看似沒事的設計很快就會變成穩定性壓力。?$"),
    re.compile(r"^.+ 通常不會單獨出現；它多半會穿過接口、權限或排程邊界，把 .+ 轉成真正的穩定性壓力。?$"),
    re.compile(r"^.+ 會讓人把『目前沒爆』誤讀成『設計沒問題』，於是風險一路被推往更後面。?$"),
    re.compile(r"^.+ 最危險的地方，在於它常把局部成功包裝成全局安全。?$"),
    re.compile(r"^只要 .+ 一進場，團隊就容易先相信現況撐得住，而不是先問代價正在往哪裡堆。?$"),
    re.compile(r"^這裡重點不是補幾個抽象案例，而是把 .+ 直接落到 .+ 這些真的會出事的邊界上。?$"),
    re.compile(r"^把 .+ 帶回 .+ 時，最該先畫出來的是 .+ 穿過接口、時序或權限邊界的那條路。?$"),
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
CONTENT_BRIEF_STRING_FIELDS = ("pressurePoint", "smallestScenario", "commonMisreading")
CONTENT_BRIEF_LIST_FIELDS = ("sourcePlan", "transferTargets", "readerQuestions")
CONTENT_BRIEF_MIN_FIELD_LEN = 18
CONTENT_BRIEF_MIN_LIST_ITEMS = 2
CONTENT_BRIEF_LIST_ITEM_MIN_LEN = {
    "sourcePlan": 10,
    "transferTargets": 4,
    "readerQuestions": 10,
}
CONTENT_BRIEF_REQUIRED_SECTION_IDS = REQUIRED_TOPIC_SECTION_IDS
PAGE_SIMILARITY_THRESHOLD = 0.30
SECTION_FRAME_SIMILARITY_THRESHOLD = 0.82
SECTION_FRAME_JACCARD_GATE = 0.28
SECTION_FRAME_MIN_LEN = 24
SECTION_FRAME_MAX_HITS_PER_SECTION = 3
SECTION_FRAME_MAX_HITS_TOTAL = 30
BRIEF_GENERIC_PATTERNS = (
    re.compile(r"這裡說明"),
    re.compile(r"這個主題"),
    re.compile(r"本頁(會|要|可以)?(說明|介紹|整理)"),
    re.compile(r"實際場景"),
    re.compile(r"相關來源"),
    re.compile(r"待補"),
    re.compile(r"TBD", re.I),
)


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
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        return 127, str(exc)
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
                if key in {"heroHtml", "mainHtml"}:
                    values.extend(text_nodes_from_html(value))
                else:
                    values.append(value)

    content_brief = payload.get("contentBrief")
    if isinstance(content_brief, dict):
        values.extend(flatten_content_brief_values(content_brief))

    cleaned: list[str] = []
    for value in values:
        text = re.sub(r"\s+", " ", value).strip()
        if text:
            cleaned.append(text)
    return cleaned


def text_nodes_from_html(html: str) -> list[str]:
    values: list[str] = []
    for value in re.findall(r">([^<>]+)<", html):
        text = re.sub(r"\s+", " ", value).strip()
        if text:
            values.append(text)
    return values


def flatten_content_brief_values(value: object) -> list[str]:
    values: list[str] = []
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, list):
        for item in value:
            values.extend(flatten_content_brief_values(item))
    elif isinstance(value, dict):
        for item in value.values():
            values.extend(flatten_content_brief_values(item))
    return values


def payload_section_segments(payload: dict) -> dict[str, list[str]]:
    page = payload.get("page", {})
    sections: dict[str, list[str]] = {}
    if not isinstance(page, dict):
        return sections

    hero_html = page.get("heroHtml")
    if isinstance(hero_html, str):
        sections["hero"] = text_nodes_from_html(hero_html)

    main_html = page.get("mainHtml")
    if not isinstance(main_html, str):
        return sections

    for match in re.finditer(
        r"<section\b[^>]*\bid=(['\"])(?P<id>[^'\"]+)\1[^>]*>(?P<body>.*?)</section>",
        main_html,
        re.I | re.S,
    ):
        section_id = match.group("id")
        sections[section_id] = text_nodes_from_html(match.group("body"))

    return sections


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


def normalize_for_similarity(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[，。！？、；：,.!?;:「」『』（）()《》【】\\[\\]\"'`~\\-—_ ]+", "", text)
    return text


def char_ngrams(text: str, n: int = 4) -> set[str]:
    text = normalize_for_similarity(text)
    return {
        text[index : index + n]
        for index in range(max(0, len(text) - n + 1))
        if contains_cjk(text[index : index + n])
    }


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def meaningful_text_units(segments: list[str], min_len: int = SECTION_FRAME_MIN_LEN) -> list[str]:
    units: list[str] = []
    for segment in segments:
        if segment in ALLOWED_REPEATED_TEXT:
            continue
        for unit in sentence_like_units(segment):
            normalized = normalize_for_similarity(unit)
            if len(normalized) < min_len:
                continue
            if not contains_cjk(normalized):
                continue
            units.append(unit)
    return units


def page_similarity_text(payload: dict) -> str:
    units = meaningful_text_units(payload_text_segments(payload), min_len=16)
    return "".join(normalize_for_similarity(unit) for unit in units)


def text_similarity(left: str, right: str) -> float:
    left_normalized = normalize_for_similarity(left)
    right_normalized = normalize_for_similarity(right)
    if not left_normalized or not right_normalized:
        return 0.0
    length_ratio = min(len(left_normalized), len(right_normalized)) / max(len(left_normalized), len(right_normalized))
    if length_ratio < 0.55:
        return 0.0

    left_grams = char_ngrams(left_normalized, n=3)
    right_grams = char_ngrams(right_normalized, n=3)
    if jaccard(left_grams, right_grams) < SECTION_FRAME_JACCARD_GATE:
        return 0.0
    return SequenceMatcher(None, left_normalized, right_normalized).ratio()


def changed_payload_paths() -> set[Path] | None:
    commands = (
        ["git", "diff", "--name-only", "--diff-filter=ACMR", "--", "data/concept-payloads"],
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "data/concept-payloads"],
        ["git", "ls-files", "--others", "--exclude-standard", "--", "data/concept-payloads"],
    )
    changed: set[Path] = set()
    for command in commands:
        code, output = run(command)
        if code:
            return None
        for line in output.splitlines():
            name = line.strip()
            if not name.endswith(".json") or not name.startswith("data/concept-payloads/"):
                continue
            changed.add((ROOT / name).resolve())
    return changed


def brief_text_has_forbidden_pattern(text: str) -> bool:
    pattern_groups = (PLACEHOLDER_TEXT_PATTERNS, STOCK_TEMPLATE_TEXT_PATTERNS, GENERATED_FORMULA_TEXT_PATTERNS, BRIEF_GENERIC_PATTERNS)
    return any(pattern.search(text) for patterns in pattern_groups for pattern in patterns)


def check_brief_string(path: Path, label: str, value: object, hits: list[str], min_len: int = CONTENT_BRIEF_MIN_FIELD_LEN) -> None:
    if not isinstance(value, str):
        hits.append(f"{rel(path)}: contentBrief.{label} must be a string")
        return

    text = re.sub(r"\s+", " ", value).strip()
    if len(normalize_for_similarity(text)) < min_len:
        hits.append(f"{rel(path)}: contentBrief.{label} is too short or vague: {text}")
        return

    if brief_text_has_forbidden_pattern(text):
        hits.append(f"{rel(path)}: contentBrief.{label} uses placeholder or formulaic wording: {text}")


def check_brief_string_list(path: Path, label: str, value: object, hits: list[str], min_items: int = CONTENT_BRIEF_MIN_LIST_ITEMS) -> None:
    if not isinstance(value, list):
        hits.append(f"{rel(path)}: contentBrief.{label} must be a list")
        return
    if len(value) < min_items:
        hits.append(f"{rel(path)}: contentBrief.{label} needs at least {min_items} items")
        return

    normalized_items: list[str] = []
    item_min_len = CONTENT_BRIEF_LIST_ITEM_MIN_LEN.get(label, 10)
    for index, item in enumerate(value, start=1):
        item_label = f"{label}[{index}]"
        check_brief_string(path, item_label, item, hits, min_len=item_min_len)
        if isinstance(item, str):
            normalized_items.append(normalize_for_similarity(item))

    if len(set(normalized_items)) < len(normalized_items):
        hits.append(f"{rel(path)}: contentBrief.{label} contains repeated items")


def check_content_brief(path: Path, payload: dict) -> list[str]:
    hits: list[str] = []
    brief = payload.get("contentBrief")
    if not isinstance(brief, dict):
        return [f"{rel(path)}: missing contentBrief for new or modified payload"]

    for field in CONTENT_BRIEF_STRING_FIELDS:
        check_brief_string(path, field, brief.get(field), hits)

    for field in CONTENT_BRIEF_LIST_FIELDS:
        check_brief_string_list(path, field, brief.get(field), hits)

    questions = brief.get("readerQuestions")
    if isinstance(questions, list):
        for index, question in enumerate(questions, start=1):
            if isinstance(question, str) and "？" not in question and "?" not in question:
                hits.append(f"{rel(path)}: contentBrief.readerQuestions[{index}] must be phrased as a question")

    section_intents = brief.get("sectionIntents")
    if not isinstance(section_intents, dict):
        hits.append(f"{rel(path)}: contentBrief.sectionIntents must be an object keyed by section id")
    else:
        missing = [section_id for section_id in CONTENT_BRIEF_REQUIRED_SECTION_IDS if section_id not in section_intents]
        if missing:
            hits.append(f"{rel(path)}: contentBrief.sectionIntents missing: {', '.join(missing)}")
        for section_id in CONTENT_BRIEF_REQUIRED_SECTION_IDS:
            if section_id in section_intents:
                check_brief_string(path, f"sectionIntents.{section_id}", section_intents[section_id], hits, min_len=12)

    return hits


def payload_title(payload: dict) -> str:
    index_entry = payload.get("indexEntry", {})
    if isinstance(index_entry, dict):
        title = index_entry.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    target = payload.get("target", {})
    if isinstance(target, dict) and target.get("slug"):
        return str(target["slug"])
    return "unknown"


def load_payloads_for_quality(errors: list[str]) -> dict[Path, dict]:
    payloads: dict[Path, dict] = {}
    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        try:
            payloads[path.resolve()] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel(path)} invalid JSON: {exc}")
    return payloads


def check_page_similarity(payloads: dict[Path, dict], scope: set[Path]) -> list[str]:
    texts = {path: page_similarity_text(payload) for path, payload in payloads.items()}
    grams = {path: char_ngrams(text, n=4) for path, text in texts.items()}
    hits: list[str] = []

    for path in sorted(scope):
        if path not in payloads:
            continue
        local_hits: list[tuple[float, Path]] = []
        for other_path, other_payload in payloads.items():
            if other_path == path:
                continue
            score = jaccard(grams.get(path, set()), grams.get(other_path, set()))
            if score >= PAGE_SIMILARITY_THRESHOLD:
                local_hits.append((score, other_path))
        if local_hits:
            local_hits.sort(reverse=True, key=lambda item: item[0])
            preview = ", ".join(f"{rel(other)} {score:.2f}" for score, other in local_hits[:5])
            hits.append(f"{rel(path)} is too similar to existing payload text ({preview})")

    return hits


def check_section_frame_similarity(payloads: dict[Path, dict], scope: set[Path]) -> list[str]:
    section_units_by_path: dict[Path, dict[str, list[str]]] = {}
    for path, payload in payloads.items():
        section_units_by_path[path] = {
            section_id: meaningful_text_units(segments)
            for section_id, segments in payload_section_segments(payload).items()
        }

    hits: list[str] = []
    total_hits = 0
    for path in sorted(scope):
        if path not in payloads:
            continue
        section_hit_counts: dict[str, int] = {}
        for section_id, units in section_units_by_path.get(path, {}).items():
            if section_id == "hero":
                continue
            if section_hit_counts.get(section_id, 0) >= SECTION_FRAME_MAX_HITS_PER_SECTION:
                continue
            for unit in units:
                if total_hits >= SECTION_FRAME_MAX_HITS_TOTAL:
                    return hits
                for other_path, other_sections in section_units_by_path.items():
                    if other_path == path:
                        continue
                    for other_unit in other_sections.get(section_id, []):
                        score = text_similarity(unit, other_unit)
                        if score < SECTION_FRAME_SIMILARITY_THRESHOLD:
                            continue
                        hits.append(
                            f"{rel(path)} section #{section_id} repeats sentence frame from {rel(other_path)} ({score:.2f}): {unit}"
                        )
                        section_hit_counts[section_id] = section_hit_counts.get(section_id, 0) + 1
                        total_hits += 1
                        break
                    if section_hit_counts.get(section_id, 0) >= SECTION_FRAME_MAX_HITS_PER_SECTION:
                        break
                if section_hit_counts.get(section_id, 0) >= SECTION_FRAME_MAX_HITS_PER_SECTION:
                    break

    return hits


def check_payload_content_quality(errors: list[str], strict_content: bool) -> None:
    repeated: dict[str, set[str]] = {}
    medium_repeated: dict[str, set[str]] = {}
    placeholder_hits: list[str] = []
    stock_phrase_hits: list[str] = []
    generated_formula_hits: list[str] = []
    content_brief_hits: list[str] = []
    page_similarity_hits: list[str] = []
    section_frame_hits: list[str] = []
    payload_count = 0
    payloads = load_payloads_for_quality(errors)

    changed_paths = changed_payload_paths()
    if changed_paths is None:
        errors.append("Cannot determine changed/new payloads for content quality gates; git status command failed")
        changed_scope: set[Path] = set()
    else:
        changed_scope = changed_paths

    if strict_content:
        formula_scope = {path.resolve() for path in PAYLOAD_DIR.glob("*.json")}
        formula_scope_label = "all payloads"
        similarity_scope = formula_scope
        similarity_scope_label = "all payloads"
    else:
        formula_scope = changed_scope
        formula_scope_label = "changed/new payloads"
        similarity_scope = changed_scope
        similarity_scope_label = "changed/new payloads"

    for path in sorted(changed_scope):
        payload = payloads.get(path)
        if payload is not None:
            content_brief_hits.extend(check_content_brief(path, payload))

    if similarity_scope:
        page_similarity_hits = check_page_similarity(payloads, similarity_scope)
        section_frame_hits = check_section_frame_similarity(payloads, similarity_scope)

    for path, payload in sorted(payloads.items(), key=lambda item: rel(item[0])):
        payload_count += 1
        scan_generated_formulas = path.resolve() in formula_scope

        for segment in payload_text_segments(payload):
            for pattern in PLACEHOLDER_TEXT_PATTERNS:
                if pattern.search(segment):
                    placeholder_hits.append(f"{rel(path)}: {segment}")
                    break

            for pattern in STOCK_TEMPLATE_TEXT_PATTERNS:
                if pattern.search(segment):
                    stock_phrase_hits.append(f"{rel(path)}: {segment}")
                    break

            if scan_generated_formulas:
                for pattern in GENERATED_FORMULA_TEXT_PATTERNS:
                    if pattern.search(segment):
                        generated_formula_hits.append(f"{rel(path)}: {segment}")
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
    generated_formula_hits = dedupe_keep_order(generated_formula_hits)
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
    if generated_formula_hits:
        preview = "\n".join(generated_formula_hits[:60])
        if len(generated_formula_hits) > 60:
            preview += "\n..."
        errors.append(
            f"Generated formula leakage found in {formula_scope_label}. These sentence shapes come from batch-template prose; rewrite them with topic-specific pressure, evidence, and examples:\n"
            + preview
        )
    if content_brief_hits:
        preview = "\n".join(content_brief_hits[:60])
        if len(content_brief_hits) > 60:
            preview += "\n..."
        errors.append(
            "Content brief gate failed. New or modified payloads need a topic-specific contentBrief before page prose is accepted:\n"
            + preview
        )
    if page_similarity_hits:
        preview = "\n".join(page_similarity_hits[:30])
        if len(page_similarity_hits) > 30:
            preview += "\n..."
        errors.append(
            f"Cross-page similarity gate failed for {similarity_scope_label}. Rewrite pages whose total text is too close to another payload:\n"
            + preview
        )
    if section_frame_hits:
        preview = "\n".join(section_frame_hits[:30])
        if len(section_frame_hits) > 30:
            preview += "\n..."
        errors.append(
            f"Section sentence-frame gate failed for {similarity_scope_label}. Rewrite repeated sentence shapes inside the named sections:\n"
            + preview
        )
    if duplicate_hits:
        errors.append("Repeated long payload text found:\n" + "\n".join(duplicate_hits[:20]))
    if medium_duplicate_hits:
        errors.append(
            f"Repeated medium-length payload text found (possible house formula; threshold {medium_repeat_threshold} files):\n"
            + "\n".join(medium_duplicate_hits[:20])
        )
    if formula_scope:
        print(f"generated formula scan ({formula_scope_label}): {len(formula_scope)} payload(s)")
    else:
        print("generated formula scan: no changed/new payloads")
    if changed_scope:
        print(f"content brief scan (changed/new payloads): {len(changed_scope)} payload(s)")
    else:
        print("content brief scan: no changed/new payloads")
    if similarity_scope:
        print(f"similarity scan ({similarity_scope_label}): {len(similarity_scope)} payload(s)")
    else:
        print("similarity scan: no changed/new payloads")

    if (
        not placeholder_hits
        and not stock_phrase_hits
        and not generated_formula_hits
        and not content_brief_hits
        and not page_similarity_hits
        and not section_frame_hits
        and not duplicate_hits
        and not medium_duplicate_hits
    ):
        print("payload content quality: ok")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Concept Reading Lab structure, sync, and content quality.")
    parser.add_argument(
        "--strict-content",
        action="store_true",
        help="Scan all payloads for generated-formula leakage instead of only changed/new payloads.",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    check_js_parse(errors)
    check_render_sync(errors)
    check_html_structure(errors)
    check_forbidden_styles(errors)
    check_payload_topic_alignment(errors)
    check_payload_content_quality(errors, strict_content=args.strict_content)

    if errors:
        print("\nValidation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nconcept lab validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
