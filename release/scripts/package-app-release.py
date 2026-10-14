"""Package a verified recovered release build from a clean main; never upload."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_snapshot(root):
    def query(*args):
        return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=root, text=True).strip()
    return {"commit": query("rev-parse", "HEAD"), "branch": query("branch", "--show-current"),
            "dirty": bool(query("status", "--porcelain"))}


def safe_relative(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and "\\" not in name and ":" not in name
            and not any(part in {".", ".."} for part in name.split("/")), "Unsafe receipt path")
    return path


def reject_links(root, path):
    for entry in (path, *path.parents):
        require(not entry.is_symlink() and not entry.is_junction(), "Linked package paths are refused")
        if entry == root:
            break
    require(path.resolve().is_relative_to(root.resolve()), "Package paths must stay in the repository")


def package_build(root, build, output):
    root, build, output = root.absolute(), build.absolute(), output.absolute()
    reject_links(root, build)
    reject_links(root, output)
    snapshot = git_snapshot(root)
    require(snapshot["branch"] == "main" and not snapshot["dirty"], "A clean main checkout is required")
    config = json.loads((root / "release/app-release.json").read_text(encoding="utf-8"))
    version = config["version"]
    require(re.fullmatch(r"\d+\.\d+\.\d+", version) and config["tag"] == "v" + version,
            "Stable release version and tag required")
    require(config["release_type"] == "recovered-source-build" and config["original_baseline_replaced"] is False,
            "Recovered build must preserve the original baseline")
    app_version = runpy.run_path(str(root / "project/src/app_version.py"))["APP_VERSION"]
    require(version == app_version == (build / "VERSION").read_text(encoding="utf-8").strip(),
            "Release version mismatch")
    receipt_bytes = (build / "build-receipt.json").read_bytes()
    receipt = json.loads(receipt_bytes)
    require(receipt["type"] == "release-build" and receipt["source_dirty"] is False
            and receipt["source_commit"] == snapshot["commit"] and receipt["app_version"] == version,
            "Release receipt or commit mismatch")
    require(receipt["lock_sha256"] == digest((root / "project/requirements-dev.lock.txt").read_bytes()), "Dependency lock mismatch")
    entrypoint = receipt["entrypoint"]
    require(entrypoint["path"] == "project/src/excel_cad_label.py"
            and entrypoint["sha256"] == digest((root / entrypoint["path"]).read_bytes()), "Entrypoint mismatch")
    for group in ("sources", "assets"):
        require(bool(receipt[group]), "Source or icon assets missing from receipt")
        for name, expected in receipt[group].items():
            path = root / safe_relative(name)
            reject_links(root, path)
            require(digest(path.read_bytes()) == expected, "Source or asset hash mismatch: " + name)
    require(config["binary_name"] in receipt["files"], "Executable missing from receipt")
    require((build / "_internal/assets/app-icon.ico").is_file() and (build / "third_party/README.md").is_file(),
            "Runtime icon or third-party notice missing")
    members = {}
    for name, expected in receipt["files"].items():
        path = build / safe_relative(name)
        reject_links(root, path)
        data = path.read_bytes()
        require(digest(data) == expected, "Packaged file hash mismatch: " + name)
        members[name] = data
    actual = set()
    for path in build.rglob("*"):
        reject_links(root, path)
        if path.is_file():
            actual.add(path.relative_to(build).as_posix())
    require(actual == set(members) | {"build-receipt.json"}, "Unlisted or missing package files")
    members["build-receipt.json"] = receipt_bytes
    manifest = dict(config, source_commit=snapshot["commit"],
                    binary_sha256=receipt["files"][config["binary_name"]],
                    files={name: digest(data) for name, data in sorted(members.items())})
    members["release-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    archive_name = f"Excel-CAD-Label-Maker-{version}-windows-x64.zip"
    archive, sums = output / archive_name, output / "SHA256SUMS.txt"
    reject_links(root, archive)
    reject_links(root, sums)
    require(not archive.exists() and not sums.exists(), "Existing release assets will not be overwritten")
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo("Excel-CAD-Label-Maker/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    with zipfile.ZipFile(archive) as package:
        require(package.testzip() is None, "ZIP integrity failure")
        for name, data in members.items():
            require(digest(package.read("Excel-CAD-Label-Maker/" + name)) == digest(data), "ZIP member mismatch")
    checksum = digest(archive.read_bytes())
    with sums.open("x", encoding="utf-8", newline="\n") as checksum_file:
        checksum_file.write(checksum + "  " + archive_name + "\n")
    return {"version": version, "tag": config["tag"], "source_commit": snapshot["commit"],
            "archive": archive_name, "sha256": checksum, "size": archive.stat().st_size,
            "exe_sha256": manifest["binary_sha256"], "members": len(members)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-output", default="release/artifacts/Excel_CAD_Label")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(package_build(ROOT, ROOT / args.build_output, ROOT / args.output), ensure_ascii=True))
