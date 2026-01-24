# 템플릿 문법 가이드

xls-template-renderer는 Jinja2와 유사한 문법을 사용하여 xlsx 파일을 템플릿으로 활용합니다.

## 기본 문법

### 변수 (Variable)

변수는 `{{ }}` 안에 표현식을 작성합니다.

```
{{ name }}
{{ user.email }}
{{ items[0].price }}
{{ price * 1.1 }}
```

**특징:**
- 어느 셀에나 위치 가능
- 일반 텍스트와 혼합 가능: `"이름: {{ name }}님"`
- 한 셀에 여러 변수 가능: `"{{ first_name }} {{ last_name }}"`
- **존재하지 않는 변수는 그대로 유지됨**: `{{ unknown }}` → `{{ unknown }}`

### 제어문 (Control Statement)

제어문은 `{% %}` 안에 작성합니다.

**중요:** 제어문은 반드시 **빈 행의 A열에만** 위치해야 합니다. (B열 이후는 비어있어야 함)
제어문이 있는 행은 렌더링 후에 삭제됩니다.

**스타일 및 가독성:**
- 제어문 앞에 들여쓰기 공백이나 탭을 사용할 수 있습니다 (중첩 구조 표현용)
- 제어문 셀에 배경색, 글꼴 색상, 굵기/기울임 등의 스타일을 적용할 수 있습니다
- 레인보우 브라켓처럼 제어문 종류별로 다른 색상을 사용하면 가독성이 향상됩니다

#### for 루프

```
{% for item in items %}
... 반복할 내용 ...
{% endfor %}
```

**예시:**

| A열 | B열 | C열 |
|-----|-----|-----|
| {% for product in products %} | | |
| | {{ product.name }} | {{ product.price }} |
| {% endfor %} | | |

**결과 (products가 3개인 경우):**

| A열 | B열 | C열 |
|-----|-----|-----|
| | 상품1 | 1000 |
| | 상품2 | 2000 |
| | 상품3 | 3000 |

**빈 리스트:** 순회할 리스트가 비어있으면 해당 범위의 모든 행이 삭제됩니다.

#### 루프 변수

for 루프 내에서 `loop` 객체를 통해 현재 반복 상태에 접근할 수 있습니다.

| 변수 | 설명 | 예시 값 (3개 항목 중 2번째) |
|------|------|---------------------------|
| `loop.index` | 1부터 시작하는 인덱스 | 2 |
| `loop.index0` | 0부터 시작하는 인덱스 | 1 |
| `loop.first` | 첫 번째 반복이면 True | False |
| `loop.last` | 마지막 반복이면 True | False |
| `loop.length` | 전체 항목 수 | 3 |

**예시:**

| A열 | B열 |
|-----|-----|
| {% for item in items %} | |
| {{ loop.index }}. {{ item.name }} | |
| {% endfor %} | |

**결과:**

| A열 |
|-----|
| 1. 상품A |
| 2. 상품B |
| 3. 상품C |

#### if 조건문

```
{% if condition %}
... 조건이 참일 때 ...
{% endif %}
```

**elif와 else 지원:**

```
{% if status == 1 %}
... 상태1 ...
{% elif status == 2 %}
... 상태2 ...
{% else %}
... 기타 ...
{% endif %}
```

**조건식 예시:**
- 단순 변수: `{% if items %}` (리스트가 비어있지 않으면 참)
- 비교: `{% if count > 0 %}`, `{% if status == "active" %}`
- 부정: `{% if not is_deleted %}`
- 논리 연산: `{% if a and b %}`, `{% if a or b %}`
- 포함 여부: `{% if item in items %}`, `{% if item not in items %}`

#### set 변수 할당

템플릿 내에서 변수를 정의합니다.

```
{% set 변수명 = 값 %}
```

**기본 사용:**

| A열 |
|-----|
| {% set discount = 0.1 %} |
| {% set message = "안녕하세요" %} |
| 할인율: {{ discount }}, 메시지: {{ message }} |

**딕셔너리 매핑:**

타입 코드를 의미 있는 텍스트로 변환할 때 유용합니다.

| A열 |
|-----|
| {% set event_types = {"a": "대면사인회", "b": "포토", "c": "게임회"} %} |
| {% set event_name = event_types.get(event_type, "기타") %} |
| 이벤트: {{ event_name }} |

**조건부 할당 (인라인 if):**

| A열 |
|-----|
| {% set status_text = "완료" if is_done else "진행중" %} |
| 상태: {{ status_text }} |

**스코프 규칙:**

set으로 정의한 변수의 스코프는 다음 규칙을 따릅니다:

| 블록 유형 | 스코프 | 설명 |
|-----------|--------|------|
| if 블록 | 없음 | 내부에서 설정한 변수가 외부에서 접근 가능 |
| for 루프 | 있음 | 내부에서 설정한 변수가 루프 외부에서 접근 불가 |

**if 블록 내에서 (스코프 없음):**

