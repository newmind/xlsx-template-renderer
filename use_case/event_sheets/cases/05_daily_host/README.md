# 05. 일일점장 이벤트 (daily_host)

## 테스트 목적
일일점장(카페) 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: daily_host

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 카페 이벤트 특유의 장소 정보
3. 서빙 관련 benefits 표시

## 수동 테스트 시 확인 사항
- [ ] 장소 "서울 OO카페" 표시
- [ ] 당첨자 수 "총 50명" 표시
- [ ] 컨셉 "'카페 알바생' 컨셉" 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/05_daily_host/data.json -o cases/05_daily_host/output.xlsx -y
```
