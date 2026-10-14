from copy import deepcopy
import json
from pathlib import Path
import ssl
import sys
from urllib.error import HTTPError, URLError
from unittest.mock import patch
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from update_check import (LATEST_API, MAX_RESPONSE_BYTES, REPOSITORY_URL, TIMEOUT_SECONDS,
                          NoRedirect, check_for_update, parse_release)


def payload(version="0.2.0"):
    tag = "v" + version
    name = f"Excel-CAD-Label-Maker-{version}-windows-x64.zip"
    return {"tag_name": tag, "draft": False, "prerelease": False,
            "html_url": REPOSITORY_URL + "/releases/tag/" + tag,
            "assets": [{"name": name, "state": "uploaded", "size": 100,
                        "browser_download_url": REPOSITORY_URL + f"/releases/download/{tag}/{name}"}]}


class Response:
    def __init__(self, data, url=LATEST_API):
        self.data, self.url = data, url
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def geturl(self):
        return self.url
    def read(self, limit):
        return self.data[:limit]


class Opener:
    def __init__(self, data=None, *, error=None, url=LATEST_API):
        self.data = json.dumps(payload()).encode() if data is None else data
        self.error, self.url = error, url
        self.requests = []
    def open(self, request, timeout):
        self.requests.append((request, timeout))
        if self.error:
            raise self.error
        return Response(self.data, self.url)


class UpdateCheckTests(unittest.TestCase):
    def test_semantic_version_comparison_and_development_version(self):
        for latest, current, expected in [("0.2.0", "0.1.0", "available"),
            ("0.2.0", "0.2.0", "current"), ("0.1.0", "0.2.0.dev1", "current"),
            ("0.2.0", "0.2.0.dev1", "available"), ("0.10.0", "0.2.0", "available")]:
            with self.subTest(latest=latest, current=current):
                result = check_for_update(current, opener=Opener(json.dumps(payload(latest)).encode()))
                self.assertEqual(result.status, expected)
                self.assertEqual(result.release.version, latest)

    def test_fixed_request_destination_tls_timeout_and_no_identifiers(self):
        opener = Opener()
        with patch("update_check.build_opener", return_value=opener) as factory:
            result = check_for_update("0.1.0")
        self.assertEqual(result.status, "available")
        handlers = factory.call_args.args
        self.assertTrue(any(isinstance(item, NoRedirect) for item in handlers))
        https = next(item for item in handlers if hasattr(item, "_context"))
        self.assertEqual(https._context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(https._context.check_hostname)
        request, timeout = opener.requests[0]
        self.assertEqual(request.full_url, LATEST_API)
        self.assertEqual(timeout, TIMEOUT_SECONDS)
        self.assertIsNone(request.data)
        self.assertNotIn("Authorization", dict(request.header_items()))
        self.assertEqual(set(key.lower() for key in dict(request.header_items())),
                         {"accept", "user-agent", "x-github-api-version"})

    def test_drafts_prereleases_missing_flags_and_bad_tags_rejected(self):
        for key, value in [("draft", True), ("prerelease", True), ("draft", None),
                           ("tag_name", "v0.2.0rc1"), ("tag_name", "../v0.2.0"),
                           ("tag_name", "not-a-version"), ("tag_name", None)]:
            data = payload()
            data[key] = value
            with self.subTest(key=key, value=value):
                self.assertEqual(check_for_update("0.1.0", opener=Opener(json.dumps(data).encode())).status, "unavailable")

    def test_bad_page_urls_fail_closed(self):
        for url in ["http://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.0",
                    "https://evil.example/releases/tag/v0.2.0",
                    "https://github.com@evil.example/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.0",
                    REPOSITORY_URL + "/releases/tag/v0.2.0?redirect=https://evil.example",
                    REPOSITORY_URL + "/releases/tag/v0.2.0#fragment",
                    "https://github.com/plcmanjp/other/releases/tag/v0.2.0"]:
            data = payload()
            data["html_url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                parse_release(data)

    def test_only_uploaded_matching_windows_zip_is_accepted(self):
        variants = []
        for key, value in [("state", "new"), ("size", 0), ("size", True),
                           ("browser_download_url", "https://evil.example/app.exe"), ("name", "source.zip")]:
            data = payload()
            data["assets"][0][key] = value
            variants.append(data)
        data = payload()
        data["assets"] = []
        variants.append(data)
        data = payload()
        data["assets"].append(deepcopy(data["assets"][0]))
        variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_release(data)

    def test_malformed_response_and_size_limit(self):
        for data in [b"not json", b"\xff", b"[]", b"null", b"x" * (MAX_RESPONSE_BYTES + 1)]:
            with self.subTest(size=len(data)):
                self.assertEqual(check_for_update(opener=Opener(data)).status, "unavailable")

    def test_network_and_http_errors_are_normal_results(self):
        errors = [TimeoutError(), URLError("offline"), OSError("connection failure")]
        errors += [HTTPError(LATEST_API, code, "failure", {}, None) for code in (403, 404, 429, 500)]
        for error in errors:
            with self.subTest(error=error):
                self.assertEqual(check_for_update(opener=Opener(error=error)).status, "unavailable")

    def test_redirects_are_refused(self):
        from urllib.request import Request
        with self.assertRaises(HTTPError):
            NoRedirect().redirect_request(Request(LATEST_API), None, 302, "redirect", {}, "http://evil.example")
        self.assertEqual(check_for_update(opener=Opener(url="https://evil.example")).reason, "unexpected-response-url")


if __name__ == "__main__":
    unittest.main()
