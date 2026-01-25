# 08. 영상통화 이벤트 (videocall_event)

## 테스트 목적
기본 영상통화 이벤트의 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: videocall_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. `per_member` 필드 렌더링
3. `call_duration_seconds` (통화시간) 표시
4. venue가 null인 경우 처리

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 100명 (멤버당 20명)" 표시
- [ ] 통화시간 "90초" 표시
- [ ] 장소가 비어있거나 "온라인"으로 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/08_videocall_event/data.json -o cases/08_videocall_event/output.xlsx -y
```
