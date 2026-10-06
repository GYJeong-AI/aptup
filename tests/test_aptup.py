"""Exercise the real scripts with a closed, mocked PATH and a temporary HOME."""

import os
from pathlib import Path
import pty
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


class AptupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aptup test ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.home = self.base / "home with spaces"
        self.home.mkdir()
        self.log = self.base / "commands"
        # No real apt-get or sudo is reachable, even if a mock goes missing.
        for command in ("bash", "cat", "dirname", "install"):
            (self.bin / command).symlink_to(shutil.which(command))
        self.env = {
            "HOME": str(self.home),
            "PATH": str(self.bin),
            "APTUP_TEST_LOG": str(self.log),
            "TERM": "dumb",
        }
        self.mock("apt-get", """#!/bin/sh
printf '%s\\t' "$@" >> "$APTUP_TEST_LOG"
printf '\\n' >> "$APTUP_TEST_LOG"
for argument do
  if [ "$argument" = "${APTUP_TEST_FAIL:-}" ]; then exit 100; fi
done
exit 0
""")
        self.mock("sudo", """#!/bin/sh
if [ "${APTUP_TEST_SUDO_FAIL:-}" = 1 ]; then exit 1; fi
exec "$@"
""")

    def mock(self, name, content):
        path = self.bin / name
        path.write_text(content)
        path.chmod(0o755)

    def run_cli(self, *args, answer=None):
        command = [BASH, str(ROOT / "aptup"), *args]
        if answer is None:
            return subprocess.run(command, input="", capture_output=True, text=True,
                                  env=self.env, timeout=5)
        master, slave = pty.openpty()
        try:
            with subprocess.Popen(command, stdin=slave, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, env=self.env) as process:
                os.close(slave)
                slave = None
                os.write(master, answer.encode())
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    raise
                return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)

    def commands(self):
        if not self.log.exists():
            return []
        return [line.rstrip("\t").split("\t") for line in self.log.read_text().splitlines()]

    def run_install(self, *args, script=None):
        return subprocess.run([BASH, str(script or ROOT / "install.sh"), *args],
                              cwd=self.base, env=self.env, text=True,
                              capture_output=True, timeout=5)

    def test_help_needs_no_package_tools(self):
        (self.bin / "apt-get").unlink()
        (self.bin / "sudo").unlink()
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertEqual(self.commands(), [])

    def test_unknown_option_fails_before_commands(self):
        result = self.run_cli("--yes", answer="y\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown option", result.stderr)
        self.assertEqual(self.commands(), [])

    def test_preview_is_read_only_without_package_tools(self):
        (self.bin / "apt-get").unlink()
        (self.bin / "sudo").unlink()
        result = self.run_cli("--dry-run", "--autoremove", "--autoclean")
        self.assertEqual(result.returncode, 0)
        for expected in ("--error-on=any update", "--no-remove upgrade", "autoremove", "autoclean"):
            self.assertIn(expected, result.stdout)
        self.assertEqual(self.commands(), [])

    def test_noninteractive_execution_is_rejected(self):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("interactive terminal", result.stderr)
        self.assertEqual(self.commands(), [])

    def test_decline_blank_and_eof_do_nothing(self):
        for answer in ("n\n", "\n", "anything\n", "\x04"):
            with self.subTest(answer=answer):
                result = self.run_cli(answer=answer)
                self.assertEqual(result.returncode, 0)
                self.assertIn("Cancelled.", result.stdout)
                self.assertEqual(self.commands(), [])

    def test_default_commands_are_conservative(self):
        result = self.run_cli(answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands(), [
            ["--error-on=any", "update"],
            ["-o", "quiet=0", "-o", "APT::Get::Assume-Yes=false", "--no-remove", "upgrade"],
        ])
        self.assertIn("All requested steps completed", result.stdout)

    def test_cleanup_is_opt_in_and_ordered(self):
        result = self.run_cli("--autoclean", "--autoremove", answer="Y\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([c[-1] for c in self.commands()], ["update", "upgrade", "autoremove", "autoclean"])
        self.assertIn("APT::Get::Purge=false", self.commands()[2])
        self.assertIn("quiet=0", self.commands()[2])
        self.assertIn("APT::Get::Assume-Yes=false", self.commands()[2])
        self.assertIn("can remove packages", result.stdout)

    def test_each_cleanup_flag_is_independent(self):
        for flag, last in (("--autoremove", "autoremove"), ("--autoclean", "autoclean")):
            with self.subTest(flag=flag):
                self.log.unlink(missing_ok=True)
                result = self.run_cli(flag, answer="y\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual([c[-1] for c in self.commands()], ["update", "upgrade", last])

    def test_failure_stops_all_later_steps_and_preserves_status(self):
        operations = ["update", "upgrade", "autoremove", "autoclean"]
        for index, operation in enumerate(operations):
            with self.subTest(operation=operation):
                self.log.unlink(missing_ok=True)
                self.env["APTUP_TEST_FAIL"] = operation
                result = self.run_cli("--autoremove", "--autoclean", answer="y\n")
                self.assertEqual(result.returncode, 100)
                self.assertEqual([c[-1] for c in self.commands()], operations[:index + 1])
                self.assertIn("failed (exit 100)", result.stderr)
                self.assertNotIn("All requested steps completed", result.stdout)

    def test_missing_apt_get_fails_clearly(self):
        (self.bin / "apt-get").unlink()
        result = self.run_cli(answer="y\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("apt-get was not found", result.stderr)
        self.assertEqual(self.commands(), [])

    @unittest.skipIf(os.geteuid() == 0, "root does not need sudo")
    def test_missing_sudo_fails_clearly(self):
        (self.bin / "sudo").unlink()
        result = self.run_cli(answer="y\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("sudo was not found", result.stderr)

    @unittest.skipIf(os.geteuid() == 0, "root does not need sudo")
    def test_sudo_failure_stops_before_apt(self):
        self.env["APTUP_TEST_SUDO_FAIL"] = "1"
        result = self.run_cli(answer="y\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.commands(), [])
        self.assertIn("Refreshing package lists failed", result.stderr)

    def test_install_copies_executable_without_changing_shell_files(self):
        rc = self.home / ".bashrc"
        rc.write_text("# Leave this alone\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.home / ".local/bin/aptup"
        self.assertEqual(installed.read_bytes(), (ROOT / "aptup").read_bytes())
        self.assertEqual(installed.stat().st_mode & 0o777, 0o755)
        self.assertEqual(rc.read_text(), "# Leave this alone\n")
        self.assertFalse((self.home / ".zshrc").exists())
        self.assertEqual(self.commands(), [])
        self.assertIn('export PATH="$HOME/.local/bin:$PATH"', result.stdout)

    def test_install_can_update_existing_regular_file(self):
        self.assertEqual(self.run_install().returncode, 0)
        installed = self.home / ".local/bin/aptup"
        installed.write_text("old version\n")
        self.assertEqual(self.run_install().returncode, 0)
        self.assertEqual(installed.read_bytes(), (ROOT / "aptup").read_bytes())

    def test_install_refuses_symlink_or_directory_destination(self):
        installed = self.home / ".local/bin/aptup"
        installed.parent.mkdir(parents=True)
        target = self.base / "keep-me"
        target.write_text("original\n")
        installed.symlink_to(target)
        self.assertEqual(self.run_install().returncode, 1)
        self.assertEqual(target.read_text(), "original\n")
        installed.unlink()
        installed.mkdir()
        self.assertEqual(self.run_install().returncode, 1)
        self.assertTrue(installed.is_dir())

    def test_install_missing_source_leaves_home_unchanged(self):
        script = self.base / "install.sh"
        shutil.copyfile(ROOT / "install.sh", script)
        result = self.run_install(script=script)
        self.assertEqual(result.returncode, 1)
        self.assertIn("aptup is missing", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_install_help_and_unknown_argument_do_not_install(self):
        self.assertEqual(self.run_install("--help").returncode, 0)
        self.assertEqual(self.run_install("--unknown").returncode, 2)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
