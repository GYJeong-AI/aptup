#!/usr/bin/env bash
set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/bin" "$tmp/home with spaces"
# Only mocks and these harmless commands are reachable from the tested scripts.
for command in bash cat dirname install; do
  ln -s "$(command -v "$command")" "$tmp/bin/$command"
done
cat > "$tmp/bin/apt-get" <<'MOCK'
#!/bin/bash
printf '%s\n' "$*" >> "$APTUP_LOG"
[[ ${*: -1} != "${APTUP_FAIL:-}" ]] || exit 100
MOCK
cat > "$tmp/bin/sudo" <<'MOCK'
#!/bin/bash
exec "$@"
MOCK
chmod +x "$tmp/bin/apt-get" "$tmp/bin/sudo"
export APTUP_LOG=$tmp/commands APTUP_ROOT=$root
export HOME="$tmp/home with spaces"
bash_bin=$(command -v bash)
script_bin=$(command -v script)
timeout_bin=$(command -v timeout)

run() {
  local expected=$1 actual=0
  shift
  : > "$APTUP_LOG"
  PATH="$tmp/bin" "$@" > "$tmp/output" 2>&1 || actual=$?
  if (( actual != expected )); then
    cat "$tmp/output"
    printf 'Expected exit %s, got %s\n' "$expected" "$actual" >&2
    exit 1
  fi
}

# util-linux script supplies a terminal; all APT/sudo calls still use the mocks.
interactive() {
  # shellcheck disable=SC2016 # The child shell expands APTUP_ROOT.
  printf '%s\n' "$2" | SHELL="$bash_bin" run "$1" "$timeout_bin" 5 "$script_bin" -qec \
    'exec bash "$APTUP_ROOT/aptup"' /dev/null
}

run 0 "$bash_bin" "$root/aptup" --help
[[ ! -s $APTUP_LOG ]]
run 0 "$bash_bin" "$root/aptup" --dry-run
[[ ! -s $APTUP_LOG ]]
grep -q -- '--no-remove upgrade' "$tmp/output"
for option in --yes --autoremove --autoclean --unknown; do
  run 2 "$bash_bin" "$root/aptup" "$option"
  [[ ! -s $APTUP_LOG ]]
done
run 1 "$bash_bin" "$root/aptup" </dev/null
[[ ! -s $APTUP_LOG ]]
interactive 0 n
[[ ! -s $APTUP_LOG ]]
interactive 0 ''
[[ ! -s $APTUP_LOG ]]
interactive 0 $'\004'
[[ ! -s $APTUP_LOG ]]
interactive 0 yes
printf '%s\n' '--error-on=any update' \
  '-o quiet=0 -o APT::Get::Assume-Yes=false --no-remove upgrade' > "$tmp/expected"
cmp "$tmp/expected" "$APTUP_LOG"
APTUP_FAIL=update interactive 100 y
[[ $(cat "$APTUP_LOG") == '--error-on=any update' ]]
APTUP_FAIL=upgrade interactive 100 y
cmp "$tmp/expected" "$APTUP_LOG"

printf '# Keep this file.\n' > "$HOME/.bashrc"
run 0 "$bash_bin" "$root/install.sh"
[[ ! -s $APTUP_LOG && -x $HOME/.local/bin/aptup ]]
cmp "$root/aptup" "$HOME/.local/bin/aptup"
[[ $(cat "$HOME/.bashrc") == '# Keep this file.' ]]
run 0 "$bash_bin" "$root/install.sh"
rm -- "$HOME/.local/bin/aptup"
ln -s "$HOME/.bashrc" "$HOME/.local/bin/aptup"
run 1 "$bash_bin" "$root/install.sh"
[[ $(cat "$HOME/.bashrc") == '# Keep this file.' ]]
printf 'All smoke tests passed (mocked APT only).\n'
