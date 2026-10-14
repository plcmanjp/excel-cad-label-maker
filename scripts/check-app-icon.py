"""Verify source hashes, ICO PNG frames, packaged asset and actual Windows PE resources."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import pefile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Project/P001-excel-cad-label/src/assets"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_icon(output, exe_name):
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["sha256"].items():
        require(name in {"app-icon.png", "app-icon.ico"}, "Unknown manifest asset")
        require(hashlib.sha256((ASSETS / name).read_bytes()).hexdigest() == expected,
                "Source asset hash mismatch: " + name)
    icon = (ASSETS / "app-icon.ico").read_bytes()
    require(struct.unpack_from("<HH", icon) == (0, 1), "Invalid ICO header")
    count = struct.unpack_from("<H", icon, 4)[0]
    require(count == len(manifest["ico_sizes"]), "ICO frame count mismatch")
    entries, frames = [], []
    expected_offset = 6 + count * 16
    for index, expected_size in enumerate(manifest["ico_sizes"]):
        entry = struct.unpack_from("<BBBBHHII", icon, 6 + index * 16)
        width, height, colors, reserved, planes, bits, length, offset = entry
        require((width or 256) == (height or 256) == expected_size, "ICO dimensions mismatch")
        require((colors, reserved, planes, bits) == (0, 0, 1, 32), "ICO is not RGBA32")
        require(offset == expected_offset and length >= 33 and offset + length <= len(icon),
                "ICO frame bounds mismatch")
        frame = icon[offset:offset + length]
        require(frame.startswith(PNG_SIGNATURE) and frame[12:16] == b"IHDR", "ICO frame is not PNG")
        require(struct.unpack_from(">II", frame, 16) == (expected_size, expected_size)
                and frame[24:26] == b"\x08\x06", "PNG dimensions or alpha format mismatch")
        entries.append(entry[:7])
        frames.append(frame)
        expected_offset += length
    require(expected_offset == len(icon), "Unexpected trailing ICO data")
    require((output / "_internal/assets/app-icon.ico").read_bytes() == icon,
            "Packaged Tk icon differs from source")
    resources = {3: {}, 14: {}}
    with pefile.PE(str(output / exe_name), fast_load=True) as executable:
        executable.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
        for resource in executable.DIRECTORY_ENTRY_RESOURCE.entries:
            if resource.id not in resources:
                continue
            for named in resource.directory.entries:
                variants = []
                for language in named.directory.entries:
                    data = language.data.struct
                    variants.append(executable.get_data(data.OffsetToData, data.Size))
                require(len(set(variants)) == 1, "Language variants have different icons")
                resources[resource.id][named.id] = variants[0]
    require(len(resources[14]) == 1 and len(resources[3]) == count, "PE icon resource count mismatch")
    group = next(iter(resources[14].values()))
    require(struct.unpack_from("<HHH", group) == (0, 1, count), "PE icon group header mismatch")
    for index, (expected_entry, frame) in enumerate(zip(entries, frames)):
        entry = struct.unpack_from("<BBBBHHIH", group, 6 + index * 14)
        require(entry[:7] == expected_entry and resources[3].get(entry[7]) == frame,
                "EXE icon frame differs from source")
    return {"status": "PASS", "ico_sizes": manifest["ico_sizes"], "pe_icon_frames": count,
            "packaged_tk_icon_matches": True, "source_sha256": manifest["sha256"],
            "exe_sha256": hashlib.sha256((output / exe_name).read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/Excel_CAD_Label_Dev")
    parser.add_argument("--exe-name", default="Excel_CAD_Label_Dev.exe")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    require(output.is_relative_to(ROOT) and Path(args.exe_name).name == args.exe_name,
            "Icon check paths must remain in the repository")
    print(json.dumps(check_icon(output, args.exe_name), ensure_ascii=True))
