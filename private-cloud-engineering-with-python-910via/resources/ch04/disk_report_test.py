import importlib
import subprocess
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "disk_report_broken"
mod = importlib.import_module(TARGET)

DF_VAR = (
    "Filesystem     1024-blocks     Used Available Capacity Mounted on\n"
    "/dev/sda2        102687672 92418904  5009452      95% /var\n"
)
DF_MANY = (
    "Filesystem     1024-blocks     Used Available Capacity Mounted on\n"
    "/dev/sda1         1048576   104858    943718      10% /boot\n"
    "/dev/sda2       104857600 94371840  10485760      90% /\n"
    "tmpfs             8388608        0   8388608       0% /dev/shm\n"
)


class FakeRunner:
    """Behaves like subprocess.run for the parts the script uses; runs nothing."""

    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        text_mode = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")
        out = self.stdout if text_mode else self.stdout.encode()
        err = "df: no such file or directory\n"
        err = err if text_mode else err.encode()
        if kwargs.get("check") and self.returncode != 0:
            raise subprocess.CalledProcessError(self.returncode, args, out, err)
        return subprocess.CompletedProcess(args, self.returncode, out, err)


class RunDfTest(unittest.TestCase):
    def test_uses_an_argument_list_without_a_shell(self):
        runner = FakeRunner(DF_VAR)
        mod.run_df("/var; rm -rf ~", runner)
        args, kwargs = runner.calls[0]
        self.assertFalse(kwargs.get("shell", False), "never run df through a shell")
        self.assertEqual(args, ["df", "-P", "-k", "/var; rm -rf ~"])

    def test_sets_a_timeout(self):
        runner = FakeRunner(DF_VAR)
        mod.run_df("/var", runner)
        self.assertEqual(runner.calls[0][1].get("timeout"), 10)

    def test_returns_str(self):
        out = mod.run_df("/var", FakeRunner(DF_VAR))
        self.assertIsInstance(out, str)
        self.assertEqual(out, DF_VAR)

    def test_non_zero_exit_raises(self):
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            mod.run_df("/nope", FakeRunner("", returncode=1))
        self.assertEqual(caught.exception.returncode, 1)


class ParseDfTest(unittest.TestCase):
    def test_single_filesystem(self):
        self.assertEqual(
            mod.parse_df(DF_VAR),
            [{"mount": "/var", "size_gib": 97.9, "used_gib": 88.1, "use_percent": 95}],
        )

    def test_several_filesystems_in_order(self):
        rows = mod.parse_df(DF_MANY)
        self.assertEqual([r["mount"] for r in rows], ["/boot", "/", "/dev/shm"])
        self.assertEqual(rows[1], {"mount": "/", "size_gib": 100.0, "used_gib": 90.0, "use_percent": 90})
        self.assertEqual(rows[0]["size_gib"], 1.0)

    def test_header_only(self):
        self.assertEqual(mod.parse_df(DF_VAR.splitlines()[0] + "\n"), [])


class DiskReportTest(unittest.TestCase):
    def test_reports_full_filesystems_and_logs(self):
        with self.assertLogs(mod.logger, level="WARNING") as logs:
            full = mod.disk_report(["/var"], threshold=90, runner=FakeRunner(DF_VAR))
        self.assertEqual([r["mount"] for r in full], ["/var"])
        self.assertEqual(len(logs.records), 1)
        self.assertIn("/var is 95% full", logs.output[0])

    def test_threshold_is_inclusive(self):
        full = mod.disk_report(["/"], threshold=90, runner=FakeRunner(DF_MANY))
        self.assertEqual([r["mount"] for r in full], ["/"])

    def test_nothing_full(self):
        full = mod.disk_report(["/"], threshold=99, runner=FakeRunner(DF_MANY))
        self.assertEqual(full, [])


if __name__ == "__main__":
    unittest.main()
