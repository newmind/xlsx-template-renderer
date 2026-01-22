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

## 제약사항

1. **제어문 위치**: 제어문(`{% %}`)과 주석(`{# #}`)은 빈 행의 A열에만 위치
2. **제어문 혼합 불가**: 제어문 셀에는 다른 텍스트가 없어야 함
3. **종료 태그 필수**: `{% endfor %}`, `{% endif %}` 필수
4. **미지원 기능**: 매크로, include, 블록 상속 등

## 사용 예시

```python
from xls_template_renderer import render_template

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
