import json
from collections import Counter
from typing import Any, Dict, List, Tuple


RuleViolation = Dict[str, Any]


# Assignment requirements:
# - Required fields: title, content, url
REQUIRED_FIELDS = ["title", "content", "url"]

# Minimum length for the "content" field (after cleaning)
MIN_CONTENT_LENGTH = 30


def validate_record(record: Dict[str, Any]) -> List[RuleViolation]:
    """
    Validate a single cleaned record.

    Assumes the record has already been passed through `cleaner.clean_record`.
    """
    violations: List[RuleViolation] = []

    # Required fields
    for field in REQUIRED_FIELDS:
        value = record.get(field)
        if value in (None, "", []):
            violations.append(
                {
                    "field": field,
                    "type": "missing_required",
                    "message": f"Required field '{field}' is missing or empty.",
                }
            )

    # Content length minimums
    content = record.get("content") or ""
    if isinstance(content, str) and len(content.strip()) < MIN_CONTENT_LENGTH:
        violations.append(
            {
                "field": "content",
                "type": "too_short",
                "message": f"Content must be at least {MIN_CONTENT_LENGTH} characters long.",
            }
        )

    # URL must look roughly valid
    url = record.get("url")
    if url is not None and isinstance(url, str):
        if not (url.startswith("http://") or url.startswith("https://")):
            violations.append(
                {
                    "field": "url",
                    "type": "invalid_format",
                    "message": "URL should start with http:// or https://.",
                }
            )

    # scraped_at should be ISO-8601 date if present
    scraped_at = record.get("scraped_at")
    if scraped_at is not None:
        if not isinstance(scraped_at, str) or len(scraped_at.split("-")) != 3:
            violations.append(
                {
                    "field": "scraped_at",
                    "type": "invalid_format",
                    "message": "scraped_at should be an ISO-8601 date (YYYY-MM-DD).",
                }
            )

    return violations


def validate_dataset(records: List[Dict[str, Any]]) -> Tuple[List[List[RuleViolation]], Dict[str, Any]]:
    """
    Validate a list of cleaned records and compute simple quality stats.

    Returns:
      - per_record_violations: list of violations per record
      - summary: aggregate stats for quality_report.txt
    """
    all_violations: List[List[RuleViolation]] = []

    for record in records:
        all_violations.append(validate_record(record))

    total_records = len(records)
    total_violations = sum(len(v) for v in all_violations)
    records_with_violations = sum(1 for v in all_violations if v)

    # Completeness percentage per field (including common fields in this dataset)
    fields_for_completeness = ["id", "title", "content", "price", "currency", "url", "scraped_at"]
    field_completeness: Dict[str, float] = {}
    if total_records > 0:
        for field in fields_for_completeness:
            non_empty = sum(
                1
                for r in records
                if r.get(field) not in (None, "", [])
            )
            field_completeness[field] = round(100.0 * non_empty / total_records, 1)

    # Common validation failures
    failure_counter: Counter = Counter()
    for rec_violations in all_violations:
        for v in rec_violations:
            key = (v.get("field", "?"), v.get("type", "violation"))
            failure_counter[key] += 1

    summary = {
        "total_records": total_records,
        "total_violations": total_violations,
        "records_with_violations": records_with_violations,
        "records_without_violations": total_records - records_with_violations,
        "field_completeness": field_completeness,
        "failure_counts": failure_counter,
    }
    return all_violations, summary


def generate_quality_report(
    records: List[Dict[str, Any]],
    per_record_violations: List[List[RuleViolation]],
    summary: Dict[str, Any],
) -> str:
    """
    Generate a human-readable textual quality report.
    """
    lines: List[str] = []
    lines.append("DATA QUALITY REPORT")
    lines.append("===================")
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-------")
    lines.append(f"Total records: {summary['total_records']}")
    lines.append(f"Valid records: {summary['records_without_violations']}")
    lines.append(f"Invalid records: {summary['records_with_violations']}")
    lines.append(f"Total individual violations: {summary['total_violations']}")
    lines.append("")
    lines.append("COMPLETENESS (per field, % non-empty)")
    lines.append("-------------------------------------")
    for field, pct in summary.get("field_completeness", {}).items():
        lines.append(f"- {field}: {pct}%")
    lines.append("")
    lines.append("COMMON VALIDATION FAILURES")
    lines.append("--------------------------")
    failure_counts = summary.get("failure_counts", {})
    if failure_counts:
        # Show up to top 5 most frequent failures
        for (field, vtype), count in failure_counts.most_common(5):
            lines.append(f"- {field} / {vtype}: {count} occurrences")
    else:
        lines.append("No validation failures.")
    lines.append("")
    lines.append("DETAILS (per record)")
    lines.append("---------------------")

    for idx, (record, violations) in enumerate(zip(records, per_record_violations), start=1):
        record_id = record.get("id") or f"# {idx}"
        lines.append(f"Record {idx} (id={record_id})")
        if not violations:
            lines.append("  OK")
        else:
            for v in violations:
                field = v.get("field", "?")
                vtype = v.get("type", "violation")
                msg = v.get("message", "")
                lines.append(f"  - [{field}] {vtype}: {msg}")
        lines.append("")

    return "\n".join(lines)


def main(input_path: str, report_path: str) -> None:
    """
    CLI entry point for validating cleaned JSON and writing a report.

      python validator.py cleaned_output.json quality_report.txt
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON array of cleaned records")

    per_record_violations, summary = validate_dataset(data)
    report = generate_quality_report(data, per_record_violations, summary)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate cleaned JSON data and write a quality report."
    )
    parser.add_argument("input", help="Path to cleaned JSON input")
    parser.add_argument("report", help="Path to write quality report text file")

    args = parser.parse_args()
    main(args.input, args.report)

