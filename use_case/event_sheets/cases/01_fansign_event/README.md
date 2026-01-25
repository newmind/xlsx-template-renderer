# 01. 대면 팬사인회 (fansign_event)

## 테스트 목적
대면 팬사인회 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: fansign_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. `sign_winners`, `viewing_winners` 필드가 올바르게 렌더링되는지
3. benefits 배열이 정상적으로 표시되는지

## 수동 테스트 시 확인 사항
- [ ] 아티스트명 "TestArtist" 표시
- [ ] 당첨자 수 "총 150명 (사인 50명 + 관람 100명)" 표시
- [ ] 특전 내용이 계층 구조로 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/01_fansign_event/data.json -o cases/01_fansign_event/output.xlsx -y
```
