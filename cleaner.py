import html
import json
import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional


def _clean_text(text: Any) -> str:
    """
    Normalise textual fields by:
      - Converting to string
      - Normalising Unicode encoding
      - Unescaping HTML entities
      - Stripping HTML tags
      - Collapsing extra whitespace
    """
    if text is None:
        return ""

    t = str(text)
    # Normalise text encoding / Unicode representation
    t = unicodedata.normalize("NFKC", t)
    # Decode HTML entities like &amp;
    t = html.unescape(t)
    # Remove simple HTML tags
    t = re.sub(r"<[^>]+>", " ", t)
    # Collapse whitespace and trim
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _parse_price(raw: Any) -> Optional[float]:
    """
    Accepts values like:
      - "USD 10.50"
      - "$10.50"
      - "10.50"
      - 10.5
    Returns a float or None if not parseable.
    """
    if raw is None:
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    if not isinstance(raw, str):
        return None

    text = raw.strip()
    # Remove common currency markers
    text = re.sub(r"(?i)\b[a-z]{3}\b", "", text)  # remove currency codes like USD
    text = text.replace("$", "").strip()

    m = re.search(r"-?\d+(\.\d+)?", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _parse_iso_date(raw: Any) -> Optional[str]:
    """
    Try to coerce common date formats to ISO-8601 (YYYY-MM-DD).
    """
    if raw is None:
        return None

    if isinstance(raw, datetime):
        return raw.date().isoformat()

    if not isinstance(raw, str):
        return None

    text = raw.strip()
    # Try a few simple patterns
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    # Fallback: if it already looks like ISO, keep it
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text
    return None


def clean_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single raw scraped record into a normalised structure.

    Expected raw fields (flexible / noisy):
      - "title" (string, may have extra whitespace)
      - "description" (string, may have HTML / line breaks)
      - "price" (string / number with currency symbols)
      - "currency" (string, optional, e.g. "USD")
      - "url" (string, possibly with surrounding spaces)
      - "scraped_at" (string date in various simple formats)
    """
    # Support both "content" (preferred) and "description" (legacy scraped field)
    title = raw.get("title") or ""
    content = raw.get("content") or raw.get("description") or ""

    cleaned: Dict[str, Any] = {
        "id": str(raw.get("id") or "").strip() or None,
        "title": _clean_text(title),
        "content": _clean_text(content),
        "price": _parse_price(raw.get("price")),
        "currency": (str(raw.get("currency")).strip().upper() or None)
        if raw.get("currency") is not None
        else None,
        "url": (str(raw.get("url") or "").strip() or None),
        "scraped_at": _parse_iso_date(raw.get("scraped_at")),
    }
    return cleaned


def clean_dataset(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply `clean_record` to an entire dataset.
    """
    return [clean_record(r) for r in records]


def main(input_path: str, output_path: str) -> None:
    """
    Simple CLI entry point:
      python cleaner.py sample_data.json cleaned_output.json
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON array of records")

    cleaned = clean_dataset(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean raw scraped JSON data into a normalised structure."
    )
    parser.add_argument("input", help="Path to raw JSON input (array of records)")
    parser.add_argument("output", help="Path to write cleaned JSON output")

    args = parser.parse_args()
    main(args.input, args.output)

