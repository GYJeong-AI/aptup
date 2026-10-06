[![English — current language](docs/images/language-en-active.svg)](README.md) [![한국어](docs/images/language-ko-idle.svg)](README.ko.md)

# aptup

A small, interactive APT updater for Ubuntu and Debian. One readable Bash script, a command preview, and conservative defaults.

## What it does

By default, `aptup` refreshes package lists and upgrades installed packages:

```bash
sudo apt-get --error-on=any update
sudo apt-get -o quiet=0 -o APT::Get::Assume-Yes=false --no-remove upgrade
```

It prints the exact commands and asks `Continue? [y/N]` before running anything. APT still shows its package list and asks for its own confirmation when changes require it. Upgrade and removal reset quiet mode and automatic yes settings so those settings cannot skip APT's confirmation. Commands run directly when you are already root.

- An update error stops the run, including a failed repository refresh that APT would otherwise treat as a warning.
- A failed or cancelled command stops all later steps and returns its exit status. Completed changes are not rolled back.
- Default upgrades cannot remove packages. Packages requiring dependency changes may be held back.
- No `full-upgrade`, release upgrade, automatic `-y`, forced repair, or automatic reboot.
- Package removal and cache cleanup run only when explicitly requested.

Save your work first. Package scripts can restart services, and a kernel or library update may require a reboot. Review APT's output and keep backups appropriate for your system.

## Install

Requires Linux, Bash, **APT 2.2 or newer**, GNU coreutils, and `sudo` unless running as root. Dependencies are not installed automatically. The terminal prompts are currently in English.

```bash
git clone https://github.com/GYJeong-AI/aptup.git
cd aptup
bash install.sh
```

Run the installer as your normal user. It only copies `aptup` to `~/.local/bin/aptup`, makes it executable, and replaces a regular file already at that location. It refuses symlinks and non-file destinations. It does not update packages or edit shell configuration.

If `~/.local/bin` is not on your `PATH`, add this line to your shell configuration yourself, then open a new terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Or use `~/.local/bin/aptup` directly. To try the source without installing, run `bash ./aptup --dry-run`.

## Use

```bash
aptup                           # Update package lists, then upgrade
aptup --dry-run                 # Show commands without running them
aptup --autoremove              # Also remove unused dependency packages
aptup --autoclean               # Also delete obsolete cached package files
aptup --autoremove --autoclean  # Explicitly request both cleanup steps
aptup --help
```

`--dry-run` is a command preview, not a simulation of package changes. It does not use `sudo`, refresh repositories, or inspect the package resolver. Actual execution requires an interactive terminal; there is no unattended mode.

`--autoremove` runs after a successful upgrade. Review its list carefully, especially for kernels and drivers. It disables purging and automatic yes answers. `--autoclean` runs last and deletes only cached package files that can no longer be downloaded; it does not remove installed packages. The initial confirmation covers this cache deletion.

APT handles locks, held packages, dependencies and package-level prompts. If a step fails, read its error and resolve the cause before retrying. aptup does not remove lock files or attempt a repair. See the [APT command reference](https://manpages.debian.org/bookworm/apt/apt-get.8.en.html).

## Update and uninstall

Update the checkout, then copy the new script again:

```bash
git pull --ff-only
bash install.sh
```

To uninstall:

```bash
rm -- "$HOME/.local/bin/aptup"
```

Upgrading from `ubuntu-toolkit/sysupdate`? The old `~/.local/bin/sysupdate` command is not replaced or removed automatically. Stop using it; after installing aptup, remove that old file yourself if you no longer need it. Existing PATH settings can stay if other commands use `~/.local/bin`.

## Validation and contributing

```bash
bash -n aptup && bash -n install.sh
shellcheck aptup install.sh
python3 -m unittest discover -s tests -v
```

The tests use a temporary home, a closed mocked command path, and a pseudo-terminal. They cover confirmation, preview, command order, failures, missing dependencies and installation without touching real packages or shell configuration. CI runs these checks on `ubuntu-latest`.

Local validation was performed on Debian 13 with Bash 5.2, ShellCheck 0.11.0 and Python 3.12. No real package update, upgrade or removal was performed. Real-system behavior on Ubuntu, Debian and other derivatives remains unverified; these are intended environments, not a compatibility guarantee.

Keep changes small. Bug reports should include your distribution, APT/Bash versions, command and redacted error output. Do not post private repository credentials or unredacted system logs.

## License

[MIT](LICENSE). The language buttons match [Aurora Theme for Firefox](https://github.com/GYJeong-AI/aurora-firefox-theme).