| A열 |
|-----|
| {% if status == "active" %} |
| {% set label = "활성" %} |
| {% else %} |
| {% set label = "비활성" %} |
| {% endif %} |
| 결과: {{ label }} |

위 예시에서 `{{ label }}`은 정상적으로 "활성" 또는 "비활성"을 출력합니다.

**for 루프 내에서 (스코프 있음):**

| A열 |
|-----|
| {% for item in items %} |
| {% set found = true %} |
| {% endfor %} |
| 결과: {{ found }} |

위 예시에서 `{{ found }}`는 루프 외부에서 undefined로 `{{ found }}` 그대로 출력됩니다.

**다른 제어문과 함께 사용:**

| A열 | B열 | C열 |
|-----|-----|-----|
| {% set categories = {"A": "전자제품", "B": "의류"} %} | | |
| {% for item in items %} | | |
| {% set category_name = categories.get(item.category, "기타") %} | | |
| | {{ item.name }} | {{ category_name }} |
| {% endfor %} | | |

### 주석 (Comment)

주석은 `{# #}` 안에 작성합니다. 렌더링 후 해당 행은 삭제됩니다.

```
{# 이 줄은 주석입니다 - 결과에 포함되지 않음 #}
```

**중요:** 주석도 제어문과 마찬가지로 **빈 행의 A열에만** 위치해야 합니다.

## 표현식

### 지원하는 연산

| 연산 | 예시 | 결과 |
|------|------|------|
| 덧셈 | `{{ 10 + 5 }}` | 15 |
| 뺄셈 | `{{ age - 1 }}` | 24 |
| 곱셈 | `{{ price * 1.1 }}` | 1100 |
| 나눗셈 | `{{ total / 2 }}` | 50 |
| 문자열 연결 | `{{ name + "님" }}` | 홍길동님 |

### 필터 (Filters)

필터는 `|` 기호를 사용하여 값을 변환합니다.

#### 기본 필터

| 필터 | 설명 | 예시 |
|------|------|------|
| `default(값)` | None일 때 기본값 반환 | `{{ value\|default('N/A') }}` |
| `length` | 길이 반환 | `{{ items\|length }}` |
| `join(구분자)` | 리스트를 문자열로 연결 | `{{ items\|join(', ') }}` |

#### 문자열 필터

| 필터 | 설명 | 예시 |
|------|------|------|
| `upper` | 대문자 변환 | `{{ name\|upper }}` → `HELLO` |
| `lower` | 소문자 변환 | `{{ name\|lower }}` → `hello` |
| `title` | 제목 케이스 변환 | `{{ name\|title }}` → `Hello World` |
| `trim` | 앞뒤 공백 제거 | `{{ text\|trim }}` |
| `replace(old, new)` | 문자열 치환 | `{{ text\|replace('a', 'b') }}` |

#### 숫자 필터

| 필터 | 설명 | 예시 |
|------|------|------|
| `round(정밀도)` | 반올림 (기본 0자리) | `{{ price\|round(2) }}` → `3.14` |
| `abs` | 절대값 | `{{ value\|abs }}` → `5` (from -5) |
| `int` | 정수 변환 | `{{ num\|int }}` → `3` (from 3.7) |
| `float` | 실수 변환 | `{{ num\|float }}` → `3.0` |

#### 리스트 필터

| 필터 | 설명 | 예시 |
|------|------|------|
| `first` | 첫 번째 요소 | `{{ items\|first }}` |
| `last` | 마지막 요소 | `{{ items\|last }}` |

**필터 체이닝:**
```
{{ value|default('')|length }}
{{ name|trim|upper }}
```

### 삼항 연산자 (Ternary)

조건에 따라 다른 값을 반환합니다.

```
{{ 'active' if is_active else 'inactive' }}
{{ count if count > 0 else '없음' }}
```

### 데이터 접근

**점 표기법:**
```
{{ user.name }}
{{ company.address.city }}
```

**인덱스 접근:**
```
{{ items[0] }}
{{ users[0].name }}
{{ matrix[0][1] }}
```

**혼합:**
```
{{ company.departments[0].members[0].name }}
```

## 중첩 데이터 예시

**입력 데이터:**
```python
data = {
    "company": {
        "name": "메이크스타",
        "departments": [
            {
                "name": "개발팀",
                "members": [
                    {"name": "김철수", "role": "백엔드"},
                    {"name": "이영희", "role": "프론트엔드"}
                ]
            },
            {
                "name": "기획팀",
                "members": [
                    {"name": "박지민", "role": "PM"}
                ]
            }
        ]
    }
}
```

**템플릿:**

| A열 | B열 | C열 |
|-----|-----|-----|
| {{ company.name }} | | |
| {% for dept in company.departments %} | | |
| | {{ dept.name }} | |
| {% for member in dept.members %} | | |
| | | {{ member.name }} ({{ member.role }}) |
| {% endfor %} | | |
| {% endfor %} | | |

**결과:**

