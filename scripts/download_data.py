"""Download the public TensorFlow mirror of the ULB/Kaggle dataset."""

from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv"
KAGGLE = "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
REFERENCE = "https://www.tensorflow.org/tutorials/structured_data/imbalanced_data"
EXPECTED_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount", "Class"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="Validate an existing Kaggle CSV instead of downloading")
    args = parser.parse_args()
    destination = args.file.resolve() if args.file else ROOT / "data" / "creditcard.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        if args.file:
            raise FileNotFoundError(destination)
        temporary = destination.with_suffix(".csv.part")
        print(f"Downloading public dataset from {SOURCE}", flush=True)
        with urllib.request.urlopen(SOURCE, timeout=120) as response, temporary.open("wb") as handle:
            total = 0
            previous = 0
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
                total += len(chunk)
                if total - previous >= 20 * 1024 * 1024:
                    print(f"Downloaded {total / 1024**2:.0f} MiB", flush=True)
                    previous = total
        temporary.replace(destination)
    with destination.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    counts = {0: 0, 1: 0}
    with destination.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError("Unexpected dataset schema; expected the original ULB creditcard.csv")
        for row in reader:
            counts[int(row["Class"])] += 1
    if counts != {0: 284315, 1: 492}:
        raise ValueError(f"Unexpected original dataset class counts: {counts}")
    metadata = {
        "dataset": "ULB / Worldline Credit Card Fraud Detection",
        "canonical_source": KAGGLE,
        "download_url": None if args.file else SOURCE,
        "mirror_reference": REFERENCE,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": digest,
        "bytes": destination.stat().st_size,
        "rows": sum(counts.values()),
        "legitimate": counts[0],
        "fraud": counts[1],
        "columns": EXPECTED_COLUMNS,
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "dataset_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in metadata.items() if key != "columns"}, indent=2))


if __name__ == "__main__":
    main()
