"""Export authentic executed-cell text and PNG outputs; no browser UI is fabricated."""

from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
from io import BytesIO
import json
import textwrap

from matplotlib import font_manager
import nbformat
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "AI_Fraud_Detection.ipynb"


def main():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    stages = {cell.metadata["stage"]: cell for cell in notebook.cells if cell.cell_type == "code"}
    if len(stages) != 6 or any(cell.execution_count is None for cell in stages.values()):
        raise ValueError("Execute the entire notebook before exporting evidence")
    if any(output.output_type == "error" for cell in stages.values() for output in cell.outputs):
        raise ValueError("Notebook has an execution error")
    screenshots = ROOT / "screenshots"
    screenshots.mkdir(exist_ok=True)
    sans = font_manager.findfont("DejaVu Sans")
    mono = font_manager.findfont("DejaVu Sans Mono")
    title_font = ImageFont.truetype(sans, 28)
    body_font = ImageFont.truetype(mono, 21)
    small_font = ImageFont.truetype(sans, 17)
    captures = []
    timestamp = datetime.now(timezone.utc).isoformat()

    def streams(cell):
        return "".join(output.get("text", "") for output in cell.outputs if output.output_type == "stream")

    def images(cell):
        return [base64.b64decode(output["data"]["image/png"])
                for output in cell.outputs if "image/png" in output.get("data", {})]

    def export(filename, stage, title, text="", png=None):
        cell = stages[stage]
        width, margin, leading = 1200, 44, 31
        lines = []
        for line in text.strip().splitlines():
            lines.extend(textwrap.wrap(line, width=85, replace_whitespace=False,
                                       drop_whitespace=False) or [""])
        graphic = None
        if png:
            raw = Image.open(BytesIO(png)).convert("RGBA")
            graphic = Image.new("RGB", raw.size, "white")
            graphic.paste(raw, mask=raw.getchannel("A"))
            scale = min((width-2*margin)/graphic.width, 1.55)
            graphic = graphic.resize((round(graphic.width*scale), round(graphic.height*scale)), Image.Resampling.LANCZOS)
        graphic_height = graphic.height + 24 if graphic else 0
        height = max(330, 146 + leading*len(lines) + graphic_height + 78)
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, width, 8), fill="#15657a")
        draw.text((margin, 28), title, font=title_font, fill="#173341")
        draw.text((margin, 73), f"Arch Store SOC lab  |  Executed notebook cell [{cell.execution_count}]  |  Output export",
                  font=small_font, fill="#55646c")
        draw.line((margin, 110, width-margin, 110), fill="#d9e1e6", width=2)
        y = 131
        for line in lines:
            draw.text((margin, y), line, font=body_font, fill="#152530")
            y += leading
        if graphic:
            canvas.paste(graphic, ((width-graphic.width)//2, y+12))
        draw.text((margin, height-51), "Source: AI_Fraud_Detection.ipynb | Actual saved outputs; no browser frame",
                  font=small_font, fill="#55646c")
        path = screenshots / filename
        canvas.save(path)
        captures.append({"path": path.relative_to(ROOT).as_posix(), "stage": stage,
                         "execution_count": cell.execution_count, "notebook_cell_id": cell.id,
                         "kind": "executed_notebook_output_export", "created_at_utc": timestamp,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "bytes": path.stat().st_size, "width": width, "height": height})

    export("00-import-libraries.png", "1-imports", "Cell 1 — Libraries and fixed alert policy", streams(stages["1-imports"]))
    export("01-baseline-traffic.png", "2-baseline", "Cell 2 — Baseline transaction traffic",
           streams(stages["2-baseline"]), images(stages["2-baseline"])[0])
    export("05-data-preprocessing.png", "3-preprocessing", "Cell 3 — Preprocessing and leakage checks", streams(stages["3-preprocessing"]))
    export("02-smote-balancing.png", "4-smote", "Cell 4 — Training-only SMOTE balancing",
           streams(stages["4-smote"]), images(stages["4-smote"])[0])
    export("06-engine-trained.png", "5-training", "Cell 5 — Detection engine trained", streams(stages["5-training"]))
    evaluation = stages["6-evaluation"]
    export("03-confusion-matrix.png", "6-evaluation", "Cell 6 — SOC confusion matrix", png=images(evaluation)[0])
    export("04-detection-report.png", "6-evaluation", "Cell 6 — Fraud precision, recall and F1", png=images(evaluation)[1])
    alert_text = streams(evaluation).split("Sample HIGH analyst-review alert (benchmark replay):", 1)[1]
    export("07-high-severity-alert.png", "6-evaluation", "Cell 6 — HIGH alert from benchmark replay", alert_text)
    metrics = json.loads((ROOT / "reports/metrics.json").read_text())
    manifest = {"created_at_utc": timestamp,
                "method": "Direct PNG output extraction and faithful stream-text rasterization",
                "browser_screenshots_captured": False,
                "browser_capture_limitation": "Computer Use stopped because it could not verify the current browser URL with sufficient confidence.",
                "notebook_sha256": hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest(),
                "dataset_sha256": metrics["dataset_sha256"], "captures": captures}
    (ROOT / "reports/evidence_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"Exported {len(captures)} authentic notebook-output evidence images")


if __name__ == "__main__":
    main()
