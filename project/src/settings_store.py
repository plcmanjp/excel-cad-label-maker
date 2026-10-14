"""Versioned, validated preferences. No Excel contents, sheet names or paths."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
from time import time_ns

from converter import LabelSettings


class SettingsError(ValueError):
    pass


def default_directory():
    override = os.environ.get("EXCEL_CAD_LABEL_SETTINGS_DIR")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ExcelCADLabelMaker"


def validated(value):
    expected = set(asdict(LabelSettings())) | {"mode"}
    if type(value) is not dict or set(value) != expected:
        raise SettingsError("설정 항목이 현재 버전과 맞지 않습니다.")
    values = value.copy()
    mode = values.pop("mode")
    if mode not in {"legacy", "display"} or type(values["auto_fit"]) is not bool:
        raise SettingsError("입력 해석과 자동 맞춤 설정을 확인해 주세요.")
    try:
        LabelSettings(**values)
    except (ValueError, TypeError) as error:
        raise SettingsError(str(error)) from error
    return {**asdict(LabelSettings(**values)), "mode": mode}


def defaults():
    return {**asdict(LabelSettings()), "mode": "legacy"}


def preset_name(name):
    if type(name) is not str or not name.strip() or len(name.strip()) > 60 or any(ord(c) < 32 for c in name):
        raise SettingsError("프리셋 이름은 1~60자의 읽을 수 있는 글자로 입력해 주세요.")
    name = name.strip()
    if name in {"기본 규격", "마지막 설정"}:
        raise SettingsError("기본 규격과 마지막 설정은 사용자 프리셋 이름으로 사용할 수 없습니다.")
    return name


class SettingsStore:
    def __init__(self, directory=None):
        self.path = Path(directory or default_directory()) / "settings.json"
        self.last = defaults()
        self.presets = {}
        self.warning = ""
        self.protected = False
        try:
            if self.path.exists():
                if self.path.stat().st_size > 256_000:
                    raise SettingsError("설정 파일이 허용 크기를 초과합니다.")
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if type(data) is not dict or set(data) != {"version", "last", "presets"} or type(data["version"]) is not int or data["version"] != 1:
                    raise SettingsError("알 수 없는 설정 버전입니다.")
                last = validated(data["last"])
                if type(data["presets"]) is not dict or len(data["presets"]) > 50:
                    raise SettingsError("프리셋 목록을 읽을 수 없습니다.")
                presets = {preset_name(name): validated(value) for name, value in data["presets"].items()}
                self.last, self.presets = last, presets
        except (OSError, ValueError, TypeError) as error:
            self.protected = True
            self.warning = f"설정 파일을 보존하고 기본값을 사용합니다. 설정 복구로 백업 후 다시 시작할 수 있습니다. ({error})"

    def _write(self, last, presets):
        if self.protected:
            raise SettingsError("기존 설정 파일을 보호 중입니다. 설정 복구를 먼저 사용해 주세요.")
        data = {"version": 1, "last": validated(last), "presets": {preset_name(n): validated(v) for n, v in presets.items()}}
        if len(presets) > 50:
            raise SettingsError("사용자 프리셋은 최대 50개입니다.")
        temp = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=self.path.parent, suffix=".tmp", delete=False) as stream:
                temp = Path(stream.name)
                json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
            self.last, self.presets = data["last"], data["presets"]
        except OSError as error:
            raise SettingsError("설정을 저장하지 못했습니다. 폴더의 쓰기 권한과 디스크 공간을 확인해 주세요.") from error
        finally:
            if temp is not None and temp.exists():
                temp.unlink()

    def remember(self, values):
        self._write(values, self.presets)

    def save(self, name, values, overwrite=False):
        name, values = preset_name(name), validated(values)
        if name in self.presets and not overwrite:
            raise SettingsError("같은 이름의 프리셋이 있습니다. 덮어쓰기를 확인해 주세요.")
        self._write(self.last, {**self.presets, name: values})

    def rename(self, old, new):
        new = preset_name(new)
        if old not in self.presets or new in self.presets:
            raise SettingsError("기존 프리셋과 새 이름을 확인해 주세요.")
        updated = self.presets.copy()
        updated[new] = updated.pop(old)
        self._write(self.last, updated)

    def delete(self, name):
        if name not in self.presets:
            raise SettingsError("사용자 프리셋을 선택해 주세요.")
        updated = self.presets.copy()
        del updated[name]
        self._write(self.last, updated)

    def recover(self):
        backup = None
        if self.path.exists():
            backup = self.path.with_name(f"settings.backup-{time_ns()}.json")
            with backup.open("xb") as stream:
                stream.write(self.path.read_bytes())
        was_protected = self.protected
        self.protected = False
        try:
            self._write(defaults(), {})
        except Exception:
            self.protected = was_protected
            raise
        self.warning = ""
        return backup
