"""Run the clone-safe SessionStart hook against disposable CURRENT fixtures."""
import json
import io
import os
from pathlib import Path
import subprocess
import sys
import shutil
from fixture_temp import FixtureDirectory, preserve_for_absence
import unittest
from contextlib import redirect_stdout
from unittest import mock
import importlib.util

SOURCE = Path(__file__).resolve().parents[1] / "hooks/session_start_status.py"
HEADINGS = ["목표", "현재 상태", "주요 결정", "검증 결과", "미해결 사항", "다음 작업"]


def load_hook_module(script=SOURCE):
    spec = importlib.util.spec_from_file_location("session_start_status", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current(overrides=None, order=None):
    sections = [["goal"], ["state"], [], [], ["open"], ["next"]]
    for key, value in (overrides or {}).items():
        sections[key] = value
    return "\n".join("## " + HEADINGS[i] + "\n" + "".join("- " + s + "\n" for s in sections[i])
                     for i in (order or range(6)))


class SessionStartTests(unittest.TestCase):
    def run_hook(self, body, source="startup", empty_newer_month=False,
                 directory_newer_journal=False, no_journal=False, sub_cwd=False):
        with FixtureDirectory() as directory:
            root = Path(directory)
            hook = root / ".agents/hooks/session_start_status.py"
            hook.parent.mkdir(parents=True)
            hook.write_bytes(SOURCE.read_bytes())
            journal = root / "wiki/journal/2026-09"
            journal.mkdir(parents=True)
            (journal / "r001-fixture.md").write_text("# Fixture\n", encoding="utf-8")
            if not no_journal and (empty_newer_month or directory_newer_journal):
                newer = journal.parent / "2026-10"
                newer.mkdir()
                if directory_newer_journal:
                    (newer / "r999-not-a-file.md").mkdir()
            if no_journal:
                preserve_for_absence(journal / "r001-fixture.md")
            path = journal.parent / "CURRENT.md"
            if body is True:
                path.mkdir()
            elif isinstance(body, bytes):
                path.write_bytes(body)
            elif body is not None:
                path.write_text(body, encoding="utf-8")
            env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ALLOW_PROTOCOL="file")
            cwd = root
            if sub_cwd:
                cwd = root / "Project" / "P001-fixture"
                cwd.mkdir(parents=True)
            p = subprocess.run([sys.executable, "-B", str(hook)], cwd=cwd,
                               input=json.dumps({"source": source}).encode(),
                               capture_output=True, env=env, timeout=15)
            self.assertEqual(p.returncode, 0, p.stderr.decode(errors="replace"))
            payload = json.loads(p.stdout.decode("utf-8"))["hookSpecificOutput"]
            self.assertEqual(payload["hookEventName"], "SessionStart")
            brief = payload["additionalContext"]
            self.assertLessEqual(len(brief.encode("utf-8")), 4096)
            self.assertIn("SOURCE: wiki/journal/CURRENT.md", brief)
            if no_journal:
                self.assertIn("JOURNAL: unavailable", brief)
            else:
                self.assertIn("2026-09/r001-fixture.md", brief)
            return brief

    def test_startup_resume_and_repeat(self):
        first = self.run_hook(current())
        self.assertEqual(first, self.run_hook(current(), "resume"))
        self.assertEqual(first, self.run_hook(current()))
        self.assertNotIn("OMITTED", first)

    def test_root_and_subcwd_are_equivalent(self):
        root = self.run_hook(current(), "startup")
        subcwd = self.run_hook(current(), "startup", sub_cwd=True)
        self.assertEqual(root, subcwd)
        self.assertEqual(subcwd, self.run_hook(current(), "resume", sub_cwd=True))

    def test_git_helper_disables_optional_locks(self):
        module = load_hook_module()
        completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with mock.patch.object(module.subprocess, "run", return_value=completed) as run:
            module._git("C:/fixture", ["status", "--porcelain"])
        self.assertEqual(
            run.call_args.args[0],
            ["git", "-C", "C:/fixture", "--no-optional-locks", "status", "--porcelain"],
        )

    def test_long_approval_restriction(self):
        self.assertIn("APPROVAL_REQUIRED_SUFFIX", self.run_hook(current({4: ["x" * 180 + " APPROVAL_REQUIRED_SUFFIX"]})))

    def test_third_open(self):
        brief = self.run_hook(current({4: ["one", "two", "APPROVAL_REQUIRED_THIRD"]}))
        self.assertNotIn("APPROVAL_REQUIRED_THIRD", brief)
        self.assertIn("OMITTED", brief)

    def test_multibyte_budget(self):
        body = current({0: ["가" * 350], 1: ["나" * 350] * 2, 4: ["다" * 350] * 2, 5: ["라" * 350] * 3})
        first = self.run_hook(body)
        self.assertIn("OMITTED", first)
        self.assertEqual(first, self.run_hook(body))

    def test_oversized_item_whole_omission(self):
        brief = self.run_hook(current({4: ["LONG_START" + "가" * 4000, "SHORT_ITEM"]}))
        self.assertNotIn("LONG_START", brief)
        self.assertIn("SHORT_ITEM", brief)
        self.assertIn("OMITTED", brief)
        self.assertIn("exceeds 10KB", brief)

    def test_continuation(self):
        self.assertIn("operation APPROVAL_REQUIRED", self.run_hook(current({4: ["operation\n  APPROVAL_REQUIRED"]})))

    def test_reordered_headings(self):
        brief = self.run_hook(current({4: ["OPEN_MARK"]}, [0, 1, 4, 2, 3, 5]))
        self.assertIn("OPEN: OPEN_MARK", brief)

    def test_latest_journal_skips_empty_newer_month(self):
        brief = self.run_hook(current(), empty_newer_month=True)
        self.assertIn("2026-09/r001-fixture.md", brief)
        self.assertNotIn("2026-10/", brief)

    def test_latest_journal_skips_directory_disguised_as_file(self):
        brief = self.run_hook(current(), directory_newer_journal=True)
        self.assertIn("2026-09/r001-fixture.md", brief)
        self.assertNotIn("2026-10/", brief)

    def test_all_journals_absent_is_explicit(self):
        self.assertIn("JOURNAL: unavailable", self.run_hook(current(), no_journal=True))

    def test_invalid_structure(self):
        for body in ["## 목표\n- goal", current() + "\n## 목표\n- duplicate",
                     current().replace("## 미해결 사항", "## unknown")]:
            with self.subTest(body=body):
                brief = self.run_hook(body)
                self.assertIn("INVALID STRUCTURE", brief)
                self.assertNotIn("OPEN:", brief)

    def test_unavailable_source(self):
        for body in (None, True, b"\xff\xfe\xff"):
            with self.subTest(body=body):
                self.assertIn("UNAVAILABLE", self.run_hook(body))

    def test_hidden_decision_and_verification(self):
        brief = self.run_hook(current({2: ["APPROVAL_PENDING"], 3: ["UNVERIFIED"]}))
        self.assertIn("OMITTED", brief)

    def test_nested_lists_require_full_source(self):
        for marker in ("  - ", "\t* ", "  1. ", "  1) "):
            with self.subTest(marker=marker):
                body = current({4: ["open"]}).replace("- open\n", "- open\n" + marker + "\ud55c\uae00 APPROVAL_REQUIRED\n")
                brief = self.run_hook(body)
                self.assertIn("INVALID STRUCTURE: nested list", brief)
                self.assertNotIn("OPEN: open", brief)


