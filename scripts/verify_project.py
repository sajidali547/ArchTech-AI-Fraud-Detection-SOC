"""Recompute the holdout decisions from the saved model and verify evidence."""

from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

import joblib
import nbformat
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fraud_engine import score_transactions, transform_transactions, FEATURE_COLUMNS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-evidence", action="store_true", help="Check model before UI captures exist")
    args = parser.parse_args()
    checks = []

    def passed(name):
        checks.append(name)
        print("PASS:", name, flush=True)

    metrics = json.loads((ROOT / "reports/metrics.json").read_text())
    provenance = json.loads((ROOT / "reports/dataset_provenance.json").read_text())
    with (ROOT / "data/creditcard.csv").open("rb") as handle:
        sha = hashlib.file_digest(handle, "sha256").hexdigest()
    assert sha == metrics["dataset_sha256"] == provenance["sha256"]
    passed("Dataset hash matches training metrics and provenance")
    clean = pd.read_csv(ROOT / "data/creditcard.csv").drop_duplicates()
    x = clean.drop(columns="Class")
    y = clean["Class"]
    train, test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    assert not (set(pd.util.hash_pandas_object(train, index=False)) &
                set(pd.util.hash_pandas_object(test, index=False)))
    passed("No repeated transaction features cross the train/test boundary")
    bundle = joblib.load(ROOT / "models/fraud_engine.joblib")
    np.testing.assert_allclose(bundle["scaler"].mean_, train[["Amount", "Time"]].mean().to_numpy())
    assert bundle["scaler"].n_samples_seen_ == len(train)
    passed("Saved scaler was fitted on the training partition only")
    saved = pd.read_csv(ROOT / "reports/test_predictions.csv")
    np.testing.assert_array_equal(saved.source_row, test.index)
    np.testing.assert_array_equal(saved.actual_class, y_test)
    scores = bundle["model"].predict_proba(transform_transactions(test, bundle["scaler"]))[:, 1]
    predicted = (scores >= bundle["threshold"]).astype(int)
    np.testing.assert_allclose(scores, saved.fraud_score, atol=1e-12, rtol=0)
    np.testing.assert_array_equal(predicted, saved.predicted_class)
    passed("Reloaded model reproduces every saved holdout score and decision")
    tn, fp, fn, tp = map(int, confusion_matrix(y_test, predicted, labels=[0, 1]).ravel())
    ev = metrics["evaluation"]
    assert [tn, fp, fn, tp] == [ev[key] for key in ["tn", "fp", "fn", "tp"]]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predicted, average="binary")
    np.testing.assert_allclose([precision, recall, f1, tn/(tn+fp)],
                              [ev["fraud_precision"], ev["fraud_recall"], ev["fraud_f1"], ev["specificity"]])
    passed("Confusion matrix, fraud precision, recall, F1 and specificity match predictions")
    alerts = [json.loads(line) for line in (ROOT / "reports/high_severity_alerts.jsonl").read_text().splitlines()]
    expected_ids = {f"ulb-row-{i}" for i in test.index[predicted == 1]}
    assert len(alerts) == tp + fp == len(expected_ids)
    assert {a["transaction_id"] for a in alerts} == expected_ids
    assert all(a["severity"] == "HIGH" and a["score"] >= bundle["threshold"]
               and a["action"] == "analyst_review" for a in alerts)
    quiet = test.loc[predicted == 0].head(100)
    assert score_transactions(quiet, bundle) == []
    assert not any("Class" in a or "actual_class" in a or "card_number" in a for a in alerts)
    passed("Only threshold crossings emit HIGH review alerts; low-score traffic stays quiet")
    for invalid in [test.head(1).drop(columns="V1"), test.head(1).assign(Class=1),
                    test.head(1).assign(V1=np.nan)]:
        try:
            score_transactions(invalid, bundle)
        except ValueError:
            continue
        raise AssertionError("Invalid or label-bearing inputs were accepted")
    passed("Missing features, labels and non-finite inputs are rejected")
    notebook = nbformat.read(ROOT / "AI_Fraud_Detection.ipynb", as_version=4)
    nbformat.validate(notebook)
    codes = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert len(codes) == 6 and [c.execution_count for c in codes] == list(range(1, 7))
    assert all(c.outputs and all(out.output_type != "error" for out in c.outputs) for c in codes)
    execution = json.loads((ROOT / "reports/execution_log.json").read_text())
    assert execution["status"] == "success" and len(execution["cells"]) == 6
    passed("All six notebook cells executed successfully and retain real outputs")
    for ignored in ["data/creditcard.csv", "models/fraud_engine.joblib"]:
        result = subprocess.run(["git", "check-ignore", ignored], cwd=ROOT, capture_output=True)
        assert result.returncode == 0
    tracked = subprocess.run(["git", "ls-files", "data/", "models/"], cwd=ROOT, text=True, capture_output=True, check=True)
    assert not tracked.stdout.strip()
    passed("Dataset and model are ignored and not tracked by Git")
    if not args.skip_evidence:
        manifest = json.loads((ROOT / "reports/evidence_manifest.json").read_text())
        assert manifest["notebook_sha256"] == hashlib.sha256((ROOT / "AI_Fraud_Detection.ipynb").read_bytes()).hexdigest()
        assert manifest["dataset_sha256"] == sha
        expected = {"00-import-libraries.png", "01-baseline-traffic.png", "02-smote-balancing.png",
                    "03-confusion-matrix.png", "04-detection-report.png", "05-data-preprocessing.png",
                    "06-engine-trained.png", "07-high-severity-alert.png"}
        assert expected.issubset({Path(item["path"]).name for item in manifest["captures"]})
        for item in manifest["captures"]:
            path = ROOT / item["path"]
            assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
            assert path.stat().st_size > 20000
        passed("All eight notebook-output evidence exports match the notebook and SHA-256 manifest")
    result = {"status": "passed", "verified_at_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_checked": not args.skip_evidence, "checks": checks,
              "confusion_matrix": [[tn, fp], [fn, tp]]}
    (ROOT / "reports/verification.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
