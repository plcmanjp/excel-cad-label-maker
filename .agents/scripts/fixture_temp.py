"""Small standalone fixture-path validator. Context exit preserves all scratch."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import tempfile
import uuid

WORKSPACE = Path(__file__).resolve().parents[2]


def _contains(root, path):
    return root == path or root in path.parents


def _plain_ancestors(path):
    for item in [*reversed(path.parents), path]:
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Fixture path contains a link or reparse point")
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError("Fixture ancestor is not a directory")


def sync_roots():
    """Read paths only; registry failures other than absence remain fatal."""
    roots = [v for k, v in os.environ.items() if k.casefold().startswith("onedrive") and v]
    if os.name == "nt":
        import winreg
        try:
            accounts = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      r"Software\Microsoft\OneDrive\Accounts")
        except FileNotFoundError:
            accounts = None
        if accounts is not None:
            with accounts:
                for index in range(winreg.QueryInfoKey(accounts)[0]):
                    with winreg.OpenKey(accounts, winreg.EnumKey(accounts, index)) as account:
                        try:
                            folder, kind = winreg.QueryValueEx(account, "UserFolder")
                        except FileNotFoundError:
                            continue
                        if kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
                            raise ValueError("Unsupported OneDrive root type")
                        roots.append(os.path.expandvars(folder))
    result = []
    for value in roots:
        path = Path(os.path.expandvars(value)).expanduser()
        if not path.is_absolute() or "%" in str(path) or "$" in str(path):
            raise ValueError("OneDrive root must be fully expanded and absolute")
        result.append(path.resolve())
    return result


def validate_base(workspace=WORKSPACE):
    workspace = Path(workspace).resolve(strict=True)
    base = Path(tempfile.gettempdir()).absolute()
    _plain_ancestors(base)
    base = base.resolve(strict=True)
    blocked = [workspace, *sync_roots()]
    if any(_contains(root, base) for root in blocked):
        raise ValueError("OS Temp must be outside workspace and OneDrive")
    return workspace, base, blocked


def create_run(workspace=WORKSPACE):
    workspace, base, blocked = validate_base(workspace)
    identity = hashlib.sha256(str(workspace).casefold().encode("utf-8")).hexdigest()[:12]
    parent = base / "excel-cad-harness" / identity
    _plain_ancestors(parent)
    parent.mkdir(parents=True, exist_ok=True)
    _plain_ancestors(parent)
    run = parent / ("fixture-" + uuid.uuid4().hex)
    run.mkdir()
    _plain_ancestors(run)
    resolved = run.resolve(strict=True)
    if resolved != run or not _contains(base, resolved) or any(
            _contains(root, resolved) for root in blocked):
        raise ValueError("Fixture path escaped its verified root")
    return run


class FixtureDirectory:
    """TemporaryDirectory-style adapter without automatic removal."""
    def __init__(self):
        self.name = str(create_run())

    def __enter__(self):
        return self.name

    def __exit__(self, *_):
        self.cleanup()

    def cleanup(self):
        return None


def preserve_for_absence(path):
    """Prepare an absence counterexample by preserving the previous payload."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        path.rename(path.with_name(path.name + ".preserved-" + uuid.uuid4().hex))
