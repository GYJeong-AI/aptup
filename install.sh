#!/usr/bin/env bash
set -euo pipefail

if (( $# != 0 )); then
  printf 'Usage: bash install.sh (run without sudo)\n' >&2
  exit 2
fi
[[ -n ${HOME:-} && $HOME == /* ]] || { printf 'install: HOME must be an absolute path.\n' >&2; exit 1; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
destination=$HOME/.local/bin/aptup
if [[ -L $destination || ( -e $destination && ! -f $destination ) ]]; then
  printf 'install: refusing to replace a symlink or non-file: %s\n' "$destination" >&2
  exit 1
fi
install -D -T -m 0755 -- "$source_dir/aptup" "$destination"
printf 'Installed %s\n' "$destination"
case ":${PATH:-}:" in
  *":$HOME/.local/bin:"*) ;;
  *)
    printf 'Add this to your shell configuration if needed:\n'
    # shellcheck disable=SC2016 # Print the literal command for the user's shell.
    printf '  export PATH="$HOME/.local/bin:$PATH"\n'
    ;;
esac
