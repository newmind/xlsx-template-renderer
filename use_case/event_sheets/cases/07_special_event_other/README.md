# 07. 스페셜 이벤트 - 기타 (special_event_other)

## 테스트 목적
가챠 외 스페셜 이벤트 (팬미팅 등)의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: special_event_other

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 대규모 이벤트 (200명) 구조
3. 복잡한 duration breakdown

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 200명" 표시
- [ ] 다양한 시간대 breakdown (4개) 표시
- [ ] 굿즈 패키지 계층 구조 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/07_special_event_other/data.json -o cases/07_special_event_other/output.xlsx -y
```
