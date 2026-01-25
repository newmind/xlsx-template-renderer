# 09. 유닛 영상통화 이벤트 (videocall_event_unit)

## 테스트 목적
유닛(소그룹) 영상통화 이벤트의 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: videocall_event_unit

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. `per_unit`, `unit_count` 필드 렌더링
3. `units` 배열 정보 표시

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 60명 (유닛당 20명 x 3유닛)" 표시
- [ ] 통화시간 "120초" 표시 (개인보다 긴 시간)
- [ ] 유닛 구성 정보 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/09_videocall_event_unit/data.json -o cases/09_videocall_event_unit/output.xlsx -y
```
