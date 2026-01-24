---
name: include_section 제어문 추가
overview: 마커 기반으로 다른 시트의 특정 섹션을 스타일과 함께 복사해오는 include_section 제어문을 추가합니다.
todos:
  - id: parser
    content: "parser.py: TokenType, Token, 정규식, 파싱 로직 추가 (INCLUDE_SECTION, DEFINE_SECTION, ENDDEFINE_SECTION)"
    status: completed
  - id: renderer
    content: "renderer.py: 워크북 전달 구조 변경 및 INCLUDE_SECTION 처리"
    status: completed
  - id: docs
    content: "SYNTAX.md: include_section 및 define_section 마커 문법 문서화"
    status: in_progress
  - id: test-parser
    content: "test_parser.py: include_section 및 define_section 마커 파싱 테스트 추가"
    status: pending
  - id: test-renderer
    content: "test_renderer.py: include_section 렌더링 테스트 추가"
    status: pending
  - id: example
    content: "examples/: include_section 예제 파일 추가"
    status: pending
isProject: false
---

# include_section 제어문 추가 (마커 기반)

## 구현 개요

**컴포넌트 시트**에서 `define_section` 마커로 섹션을 정의하고, **메인 시트**에서 `include_section`으로 해당 섹션을 참조하여 복사합니다.

### 문법

컴포넌트 시트 (섹션 정의):

```
{# define_section:헤더 #}
... 헤더 내용 (여러 행) ...
{# enddefine_section #}

{# define_section:footer #}
... 푸터 내용 ...
{# enddefine_section #}
```

메인 시트 (섹션 참조):

```
{% include_section "컴포넌트시트" "헤더" %}
```

## 변경 파일

### 1. [parser.py](src/xlsx_template_renderer/parser.py)

- `TokenType`에 추가:
  - `INCLUDE_SECTION`: 섹션 참조
  - `DEFINE_SECTION`: 섹션 시작 마커 (렌더링 시 삭제됨)
  - `ENDDEFINE_SECTION`: 섹션 끝 마커 (렌더링 시 삭제됨)
- `Token`에 필드 추가:
  - `include_sheet`: 참조할 시트명
  - `section_name`: 섹션 이름 (한글/영문 지원)
- 정규식 추가:
  - `INCLUDE_SECTION_PATTERN`: `^include_section\s+"([^"]+)"\s+"([^"]+)"$`
  - `DEFINE_SECTION_PATTERN`: `^\{#\s*define_section:([\w가-힣_]+)\s*#\}$`
  - `ENDDEFINE_SECTION_PATTERN`: `^\{#\s*enddefine_section\s*#\}$`
- `_parse_control_statement()`에서 include_section 파싱 처리

### 2. [renderer.py](src/xlsx_template_renderer/renderer.py)

- `render_template()`에서 워크북 객체를 `_render_sheet()`에 전달
- `_render_sheet()`에 워크북 참조 추가
- `_process_rows()`에 워크북 파라미터 추가
- `_find_section_rows()` 함수 추가: 시트에서 define_section 마커로 섹션 찾기
- `INCLUDE_SECTION` 토큰 처리:

  1. 지정된 시트에서 섹션 영역 찾기
  2. define_section/enddefine_section 마커 행 제외하고 내용만 복사
  3. 스타일 복사하여 output_rows에 추가
  4. 복사된 행에서 변수 치환 처리

### 3. [SYNTAX.md](docs/SYNTAX.md)

- `include_section` 제어문 섹션 추가
- define_section 마커 (`{# define_section:name #}`, `{# enddefine_section #}`) 설명
- 사용 예시

### 4. [test_parser.py](tests/test_parser.py)

- `TestIncludeSection` 클래스
  - `test_include_section_basic`: 기본 문법 파싱
  - `test_include_section_korean_name`: 한글 이름 파싱
  - `test_include_section_with_indentation`: 들여쓰기 포함
  - `test_include_section_invalid_format`: 잘못된 형식
