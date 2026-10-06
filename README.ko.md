[![English](docs/images/language-en-idle.svg)](README.md) [![한국어 — 현재 언어](docs/images/language-ko-active.svg)](README.ko.md)

# aptup

Ubuntu와 Debian을 위한 작은 대화형 APT 업데이트 도구입니다. 읽기 쉬운 Bash 스크립트 하나로 실행할 명령을 먼저 보여주고, 보수적인 기본값으로 업데이트합니다.

## 기본 동작

`aptup`은 기본적으로 패키지 목록을 새로 받은 뒤 설치된 패키지를 업그레이드합니다.

```bash
sudo apt-get --error-on=any update
sudo apt-get -o quiet=0 -o APT::Get::Assume-Yes=false --no-remove upgrade
```

실행할 명령을 그대로 보여주고 `Continue? [y/N]`으로 확인을 받습니다. 변경에 확인이 필요한 경우 APT가 패키지 목록과 자체 확인 질문을 다시 보여줍니다. 업그레이드와 제거 시 quiet 모드와 자동 yes 설정을 재설정해 해당 설정으로 APT 확인이 생략되지 않도록 합니다. 이미 root라면 `sudo` 없이 실행합니다.

- APT가 경고로만 처리할 수 있는 저장소 갱신 실패도 오류로 보고 중단합니다.
- 명령이 실패하거나 취소되면 이후 단계를 실행하지 않고 해당 종료 코드를 반환합니다. 이미 완료된 변경을 되돌리지는 않습니다.
- 기본 업그레이드는 패키지를 제거하지 않습니다. 의존성 변경이 필요한 패키지는 보류될 수 있습니다.
- `full-upgrade`, 배포판 업그레이드, 자동 `-y`, 강제 복구, 자동 재부팅을 하지 않습니다.
- 패키지 제거와 캐시 정리는 옵션으로 요청한 경우에만 실행합니다.

먼저 작업을 저장하세요. 패키지 설치 스크립트가 서비스를 재시작할 수 있고, 커널이나 라이브러리 업데이트 후 재부팅이 필요할 수 있습니다. APT 출력을 확인하고 시스템에 맞는 백업을 준비하세요.

## 설치

Linux, Bash, **APT 2.2 이상**, GNU coreutils가 필요하며 root가 아니라면 `sudo`도 필요합니다. 의존성을 자동 설치하지 않습니다. 터미널 안내는 현재 영어입니다.

```bash
git clone https://github.com/GYJeong-AI/aptup.git
cd aptup
bash install.sh
```

설치기는 일반 사용자로 실행하세요. `aptup`을 `~/.local/bin/aptup`에 복사하고 실행 권한을 설정하는 일만 합니다. 같은 위치에 일반 파일이 있으면 교체하고, 심볼릭 링크나 일반 파일이 아닌 대상은 거절합니다. 패키지를 업데이트하거나 셸 설정을 수정하지 않습니다.

`~/.local/bin`이 `PATH`에 없다면 아래 줄을 자신의 셸 설정에 직접 추가한 뒤 새 터미널을 여세요.

```bash
export PATH="$HOME/.local/bin:$PATH"
```

또는 `~/.local/bin/aptup`을 직접 실행하세요. 설치 없이 소스를 확인하려면 `bash ./aptup --dry-run`을 실행하면 됩니다.

## 사용법

```bash
aptup                           # 패키지 목록 갱신 후 업그레이드
aptup --dry-run                 # 실행 없이 명령만 확인
aptup --autoremove              # 사용하지 않는 의존성 패키지도 제거
aptup --autoclean               # 오래된 패키지 캐시도 정리
aptup --autoremove --autoclean  # 두 정리 단계를 명시적으로 요청
aptup --help
```

`--dry-run`은 명령 미리보기이며 패키지 변경 시뮬레이션이 아닙니다. `sudo`를 사용하거나 저장소를 갱신하거나 실제 의존성을 계산하지 않습니다. 실제 실행에는 대화형 터미널이 필요하며 무인 실행 모드는 없습니다.

`--autoremove`는 업그레이드에 성공한 뒤 실행합니다. 특히 커널과 드라이버를 포함한 제거 목록을 주의해서 확인하세요. 설정 파일까지 지우는 purge와 자동 yes 응답은 끕니다. `--autoclean`은 마지막에 실행하며 더 이상 다운로드할 수 없는 패키지의 캐시 파일만 지우고, 설치된 패키지는 제거하지 않습니다. 최초 확인에는 이 캐시 삭제도 포함됩니다.

잠금, 보류 패키지, 의존성과 패키지별 확인 질문은 APT가 처리합니다. 실패하면 오류를 읽고 원인을 해결한 뒤 다시 실행하세요. aptup은 잠금 파일을 지우거나 복구를 시도하지 않습니다. 자세한 동작은 [APT 명령 설명서](https://manpages.debian.org/bookworm/apt/apt-get.8.en.html)를 참고하세요.

## 업데이트와 제거

저장소의 최신 변경을 받은 뒤 스크립트를 다시 복사합니다.

```bash
git pull --ff-only
bash install.sh
```

제거하려면:

```bash
rm -- "$HOME/.local/bin/aptup"
```

기존 `ubuntu-toolkit/sysupdate`에서 옮겨 오셨나요? 이전 `~/.local/bin/sysupdate` 명령은 자동으로 교체하거나 삭제하지 않습니다. 이전 명령 대신 aptup을 사용하고, 설치 후 더 이상 필요 없다면 이전 파일을 직접 제거하세요. 다른 명령도 `~/.local/bin`을 사용한다면 기존 PATH 설정은 유지해도 됩니다.

## 검증과 기여

```bash
bash -n aptup && bash -n install.sh
shellcheck aptup install.sh
python3 -m unittest discover -s tests -v
```

테스트는 임시 홈 디렉터리, 실제 시스템 명령으로 빠져나갈 수 없는 모의 명령 경로, 가상 터미널을 사용합니다. 확인·미리보기·실행 순서·실패·의존성 누락·설치를 검사하며 실제 패키지와 셸 설정은 건드리지 않습니다. CI는 `ubuntu-latest`에서 같은 검사를 실행합니다.

로컬 검증은 Debian 13, Bash 5.2, ShellCheck 0.11.0, Python 3.12에서 진행했습니다. 실제 패키지 목록 갱신·업그레이드·제거는 실행하지 않았습니다. Ubuntu, Debian 및 다른 파생 배포판의 실제 시스템 동작은 미검증이며, 대상 환경이라는 설명이 호환성 보장을 뜻하지는 않습니다.

변경은 작게 유지해주세요. 버그 제보에는 배포판, APT/Bash 버전, 실행 명령과 개인정보를 지운 오류 출력을 포함하세요. 비공개 저장소 인증 정보나 검토하지 않은 시스템 로그는 공개하지 마세요.

## 라이선스

[MIT](LICENSE). 언어 전환 버튼은 [Aurora Theme for Firefox](https://github.com/GYJeong-AI/aurora-firefox-theme)와 같습니다.
