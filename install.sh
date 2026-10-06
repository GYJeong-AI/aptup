#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  -h|--help)
    printf 'Usage: bash install.sh\nCopies aptup to ~/.local/bin/aptup. Run without sudo.\n'
    exit 0
    ;;
esac
if (( $# != 0 )); then
  printf 'install: unknown argument. Use --help.\n' >&2
  exit 2
fi

[[ -n ${HOME:-} && $HOME == /* ]] || { printf 'install: HOME must be an absolute path.\n' >&2; exit 1; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
destination=$HOME/.local/bin/aptup
[[ -f $source_dir/aptup ]] || { printf 'install: aptup is missing beside install.sh.\n' >&2; exit 1; }
if [[ -L $destination || ( -e $destination && ! -f $destination ) ]]; then
  printf 'install: refusing to replace a symlink or non-file: %s\n' "$destination" >&2
  exit 1
fi

trap 'printf "install: copy failed; check the error above.\n" >&2' ERR
install -D -T -m 0755 -- "$source_dir/aptup" "$destination"
printf 'Installed %s\n' "$destination"
case ":${PATH:-}:" in
  *":$HOME/.local/bin:"*) ;;
  *)
    printf '\nAdd this to your shell configuration yourself if needed:\n'
    # shellcheck disable=SC2016 # Print the literal command for the user's shell.
    printf '  export PATH="$HOME/.local/bin:$PATH"\n'
    ;;
esac
printf '\nPreview with: "%s" --dry-run\n' "$destination"
