"""Record development build provenance; does not publish or replace baseline."""
import hashlib
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="project/dist/Excel_CAD_Label_Dev")
    parser.add_argument("--exe-name", default="Excel_CAD_Label_Dev.exe")
    parser.add_argument("--build-type", choices=("development-build", "update-qc-build", "release-build"), default="development-build")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT) or Path(args.exe_name).name != args.exe_name:
        raise SystemExit("Build receipt paths must remain in the repository")
    if not (output / args.exe_name).is_file():
        raise SystemExit("Development executable is missing; receipt refused")
    receipt = {
        "type": args.build_type, "baseline_version": "0.1.0",
        "app_version": runpy.run_path(str(ROOT / "project/src/app_version.py"))["APP_VERSION"],
        "baseline_replacement": False, "python": platform.python_version(),
        "platform": platform.platform(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "--no-optional-locks", "status", "--porcelain"], cwd=ROOT)),
        "sources": {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
                    for p in (ROOT / "project/src").glob("*.py")},
        "assets": {p.relative_to(ROOT).as_posix(): digest(p)
                   for p in (ROOT / "project/src/assets").glob("app-icon.*")},
        "entrypoint": {"path": "project/qc/update-notice-gui.py" if args.build_type == "update-qc-build"
                       else "project/src/excel_cad_label.py"},
        "lock_sha256": digest(ROOT / "project/requirements-dev.lock.txt"),
        "dependencies": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
        "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*")
                  if p.is_file() and p.name != "build-receipt.json"},
    }
    receipt["entrypoint"]["sha256"] = digest(ROOT / receipt["entrypoint"]["path"])
    (output / "build-receipt.json").write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print("PASS: development build receipt, " + str(len(receipt["files"])) + " files")