| A열 | B열 | C열 |
|-----|-----|-----|
| 메이크스타 | | |
| | 개발팀 | |
| | | 김철수 (백엔드) |
| | | 이영희 (프론트엔드) |
| | 기획팀 | |
| | | 박지민 (PM) |

## 서식 유지

렌더링 시 다음 서식이 유지됩니다:
- 폰트 (글꼴, 크기, 색상, 굵기, 기울임 등)
- 배경색
- 테두리
- 정렬
- 숫자 형식
- 셀 보호

**for 루프에서:** 반복되는 행의 서식도 원본과 동일하게 복제됩니다.

### Rich Text (부분 서식)

셀 내에서 특정 텍스트에만 서식을 적용한 Rich Text도 지원됩니다.

**예시:**
셀에 "이름: **{{ name }}**님" 형태로 `{{ name }}` 부분에만 볼드를 적용한 경우:
- 템플릿: `이름: `(일반) + `{{ name }}`(볼드+파란색) + `님`(일반)
- 렌더링 후: `이름: `(일반) + `홍길동`(볼드+파란색) + `님`(일반)

변수가 치환되어도 해당 부분의 서식이 그대로 유지됩니다.

**사용 방법:**
Excel에서 셀 편집 모드(F2)로 들어가 특정 텍스트만 선택 후 서식을 적용하면 Rich Text가 됩니다.

**지원 범위:**
| 서식 유형 | 지원 |
|-----------|------|
| 셀 전체 서식 | ✅ |
| 셀 내 부분 서식 (Rich Text) | ✅ |
| for 루프 내 서식 복제 | ✅ |
| for 루프 내 Rich Text 복제 | ✅ |

## 섹션 포함 (include_section)

다른 시트에 정의된 섹션을 현재 위치에 복사해서 삽입합니다. 재사용 가능한 컴포넌트를 만들 때 유용합니다.

### 섹션 정의 (define_section)

컴포넌트 시트에서 재사용할 영역을 정의합니다.

```
{# define_section:섹션이름 #}
... 섹션 내용 (여러 행 가능) ...
{# enddefine_section #}
```

**특징:**
- 섹션 이름은 영문, 한글, 숫자, 언더스코어 사용 가능
- `define_section`과 `enddefine_section` 마커 행은 렌더링 결과에 포함되지 않음
- 한 시트에 여러 섹션 정의 가능

**예시 (컴포넌트 시트):**

| A열 | B열 | C열 |
|-----|-----|-----|
| {# define_section:헤더 #} | | |
| 회사명: {{ company }} | | |
| 작성일: {{ date }} | | |
| {# enddefine_section #} | | |
| | | |
| {# define_section:푸터 #} | | |
| 문의: {{ contact }} | | |
| {# enddefine_section #} | | |

### 섹션 사용 (include_section)

정의된 섹션을 현재 위치에 삽입합니다.

```
{% include_section "시트명" "섹션이름" %}
```

**예시 (메인 시트):**

| A열 |
|-----|
| {% include_section "컴포넌트" "헤더" %} |
| ... 본문 내용 ... |
| {% include_section "컴포넌트" "푸터" %} |

**결과:**

| A열 |
|-----|
| 회사명: 메이크스타 |
| 작성일: 2024-01-20 |
| ... 본문 내용 ... |
| 문의: support@makestar.com |

### for/if 내에서 사용

`include_section`은 for 루프나 if 조건문 내에서도 사용할 수 있습니다.

**예시:**

| A열 |
|-----|
| {% for item in items %} |
| {% if item.type == "premium" %} |
| {% include_section "컴포넌트" "프리미엄_아이템" %} |
| {% else %} |
| {% include_section "컴포넌트" "기본_아이템" %} |
| {% endif %} |
| {% endfor %} |

### 에러 처리

시트나 섹션을 찾을 수 없는 경우, 원본 명령어를 유지하고 다음 행에 빨간색 볼드로 에러 메시지가 표시됩니다.

**에러 메시지 예시:**
- `[ERROR] 시트 '없는시트'를 찾을 수 없습니다`
- `[ERROR] 섹션 '없는섹션'의 define_section 마커가 없습니다 (시트: 컴포넌트)`

## 제약사항

1. **제어문 위치**: 제어문(`{% %}`)과 주석(`{# #}`)은 빈 행의 A열에만 위치
2. **제어문 혼합 불가**: 제어문 셀에는 다른 텍스트가 없어야 함
3. **종료 태그 필수**: `{% endfor %}`, `{% endif %}`, `{# enddefine_section #}` 필수
4. **중첩 define_section 미지원**: define_section 내부에 다른 define_section을 정의할 수 없음

## 사용 예시

```python
from xlsx_template_renderer import render_template

data = {
    "title": "월간 리포트",
    "items": [
        {"name": "상품A", "price": 1000},
        {"name": "상품B", "price": 2000},
    ],
    "total": 3000
}

render_template("template.xlsx", "output.xlsx", data)
```
