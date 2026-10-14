"""Record development build provenance; does not publish or replace baseline."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__ == "__main__":
    output = ROOT / "dist/Excel_CAD_Label_Dev"
    if not (output / "Excel_CAD_Label_Dev.exe").is_file():
        raise SystemExit("Development executable is missing; receipt refused")
    receipt = {
        "type": "development-build", "baseline_version": "0.1.0",
        "baseline_replacement": False, "python": platform.python_version(),
        "platform": platform.platform(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "--no-optional-locks", "status", "--porcelain"], cwd=ROOT)),
        "sources": {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
                    for p in (ROOT / "Project/P001-excel-cad-label/src").glob("*.py")},
        "lock_sha256": digest(ROOT / "requirements-dev.lock.txt"),
        "dependencies": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
        "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*")
                  if p.is_file() and p.name != "build-receipt.json"},
    }
    (output / "build-receipt.json").write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print("PASS: development build receipt, " + str(len(receipt["files"])) + " files")
