"""Python DevOps script 1: fail early if incoming training data is invalid."""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "tickets.csv"
ALLOWED = {"billing", "login", "technical"}


def read_dataset():
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not {"text", "category"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires text and category columns")
        rows = list(reader)

    if len(rows) < 15:
        raise ValueError("Expected at least 15 labeled examples")

    counts = Counter()
    seen = set()
    for index, row in enumerate(rows, start=2):
        text = row["text"].strip()
        category = row["category"].strip()
        if len(text) < 10 or category not in ALLOWED:
            raise ValueError(f"Invalid training example at CSV line {index}")
        if text.casefold() in seen:
            raise ValueError(f"Duplicate ticket text at CSV line {index}")
        seen.add(text.casefold())
        counts[category] += 1

    if any(counts[category] < 5 for category in ALLOWED):
        raise ValueError("Each category needs at least five examples")

    return rows, counts


if __name__ == "__main__":
    rows, counts = read_dataset()
    print(f"DATA OK: {len(rows)} rows; counts={dict(counts)}")
