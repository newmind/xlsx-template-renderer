# 13. 복수 이벤트 조합: (1+2부, 3+4부)

## 테스트 목적
서로 다른 두 그룹의 이벤트가 각각 하나의 시트로 묶이는지 검증

## 이벤트 구성
- 이벤트 수: 4개
- 1부: 팬사인회 (fansign_event) - event_name: "오프라인 이벤트"
- 2부: 게임회 (game_event) - event_name: "오프라인 이벤트" (1부와 동일)
- 3부: 영상통화 (videocall_event) - event_name: "온라인 이벤트"
- 4부: 개인 영상통화 (videocall_event_individual) - event_name: "온라인 이벤트" (3부와 동일)

## 예상 시트명
- `오프라인 이벤트` (1부 + 2부 내용 포함)
- `온라인 이벤트` (3부 + 4부 내용 포함)

**총 2개 시트 생성 예상**

## 주요 검증 포인트
1. 시트가 정확히 2개 생성되었는지
2. 대면 이벤트(1,2부)와 비대면 이벤트(3,4부)가 분리되었는지
3. 각 시트에 해당하는 이벤트 내용이 모두 있는지

## 수동 테스트 시 확인 사항
- [ ] "오프라인 이벤트" 시트에 팬사인회 + 게임회 내용
- [ ] "온라인 이벤트" 시트에 영상통화 + 개인 영상통화 내용
- [ ] 각 시트의 이벤트 타입 구분 확인

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/13_combo_1_2_and_3_4/data.json -o cases/13_combo_1_2_and_3_4/output.xlsx -y
```
