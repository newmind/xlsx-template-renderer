# 06. 스페셜 이벤트 - 가챠 (special_event_gacha)

## 테스트 목적
가챠(럭키박스) 형식 스페셜 이벤트의 기본 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: special_event_gacha

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 가챠 등급별 benefits 계층 구조
3. 당첨 인원이 등급별로 분류되어 표시

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 80명" 표시
- [ ] 가챠 등급별 특전 (1등~4등) 표시
- [ ] 컨셉 "'럭키박스' 컨셉" 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/06_special_event_gacha/data.json -o cases/06_special_event_gacha/output.xlsx -y
```