class CloneAndFailureTests(unittest.TestCase):
    def setUp(self):
        self.temp = FixtureDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name) / "\ubd80\ubaa8 \uacf5\uac04"
        self.root = self.parent / "\ubcf5\uc81c \uacf5\uac04"
        hooks = self.root / ".agents/hooks"
        hooks.mkdir(parents=True)
        self.script = hooks / SOURCE.name
        shutil.copy2(SOURCE, self.script)
        self.module = load_hook_module(self.script)
        self.jdir = self.root / "wiki/journal"
        self.jdir.mkdir(parents=True)

    def journal(self, month="2026-09", name="r001-fixture.md"):
        path = self.jdir / month / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Fixture\n", encoding="utf-8")
        return path

    def context(self):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(self.module.main(), 0)
        return json.loads(output.getvalue())["hookSpecificOutput"]["additionalContext"]

    def test_latest_actual_files_and_permission_errors(self):
        old = self.journal("2026-08", "r001-old.md")
        newest = self.jdir / "2026-09"
        newest.mkdir()
        (self.jdir / "2026-9").mkdir()
        (newest / "README.md").write_text("unrelated", encoding="utf-8")
        (newest / "r002-\ud55c\uae00.md").write_text("invalid", encoding="utf-8")
        (newest / "r999-directory.md").mkdir()
        self.assertEqual(self.module._latest_journal(str(self.root)), "wiki/journal/2026-08/r001-old.md")
        latest = self.journal("2026-09", "r002-valid.md")
        self.assertEqual(self.module._latest_journal(str(self.root)), "wiki/journal/2026-09/r002-valid.md")
        original = self.module.os.stat
        for denied in (newest, latest):
            def fail(path, *args, **kwargs):
                if str(path) == str(denied):
                    raise PermissionError("fixture")
                return original(path, *args, **kwargs)
            with self.subTest(denied=denied), mock.patch.object(self.module.os, "stat", side_effect=fail):
                with self.assertRaises(PermissionError):
                    self.module._latest_journal(str(self.root))
        preserve_for_absence(old.parent)
        preserve_for_absence(newest)
        self.assertIsNone(self.module._latest_journal(str(self.root)))

    def test_freshness_states_and_git_failures(self):
        cases = [(("", "10\n", "20\n"), "newer"), (("", "20\n", "10\n"), "normal"),
                 (("?? wiki/journal/CURRENT.md", None, None), "not-applicable"),
                 ((" M wiki/journal/CURRENT.md", None, None), "not-applicable"),
                 (("", "", "20\n"), "not-applicable"), (("", "10\n", ""), "not-applicable"),
                 ((None, None, None), "unavailable"), (("", None, "20\n"), "unavailable"),
                 (("", "bad", "20\n"), "unavailable")]
        for replies, expected in cases:
            with self.subTest(replies=replies), mock.patch.object(self.module, "_git", side_effect=replies):
                self.assertEqual(self.module._journal_newer(str(self.root), self.module.SOURCE, "wiki/journal/2026-09/r001-fixture.md"), expected)
        for failure in (FileNotFoundError(), subprocess.TimeoutExpired("git", 2)):
            with mock.patch.object(self.module.subprocess, "run", side_effect=failure) as run:
                self.assertIsNone(self.module._git(str(self.root), ["status"]))
                self.assertEqual(run.call_args.kwargs["timeout"], 2)
        for code in (1, 128):
            with mock.patch.object(self.module.subprocess, "run", return_value=subprocess.CompletedProcess([], code, "", "failure")):
                self.assertIsNone(self.module._git(str(self.root), ["status"]))

    def test_current_and_journal_failures_remain_independent(self):
        self.journal()
        path = self.jdir / "CURRENT.md"
        for case in ("missing", "invalid", "permission", "unicode"):
            preserve_for_absence(path)
            if case == "invalid":
                path.write_bytes(b"\xff")
            elif case in ("permission", "unicode"):
                path.write_text(current(), encoding="utf-8")
            original = self.module.io.open
            def fail(target, *args, **kwargs):
                if str(target) == str(path):
                    raise PermissionError("fixture") if case == "permission" else UnicodeError("fixture")
                return original(target, *args, **kwargs)
            patch = mock.patch.object(self.module.io, "open", side_effect=fail) if case in ("permission", "unicode") else mock.patch.object(self.module.io, "open", wraps=original)
            with self.subTest(case=case), patch, mock.patch.object(self.module, "_journal_newer", side_effect=AssertionError("no Git")):
                text = self.context()
            self.assertIn("UNAVAILABLE", text)
            self.assertIn("JOURNAL: wiki/journal/2026-09/r001-fixture.md", text)
        preserve_for_absence(path)
        original_listdir = self.module.os.listdir
        def denied(target):
            if str(target) == str(self.jdir):
                raise PermissionError("fixture")
            return original_listdir(target)
        with mock.patch.object(self.module.os, "listdir", side_effect=denied):
            text = self.context()
        self.assertIn("[JOURNAL] SOURCE UNAVAILABLE", text)
        self.assertIn("UNAVAILABLE: read wiki/journal/CURRENT.md", text)
        path.write_text(("(\uc5c6\uc74c)\n" * 5) + ("x" * 10300), encoding="utf-8")
        with mock.patch.object(self.module.os, "listdir", side_effect=denied):
            text = self.context()
        self.assertIn("exceeds 10KB", text)
        self.assertIn("unused starter skeleton", text)

    def test_original_and_clone_registered_commands(self):
        self.journal("2026-08", "r001-previous.md")
        (self.jdir / "2026-09").mkdir()
        (self.jdir / "CURRENT.md").write_text(current(), encoding="utf-8")
        registration = json.loads((SOURCE.parents[2] / ".codex/hooks.example.json").read_text(encoding="utf-8"))
        hook = registration["hooks"]["SessionStart"][0]["hooks"][0]
        child = self.root / "Project" / "\ud558위 \uacbd\ub85c"
        child.mkdir(parents=True)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for field in ("command", "commandWindows"):
            original = hook[field]
            self.assertEqual(original, "python .agents/hooks/session_start_status.py")
            for source in ("startup", "resume"):
                result = subprocess.run(original, shell=True, cwd=self.root,
                    input=json.dumps({"source": source}).encode(), capture_output=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                self.assertIn("GOAL: goal", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
            cloned = original.replace(".agents/hooks/session_start_status.py", '"' + str(self.script) + '"')
            self.assertNotEqual(original, cloned)
            for parent_source in (False, True):
                parent_file = self.parent / "AGENTS.md"
                if parent_source:
                    parent_file.write_text("# Synthetic parent\n", encoding="utf-8")
                else:
                    preserve_for_absence(parent_file)
                outputs = []
                for cwd in (self.root, child):
                    for source in ("startup", "resume"):
                        with self.subTest(field=field, parent=parent_source, cwd=cwd, source=source):
                            result = subprocess.run(cloned, shell=True, cwd=cwd,
                                input=json.dumps({"source": source}).encode(), capture_output=True, timeout=15)
                            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                            brief = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
                            self.assertIn("GOAL: goal", brief)
                            self.assertIn("2026-08/r001-previous.md", brief)
                            outputs.append(result.stdout)
                            self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
                self.assertEqual(outputs, [outputs[0]] * 4)
            no_python = os.environ.copy()
            no_python["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
            missing = subprocess.run(cloned, shell=True, cwd=self.root, env=no_python,
                capture_output=True, timeout=15)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("python", (missing.stdout + missing.stderr).decode(errors="replace").lower())

    def test_normal_bytes_and_read_counts(self):
        self.journal()
        raw = current()
        (self.jdir / "CURRENT.md").write_text(raw, encoding="utf-8")
        original_open = self.module.io.open
        original_listdir = self.module.os.listdir
        with mock.patch.object(self.module.io, "open", wraps=original_open) as opened, \
                mock.patch.object(self.module.os, "listdir", wraps=original_listdir) as listed, \
                mock.patch.object(self.module, "_git", side_effect=("", "20\n", "10\n")) as git_calls, \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(self.module.main(), 0)
        expected = self.module.build_brief(raw, "wiki/journal/2026-09/r001-fixture.md", [])
        payload = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": expected}}
        self.assertEqual(output.getvalue().encode("utf-8"), (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        self.assertEqual(opened.call_count, 1)
        self.assertEqual(listed.call_count, 2)
        self.assertEqual(git_calls.call_count, 3)

    def test_disposable_git_status_index_head_refs_preserved(self):
        self.journal()
        (self.jdir / "CURRENT.md").write_text(current(), encoding="utf-8")
        empty_hooks = self.root / "empty-hooks"
        empty_hooks.mkdir()
        def git(*args):
            result = subprocess.run(["git", "-c", "core.hooksPath=" + str(empty_hooks),
                "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "--no-optional-locks", *args],
                cwd=self.root, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            return result.stdout
        git("init", "-q")
        tracked = self.root / "tracked.txt"
        tracked.write_text("committed", encoding="utf-8")
        git("add", "--", "wiki/journal/CURRENT.md", "wiki/journal/2026-09/r001-fixture.md", "tracked.txt")
        git("commit", "-qm", "fixture")
        tracked.write_text("staged", encoding="utf-8")
        git("add", "--", "tracked.txt")
        tracked.write_text("unstaged", encoding="utf-8")
        (self.root / "untracked.txt").write_text("untracked", encoding="utf-8")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        status = git("status", "--porcelain")
        head = git("rev-parse", "HEAD")
        refs = git("show-ref")
        self.assertIn(b"MM tracked.txt", status)
        self.assertIn(b"?? untracked.txt", status)
        registration = json.loads((SOURCE.parents[2] / ".codex/hooks.example.json").read_text(encoding="utf-8"))
        command = registration["hooks"]["SessionStart"][0]["hooks"][0]["commandWindows"]
        command = command.replace(".agents/hooks/session_start_status.py", '"' + str(self.script) + '"')
        for source in ("startup", "resume"):
            result = subprocess.run(command, shell=True, cwd=self.root,
                input=json.dumps({"source": source}).encode(), capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            brief = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("GOAL: goal", brief)
            self.assertNotIn("SOURCE UNAVAILABLE", brief)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(status, git("status", "--porcelain"))
        self.assertEqual(head, git("rev-parse", "HEAD"))
        self.assertEqual(refs, git("show-ref"))


if __name__ == "__main__":
    unittest.main()
