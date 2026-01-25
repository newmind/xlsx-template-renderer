# 02. 대면 포토회 (photo_event)

## 테스트 목적
대면 포토회 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: photo_event

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. `per_member` 필드가 올바르게 렌더링되는지
3. 포토회 특유의 benefits 구조가 표시되는지

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 60명 (멤버당 12명)" 표시
- [ ] 폴라로이드 촬영 관련 특전 표시
- [ ] 컨셉 "'회사원' 컨셉" 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/02_photo_event/data.json -o cases/02_photo_event/output.xlsx -y
```
