# 이벤트 시트 테스트 케이스

xlsx-template-renderer를 사용한 이벤트 시트 생성 테스트입니다.

## 동작 방식

`render_event_sheets.py` 스크립트가 다음 과정을 수행합니다:

1. data.json에서 events를 `event_name` 기준으로 그룹화
2. 각 그룹별로 `story-template` 시트를 복사하여 새 시트 생성
3. 시트명은 `event_title`들을 조합 (예: "1부 대면 팬사인회 2부 포토회")
4. 각 시트에 해당 그룹의 이벤트 데이터로 렌더링
5. 원본 `story-template` 시트 삭제

### 시트명 생성 규칙

| 케이스 | events 구성 | 생성 시트명 |
|--------|-------------|-------------|
| 단일 이벤트 | 1개 이벤트 | `event_title` 그대로 (예: "1부 대면 팬사인회") |
| 복합 이벤트 | 같은 event_name 공유 | `event_title`들 조합 (예: "1부 대면 팬사인회 2부 포토회") |

## 디렉토리 구조

```
use_case/event_sheets/
├── template.xlsx              # 공통 템플릿
├── README.md                  # 이 파일
├── USECASE.md                 # 유즈케이스 설명
├── pdf-to-json-prompt.md      # JSON 스키마 정의
├── cases/                     # 테스트 케이스들
│   ├── 01_fansign_event/      # 팬사인회
│   ├── 02_photo_event/        # 포토회
│   ├── ...
│   └── 14_combo_1_2_3_and_4/  # 복수 이벤트 조합
└── scripts/                   # 테스트 스크립트
    ├── render_event_sheets.py # 시트 복사 + 렌더링
    ├── run_all.sh             # 전체 실행
    ├── run_single.sh          # 단일 실행
    └── verify.py              # 검증 스크립트
```

## 빠른 시작

### 1. 전체 케이스 실행

```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
./scripts/run_all.sh
```

### 2. 특정 케이스만 실행 (수동 테스트)

```bash
./scripts/run_single.sh 01_fansign_event
```

### 3. 검증 실행

```bash
# 전체 검증
uv run python scripts/verify.py

# 특정 케이스 검증
uv run python scripts/verify.py 01_fansign_event 12_combo_1_2_and_3
```

## 테스트 케이스 목록

### 대면 이벤트 (4종)
| 케이스 | 설명 | 예상 시트 |
|--------|------|-----------|
| 01_fansign_event | 팬사인회 | 1부 대면 팬사인회 |
| 02_photo_event | 포토회 | 1부 대면 포토회 |
| 03_game_event | 게임회 | 1부 대면 게임회 |
| 04_bakery_event | 베이커리 이벤트 | 1부 베이커리 이벤트 |

### 스페셜 이벤트 (3종)
| 케이스 | 설명 | 예상 시트 |
|--------|------|-----------|
| 05_daily_host | 일일점장 | 1부 일일점장 이벤트 |
| 06_special_event_gacha | 스페셜(가챠) | 1부 스페셜 이벤트 (가챠) |
| 07_special_event_other | 스페셜(가챠 외) | 1부 스페셜 이벤트 (팬미팅) |

### 비대면/영상통화 이벤트 (4종)
| 케이스 | 설명 | 예상 시트 |
|--------|------|-----------|
| 08_videocall_event | 영상통화 | 1부 영상통화 이벤트 |
| 09_videocall_event_unit | 유닛 영상통화 | 1부 유닛 영상통화 이벤트 |
| 10_videocall_event_individual | 개인 영상통화 | 1부 개인 영상통화 이벤트 |
| 11_online_twoshot_event | 온라인 투샷회 | 1부 11 온라인 투샷회 |

### 복수 이벤트 조합 (3종)
| 케이스 | 조합 | 예상 시트 |
|--------|------|-----------|
| 12_combo_1_2_and_3 | 1+2부, 3부 | "1부 대면 팬사인회 2부 대면 포토회", "3부 영상통화 이벤트" |
| 13_combo_1_2_and_3_4 | 1+2부, 3+4부 | "1부 대면 팬사인회 2부 대면 게임회", "3부 영상통화 이벤트 4부 개인 영상통화" |
| 14_combo_1_2_3_and_4 | 1+2+3부, 4부 | "1부 대면 팬사인회 2부 대면 포토회 3부 대면 게임회", "4부 영상통화 이벤트" |

## 검증 항목

verify.py가 확인하는 항목:

1. **파일 존재**: output.xlsx가 생성되었는지
2. **시트명 검증**: data.json 기반 예상 시트명과 실제 시트명 비교
3. **템플릿 변수 잔존**: `{{`, `{%` 등이 남아있지 않은지
4. **에러 메시지**: `#ERROR`, `#VALUE` 등 Excel 에러 확인

## 문제 해결

### 케이스 실패 시

1. 단일 케이스 재실행:
   ```bash
   ./scripts/run_single.sh <케이스명>
   ```

2. output.xlsx 직접 확인:
   ```bash
   open cases/<케이스명>/output.xlsx
   ```

3. data.json 확인:
   ```bash
   cat cases/<케이스명>/data.json | jq .
   ```

4. 케이스별 README 확인:
   ```bash
   cat cases/<케이스명>/README.md
   ```
