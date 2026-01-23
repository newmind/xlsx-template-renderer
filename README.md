# xlsx-template-renderer

Jinja2 스타일 문법을 사용하여 xlsx 템플릿을 렌더링하는 Python 라이브러리입니다.

## 주요 기능

- **변수 치환**: `{{ name }}`, `{{ user.email }}`, `{{ price * 1.1 }}`
- **반복문**: `{% for item in items %}...{% endfor %}`
- **조건문**: `{% if condition %}...{% elif %}...{% else %}...{% endif %}`
- **논리 연산자**: `{% if a and b %}`, `{% if a or b %}`, `{% if not a %}`, `{% if item in items %}`
- **루프 변수**: `{{ loop.index }}`, `{{ loop.first }}`, `{{ loop.last }}`, `{{ loop.length }}`
- **필터**: `{{ value|default('N/A') }}`, `{{ items|length }}`, `{{ items|join(',') }}`
- **삼항 연산자**: `{{ 'yes' if condition else 'no' }}`
- **주석**: `{# 주석 내용 #}`
- **서식 유지**: 폰트, 배경색, 테두리, 정렬, 숫자 형식, 셀 내 부분 서식(Rich Text) 보존

## 설치

### GitHub에서 설치 (외부 프로젝트)

```bash
# 최신 버전
pip install git+https://github.com/newmind/xlsx-template-renderer.git

# 특정 버전 (권장)
pip install git+https://github.com/newmind/xlsx-template-renderer.git@v0.2.0
```

**requirements.txt에 추가:**
```
xlsx-template-renderer @ git+https://github.com/newmind/xlsx-template-renderer.git@v0.2.0
```

**pyproject.toml에 추가:**
```toml
[project]
dependencies = [
    "xlsx-template-renderer @ git+https://github.com/newmind/xlsx-template-renderer.git@v0.2.0",
]
```

### 로컬 개발용 설치

```bash
pip install -e .
```

개발 의존성 포함:
```bash
pip install -e ".[dev]"
```

## 빠른 시작

```python
from xlsx_template_renderer import render_template

data = {
    "title": "월간 리포트",
    "items": [
        {"name": "상품A", "price": 1000},
        {"name": "상품B", "price": 2000},
    ]
}

render_template("template.xlsx", "output.xlsx", data)
```

## 문서

- [템플릿 문법](docs/SYNTAX.md)
- [라이브러리 배포 가이드](docs/LIBRARY_PACKAGING.md)

## 예제

- [기본 사용법](examples/simple_usage.py)
- [복잡한 템플릿 (Rich Text 포함)](examples/advanced_usage.py)

## 테스트

```bash
pytest
```

## TODO: Jinja2 대비 미지원 기능

### 필터 (Filters)
- [x] 기본값 필터: `{{ value|default('N/A') }}`
- [x] 리스트 필터: `{{ items|length }}`, `{{ items|join(',') }}`, `{{ items|first }}`, `{{ items|last }}`
- [x] 필터 체이닝: `{{ value|default('')|length }}`
- [x] 기본 필터: `{{ name|upper }}`, `{{ name|lower }}`, `{{ name|title }}`
- [x] 숫자 필터: `{{ price|round }}`, `{{ value|abs }}`, `{{ num|int }}`, `{{ num|float }}`
- [x] 문자열 필터: `{{ text|trim }}`, `{{ text|replace('a', 'b') }}`
- [ ] 문자열 필터: `{{ text|truncate(50) }}`
- [ ] 날짜 필터: `{{ date|date('Y-m-d') }}`

### 테스트 (Tests)
- [ ] `{% if items is defined %}`
- [ ] `{% if value is none %}`
- [ ] `{% if num is odd %}`, `{% if num is even %}`
- [ ] `{% if value is string %}`, `{% if value is number %}`

### 논리 연산자
- [x] `and`, `or`: `{% if a and b %}`, `{% if a or b %}`
- [x] `not`: `{% if not condition %}`
- [x] `in`: `{% if item in items %}`, `{% if item not in items %}`
- [ ] 괄호 그룹핑: `{% if (a or b) and c %}`

### 루프 변수
- [x] `loop.index` (1부터 시작하는 인덱스)
- [x] `loop.index0` (0부터 시작하는 인덱스)
- [x] `loop.first`, `loop.last`
- [x] `loop.length`

### 기타 제어문
- [ ] `{% set var = value %}` (변수 할당)
- [ ] `{% macro %}...{% endmacro %}` (매크로)
- [ ] `{% include %}` (템플릿 포함)
- [ ] `{% block %}...{% endblock %}` (블록 상속)

### 표현식
- [x] 삼항 연산자: `{{ 'yes' if condition else 'no' }}`
- [ ] 나머지 연산: `{{ value % 2 }}`
- [ ] 거듭제곱: `{{ value ** 2 }}`
- [ ] 문자열 키 접근: `{{ dict['key-name'] }}`
