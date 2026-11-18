# Evidence guide

The evidence images were exported from the actual outputs of the fully executed `AI_Fraud_Detection.ipynb`. Each code cell has a recorded execution count, retained output and timing entry. No metrics or notebook interface was fabricated.

**Capture limitation:** These PNG files are notebook-output exports, not operating-system or browser screenshots. Computer Use stopped because it could not determine the current browser URL with enough confidence to enforce policy. The required filenames are retained under `screenshots/`, with an explicit output-export label on every image. Live Jupyter screenshots remain a manual evidence step if a course or assessor specifically requires browser chrome.

| Evidence file | Cell | Content |
| --- | --- | --- |
| `00-import-libraries.png` | 1 | Actual library versions and fixed threshold |
| `01-baseline-traffic.png` | 2 | Original transaction counts and baseline chart |
| `05-data-preprocessing.png` | 3 | Deduplication, split sizes and zero-overlap checks |
| `02-smote-balancing.png` | 4 | Original and resampled training counts and chart |
| `06-engine-trained.png` | 5 | Successful 100-tree training, elapsed time and saved artifact |
| `03-confusion-matrix.png` | 6 | Actual holdout confusion matrix |
| `04-detection-report.png` | 6 | Actual precision, recall, F1 and support |
| `07-high-severity-alert.png` | 6 | Actual HIGH review alert from the benchmark replay |

The plot images are decoded from the notebook's saved `image/png` outputs. Text is taken directly from saved stream outputs and rasterized into a labeled evidence panel. A plot can be resized to fit the panel; values and chart content are preserved. Standalone high-resolution figure exports are additionally available in `reports/figures/`.

## Reproduce and verify

From the project root in its configured Python environment:

```cmd
python scripts/run_notebook.py
python scripts/export_evidence.py
python scripts/verify_project.py
```

`reports/evidence_manifest.json` binds each PNG to its notebook cell ID, execution count, creation time, dimensions and SHA-256. It also records the executed notebook's hash and dataset hash. `reports/execution_log.json` records the six execution stages; `reports/verification.json` records reproducibility checks. These hashes support consistency checks; they are not third-party attestation.

## Capture live Jupyter screenshots if required

1. Run `python -m jupyterlab AI_Fraud_Detection.ipynb` in the configured environment.
2. Open the completed notebook and inspect each cell's saved output. To rerun, use **Run > Run All Cells** and wait until all six have completed.
3. Capture each output with the operating system's screenshot tool. For Cell 6, capture the matrix, detection report and alert separately so values remain readable.
4. Save live screenshots in a separate `screenshots/live/` folder so the original hashed output-export evidence is preserved. Label the capture method and time accurately.

For an inspection without a running kernel, open `reports/AI_Fraud_Detection.html` in a browser. It is an HTML export of the executed notebook, with the code and original outputs intact.
