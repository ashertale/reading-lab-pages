from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import validate_concept_lab as validator


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = ROOT / "data" / "concept-payloads"
REPORT_DIR = ROOT / ".superpowers" / "concept-audits"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_payloads() -> dict[Path, dict]:
    payloads: dict[Path, dict] = {}
    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        payloads[path.resolve()] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def formula_hits_by_path(payloads: dict[Path, dict]) -> dict[Path, list[str]]:
    hits: dict[Path, list[str]] = defaultdict(list)
    for path, payload in payloads.items():
        for segment in validator.payload_text_segments(payload):
            for pattern in validator.GENERATED_FORMULA_TEXT_PATTERNS:
                if pattern.search(segment):
                    hits[path].append(segment)
                    break
    return hits


def page_similarity_by_path(payloads: dict[Path, dict], threshold: float) -> dict[Path, list[dict]]:
    texts = {path: validator.page_similarity_text(payload) for path, payload in payloads.items()}
    grams = {path: validator.char_ngrams(text, n=4) for path, text in texts.items()}
    hits: dict[Path, list[dict]] = defaultdict(list)
    paths = sorted(payloads)
    for index, left in enumerate(paths):
        for right in paths[index + 1 :]:
            score = validator.jaccard(grams.get(left, set()), grams.get(right, set()))
            if score < threshold:
                continue
            hits[left].append({"path": rel(right), "score": round(score, 3)})
            hits[right].append({"path": rel(left), "score": round(score, 3)})
    for path in hits:
        hits[path].sort(key=lambda item: item["score"], reverse=True)
    return hits


def section_frame_hits_by_path(payloads: dict[Path, dict]) -> dict[Path, list[dict]]:
    units_by_path: dict[Path, dict[str, list[str]]] = {}
    for path, payload in payloads.items():
        units_by_path[path] = {
            section_id: validator.meaningful_text_units(segments)
            for section_id, segments in validator.payload_section_segments(payload).items()
        }

    index_by_section: dict[str, list[tuple[Path, str, set[str]]]] = defaultdict(list)
    for path, sections in units_by_path.items():
        for section_id, units in sections.items():
            if section_id == "hero":
                continue
            for unit in units:
                index_by_section[section_id].append((path, unit, validator.char_ngrams(unit, n=3)))

    hits: dict[Path, list[dict]] = defaultdict(list)
    for left in sorted(payloads):
        for section_id, units in units_by_path[left].items():
            if section_id == "hero":
                continue
            section_hits = 0
            for unit in units:
                unit_grams = validator.char_ngrams(unit, n=3)
                for right, other_unit, other_grams in index_by_section.get(section_id, []):
                    if right == left:
                        continue
                    if validator.jaccard(unit_grams, other_grams) < validator.SECTION_FRAME_JACCARD_GATE:
                        continue
                    score = validator.text_similarity(unit, other_unit)
                    if score < validator.SECTION_FRAME_SIMILARITY_THRESHOLD:
                        continue
                    hits[left].append(
                        {
                            "section": section_id,
                            "path": rel(right),
                            "score": round(score, 3),
                            "text": unit,
                        }
                    )
                    section_hits += 1
                    break
                if section_hits >= validator.SECTION_FRAME_MAX_HITS_PER_SECTION:
                    break
    return hits


def page_family(path: Path, payload: dict) -> str:
    page_type = payload.get("indexEntry", {}).get("type", "")
    if "心理" in page_type or "偏誤" in page_type:
        return "psychology"
    if "工程" in page_type or "系統" in page_type or "可靠" in page_type:
        return "engineering_systems"
    if "悖論" in page_type or "哲學" in page_type:
        return "paradox_philosophy"
    if "原則" in page_type or "判斷" in page_type:
        return "principle"
    return "other"


