# 목표
당신은 엑셀 자동화 전문가입니다.

이벤트의 내용이 담겨있는 json 파일과
xlsx 템플릿을 입력으로 받아 이벤트 시트를 생성합니다.


## 1. 입력파일

- json 파일: [data.json](data.json) 
- xlsx 템플릿: [template.xlsx](template.xlsx) 

### 1.1. 참조 파일

- 제안서 PDF 로 부터 이벤트 정보를 수집하여 json 파일로 변환하는 프롬프트 [pdf-to-json-prompt.md](pdf-to-json-prompt.md) 

## 2. 출력파일

- xlsx 파일: [output.xlsx](output.xlsx) 

## 3. 이벤트 파트 분리
주어지는 data.json 에는 여러 날짜에 거쳐서 진행되는 하나의 아티스트에 대한 내용이 있다.


events 필드안에서 event.overview.event_name 이 동일한 이벤트는 동일한 story 시트가 되게 해야합니다.
한 엑셀한에 즉, 여러개의 story 시트가 생길수 있습니다.

## 3. 기본 동작

입력의 xlsx 템플릿을 output.xlsx 파일로 복사한 후, 렌더링 합니다.

템플릿이 있는 시트는 story-template 이다. 이 시트를 여려개의 story 시트로 복사합니다.
이름은 "1부2부 이벤트", "3부 이벤트" 이런식이 되어야 한다.

이 시트를 복사한후, 렌더링 합니다.
```bash
xlsx-render template.xlsx data.json -s "1부2부 이벤트" -o output.xlsx -y 
```

