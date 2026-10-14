"""A product recipe for the shared UIA engine, not a copied control engine."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys


def recipe(pid, preview_visible=False):
    def wait(identifier, selector):
        return {"id": identifier, "action": "wait", "selector": selector, "state": "visible", "risk": "read_only"}
    def keys(identifier, selector, value, risk="app_state"):
        return {"id": identifier, "action": "type_keys", "selector": selector, "value": value, "risk": risk}
    def text(identifier, selector, value, risk="app_state"):
        return {"id": identifier, "action": "set_text", "selector": selector, "value": value, "risk": risk}
    browse, save = {"title": "파일 찾기"}, {"title": "DXF 저장"}
    opening, saving = {"auto_id": "1148", "control_type": "Edit"}, {"auto_id": "1001", "control_type": "Edit"}
    return {"schema_version": 1, "id": "issue20-keyboard-20-labels",
            "target": {"backend": "uia", "process_id": pid, "title_re": "^Excel CAD Label Maker.*"},
            "limits": {"run_timeout_seconds": 60, "action_timeout_seconds": 12, "poll_interval_seconds": .1, "max_actions": 20},
            "steps": [wait("ready", browse), keys("ctrl-o", browse, "^o"), wait("open-dialog", opening),
                      text("input-name", opening, "${INPUT}"), keys("open-enter", opening, "{ENTER}"),
                      wait("analyzed", {"title_re": "^라벨 20개, 총 60칸, 확인 0건.*"}),
                      *([] if preview_visible else [keys("preview-tab", save, "^{TAB}")]), wait("preview-visible", {"title": "도면"}),
                      keys("ctrl-s", save, "^s"), wait("save-dialog", saving),
                      text("output-name", saving, "${OUTPUT}", "data_mutation"), keys("save-enter", saving, "{ENTER}", "data_mutation"),
                      wait("saved", {"title_re": "^저장 완료: 20개 라벨, 60칸.*"}),
                      {"id": "screen", "action": "capture", "scope": "main", "risk": "read_only", "name": "screen.png"},
                      {"id": "tree", "action": "dump_tree", "scope": "main", "risk": "read_only", "name": "tree.json"}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--toolkit", required=True)
    args = parser.parse_args()
    from pywinauto import Desktop
    Desktop(backend="uia").window(process=args.pid, title_re="^Excel CAD Label Maker.*").wait("exists visible", timeout=10)
    windows = Desktop(backend="uia").windows(process=args.pid, title_re="^Excel CAD Label Maker.*")
    if len(windows) != 1:
        raise SystemExit("정확한 앱 창 하나가 필요합니다.")
    canvases = windows[0].descendants(title="도면")
    if len(canvases) > 1:
        raise SystemExit("도면 컨트롤이 여러 개라 대상이 불명확합니다.")
    report = Path(args.report_dir).resolve()
    profile = report.with_name(report.name + ".profile.json")
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_text(json.dumps(recipe(args.pid, bool(canvases) and canvases[0].is_visible()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    engine = Path(args.toolkit).resolve() / "scripts/windows_uia_qc.py"
    command = [sys.executable, "-B", str(engine), "run", "--profile", str(profile), "--report-dir", str(report),
               "--var", "INPUT=" + str(Path(args.input).resolve()), "--var", "OUTPUT=" + str(Path(args.output).resolve()), "--allow-data-mutation"]
    result = subprocess.run(command, timeout=70)
    if result.returncode == 0:
        summary = json.loads((report / "final-summary.json").read_text(encoding="utf-8"))
        elapsed = (datetime.fromisoformat(summary["finished_at"]) - datetime.fromisoformat(summary["started_at"])).total_seconds()
        print(json.dumps({"transport": "PASS", "elapsed_seconds": elapsed, "scope": "developer UIA keyboard reproduction, not a novice-user study"}))
    raise SystemExit(result.returncode)