def build_report(payloads: dict[Path, dict], similarity_threshold: float) -> dict:
    formulas = formula_hits_by_path(payloads)
    similarities = page_similarity_by_path(payloads, threshold=similarity_threshold)
    section_frames = section_frame_hits_by_path(payloads)

    pages = []
    for path, payload in payloads.items():
        formula_count = len(formulas.get(path, []))
        similarity_count = len(similarities.get(path, []))
        section_frame_count = len(section_frames.get(path, []))
        score = formula_count * 4 + section_frame_count * 2 + similarity_count
        pages.append(
            {
                "path": rel(path),
                "slug": path.stem,
                "title": payload.get("indexEntry", {}).get("title", path.stem),
                "family": page_family(path, payload),
                "severity": score,
                "formulaCount": formula_count,
                "pageSimilarityCount": similarity_count,
                "sectionFrameCount": section_frame_count,
                "formulaExamples": formulas.get(path, [])[:5],
                "similarPages": similarities.get(path, [])[:5],
                "sectionFrameExamples": section_frames.get(path, [])[:5],
            }
        )
    pages.sort(key=lambda item: (item["severity"], item["formulaCount"], item["sectionFrameCount"]), reverse=True)

    family_counts = Counter(page["family"] for page in pages)
    issue_counts = {
        "pages": len(pages),
        "withFormula": sum(1 for page in pages if page["formulaCount"]),
        "withPageSimilarity": sum(1 for page in pages if page["pageSimilarityCount"]),
        "withSectionFrame": sum(1 for page in pages if page["sectionFrameCount"]),
    }
    return {
        "summary": {
            "similarityThreshold": similarity_threshold,
            "issueCounts": issue_counts,
            "familyCounts": dict(family_counts),
        },
        "pages": pages,
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# Concept Content Audit",
        "",
        "## Summary",
        "",
        f"- Pages audited: {report['summary']['issueCounts']['pages']}",
        f"- Pages with generated formula hits: {report['summary']['issueCounts']['withFormula']}",
        f"- Pages with page-level similarity hits: {report['summary']['issueCounts']['withPageSimilarity']}",
        f"- Pages with section sentence-frame hits: {report['summary']['issueCounts']['withSectionFrame']}",
        f"- Similarity threshold: {report['summary']['similarityThreshold']}",
        "",
        "## Highest Priority",
        "",
    ]
    for page in report["pages"][:40]:
        lines.extend(
            [
                f"### {page['title']} (`{page['slug']}`)",
                "",
                f"- Path: `{page['path']}`",
                f"- Severity: {page['severity']}",
                f"- Formula hits: {page['formulaCount']}",
                f"- Similar pages: {page['pageSimilarityCount']}",
                f"- Section frame hits: {page['sectionFrameCount']}",
            ]
        )
        if page["formulaExamples"]:
            lines.append("- Formula examples:")
            for item in page["formulaExamples"][:3]:
                lines.append(f"  - {item}")
        if page["similarPages"]:
            lines.append("- Similar pages:")
            for item in page["similarPages"][:3]:
                lines.append(f"  - `{item['path']}` ({item['score']})")
        if page["sectionFrameExamples"]:
            lines.append("- Section frame examples:")
            for item in page["sectionFrameExamples"][:2]:
                lines.append(f"  - `{item['section']}` vs `{item['path']}` ({item['score']}): {item['text']}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Concept Reading Lab payload content quality.")
    parser.add_argument("--similarity-threshold", type=float, default=validator.PAGE_SIMILARITY_THRESHOLD)
    args = parser.parse_args()

    payloads = load_payloads()
    report = build_report(payloads, similarity_threshold=args.similarity_threshold)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "concept-content-audit.json"
    md_path = REPORT_DIR / "concept-content-audit.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, md_path)

    print(f"audited {report['summary']['issueCounts']['pages']} pages")
    print(f"formula pages: {report['summary']['issueCounts']['withFormula']}")
    print(f"similarity pages: {report['summary']['issueCounts']['withPageSimilarity']}")
    print(f"section-frame pages: {report['summary']['issueCounts']['withSectionFrame']}")
    print(json_path.relative_to(ROOT).as_posix())
    print(md_path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
