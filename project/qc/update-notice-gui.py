"""Separate GUI QC entry point. No version override exists in the production app."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "project/src"))
from app_version import APP_VERSION
from excel_cad_label import App
from tkinterdnd2 import TkinterDnD
from update_check import check_for_update


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=("live-older", "live-current"), default="live-older")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--geometry", help="Window size and position for placement QC")
    args = parser.parse_args()
    current = "0.0.1" if args.scenario == "live-older" else APP_VERSION
    def checker(version):
        result = check_for_update(version)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({"scenario": args.scenario, "production_version": APP_VERSION,
                                           "comparison_version": current, "real_github_api": True,
                                           "result": asdict(result)}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        return result
    root = TkinterDnD.Tk()
    App(root, current_version=current, update_checker=checker)
    root.title(f"업데이트 알림 검수 (입력 버전 {current}, 실제 API)")
    if args.geometry:
        root.geometry(args.geometry)
    root.mainloop()


if __name__ == "__main__":
    main()
