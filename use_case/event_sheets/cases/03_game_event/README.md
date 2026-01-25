# 03. 대면 게임회 (game_event)

## 테스트 목적
대면 게임회 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: game_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 게임회 특유의 당첨자 수 구조 (단순 total)
3. 게임 관련 benefits 표시

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 100명" 표시
- [ ] 게임 진행 관련 특전 표시
- [ ] 컨셉 "'스포츠' 컨셉" 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/03_game_event/data.json -o cases/03_game_event/output.xlsx -y
```
