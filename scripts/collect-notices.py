"""Collect installed license originals and hash-checked PyPI source notices."""
import hashlib
import importlib.metadata as metadata
from io import BytesIO
import json
from pathlib import Path
import sys
import tarfile
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "third_party/notices"

def is_notice(name):
    name = Path(str(name)).name.lower()
    return name.startswith(("license", "licence", "copying", "notice", "copyright")) and not name.endswith((".py", ".pyc"))

def fetch(url):
    with urlopen(url, timeout=30) as response:
        return response.read()

def source_notices(name, version):
    info = json.loads(fetch(f"https://pypi.org/pypi/{name}/{version}/json"))
    source = next(item for item in info["urls"] if item["packagetype"] == "sdist")
    data = fetch(source["url"])
    if hashlib.sha256(data).hexdigest() != source["digests"]["sha256"]:
        raise ValueError("Source archive hash mismatch: " + name)
    if source["filename"].endswith(".zip"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            files = [(item, archive.read(item)) for item in archive.namelist() if is_notice(item)]
    else:
        with tarfile.open(fileobj=BytesIO(data)) as archive:
            files = [(item.name, archive.extractfile(item).read()) for item in archive.getmembers()
                     if item.isfile() and is_notice(item.name)]
    return files, {"url": source["url"], "sha256": source["digests"]["sha256"]}

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    provenance = {}
    for line in (ROOT / "requirements-dev.lock.txt").read_text().splitlines():
        name, version = line.split("==")
        distribution = metadata.distribution(name)
        if distribution.version != version:
            raise ValueError("Installed version differs from lock: " + name)
        files = [(str(p), distribution.locate_file(p).read_bytes())
                 for p in (distribution.files or []) if is_notice(p)]
        source = {"kind": "installed-distribution", "version": version}
        if not files:
            files, archive = source_notices(name, version)
            source.update(kind="verified-pypi-sdist", archive=archive)
        if not files:
            raise ValueError("Missing license notice: " + name)
        target = OUTPUT / name
        target.mkdir(exist_ok=True)
        saved = {}
        for index, (origin, data) in enumerate(files):
            path = target / f"{index:02d}-{Path(origin).name}"
            path.write_bytes(data)
            saved[path.relative_to(OUTPUT).as_posix()] = {"origin": origin, "sha256": hashlib.sha256(data).hexdigest()}
        provenance[name] = {**source, "files": saved}
    for name, path in {"Python": Path(sys.base_prefix) / "LICENSE.txt",
                       "Tk": Path(sys.base_prefix) / "tcl/tk8.6/license.terms"}.items():
        data = path.read_bytes()
        (OUTPUT / (name + "-LICENSE.txt")).write_bytes(data)
        provenance[name] = {"kind": "installed-runtime", "sha256": hashlib.sha256(data).hexdigest()}
    # TkDnD's bundled Tcl sources contain their own copyright and license notice.
    tkdnd = metadata.distribution("tkinterdnd2").locate_file("tkinterdnd2/tkdnd/win-x64/tkdnd.tcl")
    data = tkdnd.read_bytes()
    (OUTPUT / "TkDnD-source-notice.tcl").write_bytes(data)
    provenance["TkDnD"] = {"kind": "bundled-source", "sha256": hashlib.sha256(data).hexdigest()}
    (ROOT / "third_party/provenance.json").write_text(json.dumps(provenance, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print("PASS: preserved notices for " + str(len(provenance)) + " components")

if __name__ == "__main__":
    main()
