# 04. 베이커리 이벤트 (bakery_event)

## 테스트 목적
베이커리 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: bakery_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 베이커리 특유의 장시간 duration (120분)
3. 체험형 이벤트 benefits 표시

## 수동 테스트 시 확인 사항
- [ ] 장소 "서울 OO베이커리" 표시
- [ ] 당첨자 수 "총 30명" 표시 (소규모)
- [ ] 컨셉 "'파티셰' 컨셉" 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/04_bakery_event/data.json -o cases/04_bakery_event/output.xlsx -y
```
