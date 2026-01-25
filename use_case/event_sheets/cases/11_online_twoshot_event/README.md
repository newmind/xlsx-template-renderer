# 11. 1:1 온라인 투샷회 (online_twoshot_event)

## 테스트 목적
온라인 투샷회 이벤트의 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: online_twoshot_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. `session_duration_seconds` (촬영시간) 표시
3. 온라인 투샷 특유의 benefits 구조

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 50명 (멤버당 10명)" 표시
- [ ] 촬영시간 "60초" 표시
- [ ] 포즈/사진 관련 특전 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/11_online_twoshot_event/data.json -o cases/11_online_twoshot_event/output.xlsx -y
```
