[![English](docs/images/language-en-idle.svg)](README.md) [![한국어 — 현재 언어](docs/images/language-ko-active.svg)](README.ko.md)

# aptup

작은 Bash 명령 하나로 Ubuntu 또는 Debian 패키지를 업데이트합니다.

## 기본 동작

`aptup`은 아래 명령을 보여주고 `Continue? [y/N]`으로 확인을 받은 뒤 실행합니다.

```bash
sudo apt-get --error-on=any update
sudo apt-get -o quiet=0 -o APT::Get::Assume-Yes=false --no-remove upgrade
```

이미 root라면 `sudo` 없이 실행합니다.

- 저장소 갱신 실패를 포함한 모든 오류에서 중단하고 해당 종료 코드를 반환합니다.
- quiet 모드와 자동 yes 설정을 꺼서 APT의 패키지 확인 질문을 유지합니다.
- 패키지 제거, 캐시 정리, 배포판 업그레이드, 재부팅은 하지 않습니다.
- 일부 패키지는 보류될 수 있습니다. 이미 완료된 변경은 되돌리지 않습니다.

먼저 작업을 저장하세요. 패키지 업데이트가 서비스를 재시작하거나 재부팅을 필요로 할 수 있습니다. 확인 전에 APT 출력을 읽어보세요.

## 설치

Linux, Bash, APT 2.2+, GNU coreutils가 필요하며 root가 아니라면 `sudo`도 필요합니다. 터미널 안내는 영어입니다.

```bash
git clone https://github.com/GYJeong-AI/aptup.git
cd aptup
bash install.sh
```

설치기는 `sudo` 없이 실행하세요. `aptup`만 `~/.local/bin/aptup`에 복사합니다. 기존 일반 파일은 교체하지만 심볼릭 링크나 디렉터리는 거절합니다. 셸 설정을 변경하거나 의존성을 설치하지 않습니다.

필요하다면 아래 줄을 자신의 셸 설정에 추가한 뒤 새 터미널을 여세요.

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 사용법

```bash
aptup            # 패키지 목록 갱신 후 업그레이드
aptup --dry-run  # 실행 없이 명령만 확인
aptup --help
```

실행에는 대화형 터미널이 필요합니다. `--dry-run`은 `sudo`를 사용하거나 저장소에 접속하지 않으며, 패키지 변경 시뮬레이션은 아닙니다. 정리 옵션은 지원하지 않습니다.

설치된 스크립트를 업데이트하려면 저장소에서 `git pull --ff-only` 후 `bash install.sh`를 실행하세요. 제거하려면:

```bash
rm -- "$HOME/.local/bin/aptup"
```

## 검사

```bash
for file in aptup install.sh tests/smoke.sh; do bash -n "$file"; done
shellcheck aptup install.sh tests/smoke.sh
bash tests/smoke.sh
```

작은 Bash 스모크 테스트가 모의 APT/sudo 명령과 임시 홈 디렉터리를 사용합니다. 테스트에는 util-linux의 `script`와 GNU `timeout`이 필요하며 Python은 필요하지 않습니다. CI는 Ubuntu에서 같은 검사를 실행합니다. 테스트는 실제 패키지를 변경하지 않으며, 실제 시스템 업그레이드 동작은 미검증입니다.

## 라이선스

[MIT](LICENSE). 언어 전환 버튼은 [Aurora Theme for Firefox](https://github.com/GYJeong-AI/aurora-firefox-theme)와 같습니다.
