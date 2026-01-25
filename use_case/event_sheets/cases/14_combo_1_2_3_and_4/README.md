# 14. 복수 이벤트 조합: (1+2+3부, 4부)

## 테스트 목적
3개 이벤트가 하나의 시트로 묶이고, 1개가 별도 시트로 생성되는지 검증

## 이벤트 구성
- 이벤트 수: 4개
- 1부: 팬사인회 (fansign_event) - event_name: "메인 이벤트"
- 2부: 포토회 (photo_event) - event_name: "메인 이벤트" (1부와 동일)
- 3부: 게임회 (game_event) - event_name: "메인 이벤트" (1,2부와 동일)
- 4부: 영상통화 (videocall_event) - event_name: "스페셜 이벤트" (다름)

## 예상 시트명
- `메인 이벤트` (1부 + 2부 + 3부 내용 포함)
- `스페셜 이벤트` (4부 내용만)

**총 2개 시트 생성 예상**

## 주요 검증 포인트
1. 시트가 정확히 2개 생성되었는지
2. "메인 이벤트" 시트에 3개 이벤트 내용이 모두 있는지
3. "스페셜 이벤트" 시트에 4부 내용만 있는지
4. 대면 이벤트 3개가 하나로 묶이는지

## 수동 테스트 시 확인 사항
- [ ] "메인 이벤트" 시트에 팬사인회 + 포토회 + 게임회 내용
- [ ] "스페셜 이벤트" 시트에 영상통화 내용
- [ ] 같은 날짜(8/20) 이벤트들이 하나의 시트에 있는지

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/14_combo_1_2_3_and_4/data.json -o cases/14_combo_1_2_3_and_4/output.xlsx -y
```
