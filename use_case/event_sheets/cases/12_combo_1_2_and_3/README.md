# 12. 복수 이벤트 조합: (1+2부, 3부)

## 테스트 목적
같은 event_name을 가진 이벤트들이 하나의 시트로 묶이는지 검증

## 이벤트 구성
- 이벤트 수: 3개
- 1부: 팬사인회 (fansign_event) - event_name: "1부2부 이벤트"
- 2부: 포토회 (photo_event) - event_name: "1부2부 이벤트" (1부와 동일)
- 3부: 영상통화 (videocall_event) - event_name: "3부 이벤트" (다름)

## 예상 시트명
- `1부2부 이벤트` (1부 + 2부 내용 포함)
- `3부 이벤트` (3부 내용만)

**총 2개 시트 생성 예상**

## 주요 검증 포인트
1. 시트가 정확히 2개 생성되었는지
2. "1부2부 이벤트" 시트에 1부, 2부 내용이 모두 있는지
3. "3부 이벤트" 시트에 3부 내용만 있는지
4. event_name 기준으로 시트 분리가 올바른지

## 수동 테스트 시 확인 사항
- [ ] 시트 탭이 2개인지 확인
- [ ] 각 시트의 이벤트 내용이 맞는지 확인
- [ ] 대면(1,2부) vs 비대면(3부) 구분 확인

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/12_combo_1_2_and_3/data.json -o cases/12_combo_1_2_and_3/output.xlsx -y
```