- `TestDefineSectionMarkers` 클래스
  - `test_define_section_english`: 영문 마커
  - `test_define_section_korean`: 한글 마커
  - `test_enddefine_section`: 끝 마커
  - `test_define_section_with_spaces`: 공백 포함

### 5. [test_renderer.py](tests/test_renderer.py)

- `TestIncludeSection` 클래스
  - `test_include_section_basic`: 기본 복사
  - `test_include_section_with_style`: 스타일 유지
  - `test_include_section_with_variables`: 변수 치환
  - `test_include_section_korean_name`: 한글 이름
  - `test_include_section_in_for_loop`: for 루프 내 사용
  - `test_include_section_in_if_statement`: if 문 내 사용
  - `test_include_section_nonexistent_sheet`: 존재하지 않는 시트
  - `test_include_section_nonexistent_section`: 존재하지 않는 섹션
  - `test_include_section_multiple_sections`: 여러 섹션이 정의된 시트

### 6. examples/ 추가

- `include_section_template.xlsx`: 멀티 시트 템플릿
  - "메인" 시트: include_section 사용
  - "컴포넌트" 시트: define_section/enddefine_section 마커로 섹션 정의
- `include_section_usage.py`: 사용 예제
- `include_section_output.xlsx`: 출력 결과

## 동작 방식

**컴포넌트 시트** (이름: "컴포넌트"):

```
Row 1: {# define_section:헤더 #}
Row 2: 회사명: {{ company }}
Row 3: 날짜: {{ date }}
Row 4: {# enddefine_section #}
Row 5: 
Row 6: {# define_section:footer #}
Row 7: 문의: {{ contact }}
Row 8: {# enddefine_section #}
```

**메인 시트**:

```
Row 1: {% include_section "컴포넌트" "헤더" %}
Row 2: ... 본문 내용 ...
Row 3: {% include_section "컴포넌트" "footer" %}
```

**출력 결과**:

```
Row 1: 회사명: 메이크스타
Row 2: 날짜: 2024-01-20
Row 3: ... 본문 내용 ...
Row 4: 문의: support@makestar.com
```

## 사용 예시

### 독립적 사용

```
{% include_section "템플릿" "헤더" %}
{{ content }}
{% include_section "템플릿" "푸터" %}
```

### for 루프 내 사용

```
{% for item in items %}
  {% if item.type == "premium" %}
    {% include_section "템플릿" "프리미엄_아이템" %}
  {% else %}
    {% include_section "템플릿" "기본_아이템" %}
  {% endif %}
{% endfor %}
```

## 예외 처리 (엑셀에 에러 메시지 표시)

에러 발생 시 예외를 throw하지 않고, 해당 위치에 **빨간색 글자**로 에러 메시지를 표시합니다.

### 에러 메시지 형식

| 상황 | 표시되는 메시지 |

|------|----------------|

| 존재하지 않는 시트 | `[ERROR] 시트 'XXX'를 찾을 수 없습니다` |

| 존재하지 않는 섹션 | `[ERROR] 섹션 'XXX'를 찾을 수 없습니다 (시트: YYY)` |

| 시작 마커 없음 | `[ERROR] 섹션 'XXX'의 define_section 마커가 없습니다` |

| 끝 마커 없음 | `[ERROR] 섹션 'XXX'의 enddefine_section 마커가 없습니다` |

### 에러 표시 스타일

```python
error_font = Font(color="FF0000", bold=True)  # 빨간색 볼드
```

### 예시

**템플릿**:

```
{% include_section "없는시트" "헤더" %}
```

**출력 결과**:

```
Row 1: {% include_section "없는시트" "헤더" %}   (원본 명령어 유지)
Row 2: [ERROR] 시트 '없는시트'를 찾을 수 없습니다   (빨간색 볼드)
```

에러 발생 시 원본 명령어 row를 삭제하지 않고 유지하여, 어떤 include_section에서 문제가 발생했는지 쉽게 파악할 수 있습니다.

### 제한사항

- 중첩된 define_section: 지원하지 않음 (내부 define_section은 무시됨)