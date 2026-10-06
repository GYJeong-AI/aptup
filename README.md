[![English — current language](docs/images/language-en-active.svg)](README.md) [![한국어](docs/images/language-ko-idle.svg)](README.ko.md)

# aptup

Update Ubuntu or Debian packages with one small Bash command.

## What it does

`aptup` shows these commands and asks `Continue? [y/N]` before running them:

```bash
sudo apt-get --error-on=any update
sudo apt-get -o quiet=0 -o APT::Get::Assume-Yes=false --no-remove upgrade
```

Already root? The commands run without `sudo`.

- Stops on any failure, including a failed repository refresh, and returns that exit status.
- Keeps APT's own package confirmation by disabling quiet mode and automatic yes.
- Does not remove packages, clean caches, run a distribution upgrade, or reboot.
- Some packages may be held back. Completed changes are not rolled back.

Save your work first: package updates can restart services or require a reboot. Review APT's output before confirming.

## Install

Requires Linux, Bash, APT 2.2+, GNU coreutils, and `sudo` unless root. Prompts are in English.

```bash
git clone https://github.com/GYJeong-AI/aptup.git
cd aptup
bash install.sh
```

Run the installer without `sudo`. It copies only `aptup` to `~/.local/bin/aptup`, replacing an existing regular file but refusing a symlink or directory. It does not change shell settings or install dependencies.

If needed, add this to your shell configuration and open a new terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Use

```bash
aptup            # Refresh package lists, then upgrade
aptup --dry-run  # Preview commands only
aptup --help
```

Execution requires an interactive terminal. `--dry-run` does not use `sudo` or contact repositories; it is not a simulation of package changes. Cleanup flags are not supported.

To update the installed script, run `git pull --ff-only` in the checkout, then `bash install.sh`. To uninstall:

```bash
rm -- "$HOME/.local/bin/aptup"
```

## Checks

```bash
for file in aptup install.sh tests/smoke.sh; do bash -n "$file"; done
shellcheck aptup install.sh tests/smoke.sh
bash tests/smoke.sh
```

The small Bash smoke test uses mocked APT/sudo commands and a temporary home. Tests require util-linux `script` and GNU `timeout`; Python is not needed. CI runs these checks on Ubuntu. No real package changes are performed by the tests; real-system upgrades remain unverified.

## License

[MIT](LICENSE). Language buttons match [Aurora Theme for Firefox](https://github.com/GYJeong-AI/aurora-firefox-theme).
