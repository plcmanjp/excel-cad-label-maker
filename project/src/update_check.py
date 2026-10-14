"""Read-only GitHub release lookup with a fixed destination and validated links."""
from dataclasses import dataclass
import json
import re
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from packaging.version import InvalidVersion, Version
from app_version import APP_VERSION

REPOSITORY_URL = "https://github.com/plcmanjp/excel-cad-label-maker"
LATEST_API = "https://api.github.com/repos/plcmanjp/excel-cad-label-maker/releases/latest"
TIMEOUT_SECONDS = 3
MAX_RESPONSE_BYTES = 256 * 1024


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag: str
    page_url: str
    asset_name: str


@dataclass(frozen=True)
class UpdateResult:
    status: str  # available / current / unavailable
    release: ReleaseInfo | None = None
    reason: str = ""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "Release lookup redirect refused", headers, None)


def release_page_url(tag):
    if not isinstance(tag, str) or not re.fullmatch(r"v?\d+\.\d+\.\d+", tag) or len(tag) > 64:
        raise ValueError("Invalid stable release tag")
    version = Version(tag.removeprefix("v"))
    if version.is_prerelease or version.is_devrelease:
        raise ValueError("Stable release required")
    return REPOSITORY_URL + "/releases/tag/" + tag


def parse_release(payload):
    if not isinstance(payload, dict) or payload.get("draft") is not False or payload.get("prerelease") is not False:
        raise ValueError("Published stable release required")
    tag = payload.get("tag_name")
    page = release_page_url(tag)
    if payload.get("html_url") != page:
        raise ValueError("Unexpected release page URL")
    version = str(Version(tag.removeprefix("v")))
    asset_name = f"Excel-CAD-Label-Maker-{version}-windows-x64.zip"
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Windows asset is missing")
    expected_download = REPOSITORY_URL + f"/releases/download/{tag}/{asset_name}"
    matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("name") == asset_name]
    if len(matches) != 1:
        raise ValueError("Exactly one Windows asset is required")
    asset = matches[0]
    if (asset.get("state") != "uploaded" or type(asset.get("size")) is not int or asset["size"] <= 0
            or asset.get("browser_download_url") != expected_download):
        raise ValueError("Windows asset is not ready or its URL is unexpected")
    return ReleaseInfo(version, tag, page, asset_name)


def check_for_update(current_version=APP_VERSION, *, opener=None):
    try:
        current = Version(current_version)
        request = Request(LATEST_API, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Excel-CAD-Label-Maker/" + APP_VERSION,
            "X-GitHub-Api-Version": "2026-03-10",
        })
        if opener is None:
            opener = build_opener(NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.geturl() != LATEST_API:
                return UpdateResult("unavailable", reason="unexpected-response-url")
            data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            return UpdateResult("unavailable", reason="response-too-large")
        release = parse_release(json.loads(data.decode("utf-8")))
        status = "available" if Version(release.version) > current else "current"
        return UpdateResult(status, release)
    except HTTPError as error:
        return UpdateResult("unavailable", reason=f"http-{error.code}")
    except (URLError, TimeoutError, OSError):
        return UpdateResult("unavailable", reason="network-error")
    except (ValueError, InvalidVersion, UnicodeError, TypeError, RecursionError):
        return UpdateResult("unavailable", reason="invalid-release")
