# 10. 개인 영상통화 이벤트 (videocall_event_individual)

## 테스트 목적
개인(프라이빗) 영상통화 이벤트의 렌더링 검증

## 이벤트 구성
- 이벤트 수: 1개
- 이벤트 타입: videocall_event_individual

## 예상 시트명
- `1부 이벤트` (story-template 복사)

## 주요 검증 포인트
1. 시트명이 "1부 이벤트"로 생성되었는지
2. 소규모 당첨자 (25명) 처리
3. 긴 통화시간 (180초) 표시

## 수동 테스트 시 확인 사항
- [ ] 당첨자 수 "총 25명 (멤버당 5명)" 표시
- [ ] 통화시간 "180초" 표시 (가장 긴 시간)
- [ ] 프라이빗 특전 (스크린샷, 친필 편지) 표시

## 실행 방법
```bash
cd /Users/jgkim/src/makestar/ax/xlsx-template-renderer/use_case/event_sheets
xlsx-render template.xlsx cases/10_videocall_event_individual/data.json -o cases/10_videocall_event_individual/output.xlsx -y
```
