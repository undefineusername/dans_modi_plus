# Dan's MODI+ (dans_modi_plus)

MODI+ 하드웨어 모듈을 기반으로 사용자의 감정 상태를 감지·기록하고, LLM과 연동해 개인화된 반응을 생성하는 스마트 디바이스 프로젝트.

단순 하드웨어 제어 테스트에서 시작해, 센서 기반 인터랙션 → 로컬 데이터 저장 → 대화형 시나리오 → AI 연동 및 개인화 메모리까지 순차적으로 확장되었다.

## Overview

| | |
|---|---|
| Hardware | LUXROBO MODI+ (Display, LED, Speaker, Button, Dial, ToF) |
| Language | Python |
| AI | Grok API |
| Storage | Local JSON |
| Status | v0.6.2 (active development) |

## Features

- ToF 센서 기반 사용자 감지 및 대기 상태 제어
- Dial/Button을 통한 기분 점수(Mood Score) 입력
- LED, Speaker를 통한 실시간 피드백
- 입력 데이터의 로컬 파일 기반 누적 저장
- JSON 시나리오 기반 대화형 인터페이스
- LLM 연동을 통한 상황별 응답 생성
- 사용자 프로필 및 대화 기록 기반 개인화 메모리

## Project Structure

```
프로젝트릭동/
├── main.py
├── groktest.py
├── dialogue.json
├── my_profile.json
├── my_memory.json
└── README.md
```

## Getting Started

```bash
git clone https://github.com/undefineusername/dans_modi_plus.git
cd dans_modi_plus/프로젝트릭동
pip install -r requirements.txt
python main.py
```

## Version History

### v0.1
MODI+ 모듈 연결 및 개별 모듈(Display, LED, Speaker, Button) 동작 검증을 위한 초기 테스트 단계.

### v0.2
ToF 센서로 사용자 근접을 감지해 대기 상태를 해제하고, Dial과 Button으로 기분 점수를 입력·확정하는 기본 루프 구현. LED와 Speaker로 피드백 제공.

### v0.3 / v0.3.1
단일 스크립트 구조에서 벗어나 `main.py` 중심으로 코드 구조화. 로직과 데이터를 분리하고, 입력 데이터를 로컬 파일에 누적 저장하기 시작.

### v0.4
모듈 연결 유실 등에 대한 예외 처리 추가. 10초 주기 리프레시 루프 도입 및 전체 시퀀스 흐름 개선.

### v0.5
`dialogue.json` 기반 대화형 인터페이스 도입. 사용자 입력 및 상태에 따라 디스플레이/스피커로 시나리오 기반 대화를 전달하는 구조 설계.

### v0.6 / v0.6.1
`groktest.py`를 통한 Grok API 연동 테스트. `my_profile.json`, `my_memory.json`을 활용해 이전 기분 상태와 대화 기록을 기억하고, 이를 반영한 실시간 응답을 생성하는 구조로 확장.

### v0.6.2 (latest)
v0.6 계열에서 발견된 버그 수정 및 예외 처리 보강. 메모리 저장 및 API 호출 흐름 최적화.

## License

TBD

## Contributing

Not currently open for external contributions.