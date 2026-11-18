"""Execute all six notebook cells, checkpoint their outputs and export HTML."""

from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "AI_Fraud_Detection.ipynb"


def main():
    subprocess.run([sys.executable, "-m", "ipykernel", "install", "--prefix", sys.prefix,
                    "--name", "arch-fraud", "--display-name", "Python (Arch Fraud SOC)"], check=True)
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    log = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "cells": []}
    started = {}

    def on_start(cell, cell_index, **kwargs):
        if cell.cell_type == "code":
            started[cell_index] = time.perf_counter()
            print(f"Starting {cell.metadata.get('stage', cell_index)}", flush=True)

    def on_done(cell, cell_index, **kwargs):
        if cell.cell_type == "code":
            elapsed = time.perf_counter() - started[cell_index]
            log["cells"].append({"stage": cell.metadata.get("stage"),
                                  "execution_count": cell.execution_count,
                                  "seconds": round(elapsed, 3),
                                  "completed_at_utc": datetime.now(timezone.utc).isoformat()})
            NOTEBOOK.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")
            (ROOT / "reports" / "execution_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
            print(f"Completed {cell.metadata.get('stage')} in {elapsed:.1f}s", flush=True)

    client = NotebookClient(notebook, timeout=1800, kernel_name="arch-fraud",
                            resources={"metadata": {"path": str(ROOT)}},
                            on_cell_start=on_start, on_cell_executed=on_done)
    client.execute()
    NOTEBOOK.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")
    log["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    log["status"] = "success"
    (ROOT / "reports" / "execution_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    exporter = HTMLExporter(template_name="lab")
    html, _ = exporter.from_notebook_node(notebook)
    (ROOT / "reports" / "AI_Fraud_Detection.html").write_text(html, encoding="utf-8")
    print("All six cells executed; notebook and HTML saved.", flush=True)


if __name__ == "__main__":
    main()
