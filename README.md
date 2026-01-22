# xls-template-renderer

Jinja2 스타일 문법을 사용하여 xlsx 템플릿을 렌더링하는 Python 라이브러리입니다.

## 주요 기능

- **변수 치환**: `{{ name }}`, `{{ user.email }}`, `{{ price * 1.1 }}`
- **반복문**: `{% for item in items %}...{% endfor %}`
- **조건문**: `{% if condition %}...{% elif %}...{% else %}...{% endif %}`
- **주석**: `{# 주석 내용 #}`
- **서식 유지**: 폰트, 배경색, 테두리, 정렬, 숫자 형식, 셀 내 부분 서식(Rich Text) 보존

## 설치

```bash
pip install -e .
```

개발 의존성 포함:
```bash
pip install -e ".[dev]"
```

## 빠른 시작

```python
from xls_template_renderer import render_template

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
