---
name: inplace 렌더링 지원
overview: "`render_template`은 inplace 렌더링 전용으로 변경하고, 새 파일 생성은 `render_template_to_file` 함수로 분리합니다."
todos:
  - id: update-render-template
    content: render_template 시그니처 변경 (output_path 제거, inplace 전용)
    status: completed
  - id: add-render-to-file
    content: render_template_to_file 함수 추가 (복사 후 렌더링)
    status: completed
  - id: update-init
    content: __init__.py에 새 함수 export 추가
    status: completed
  - id: update-tests
    content: 기존 테스트 수정 및 새 테스트 추가
    status: completed
  - id: update-examples
    content: examples 파일들 수정
    status: completed
isProject: false
---

# Inplace 렌더링 분리

## 설계

**책임 분리:**

- `render_template`: inplace 렌더링 (원본 파일 직접 수정)
- `render_template_to_file`: 복사 후 렌더링 (새 파일 생성)

## 1. render_template 변경

[renderer.py](src/xlsx_template_renderer/renderer.py) - output_path 제거:

```python
def render_template(
    template_path: str,
    data: Dict[str, Any],
    sheets: Optional[List[str]] = None
) -> None:
    """
    Render an xlsx template in-place.
    
    Args:
        template_path: Path to the xlsx file to render (modified in-place)
        data: Dictionary containing the data to render
        sheets: Optional list of sheet names to process. If None, all sheets are processed.
    """
    wb = load_workbook(template_path, rich_text=True)
    
    if sheets is None:
        target_sheets = wb.sheetnames
    else:
        target_sheets = [s for s in sheets if s in wb.sheetnames]
    
    for sheet_name in target_sheets:
        ws = wb[sheet_name]
        _render_sheet(ws, data, wb)
    
    wb.save(template_path)
```

## 2. render_template_to_file 추가

```python
import shutil

def render_template_to_file(
    template_path: str,
    output_path: str,
    data: Dict[str, Any],
    sheets: Optional[List[str]] = None
) -> None:
    """
    Copy template and render to a new file.
    
    Args:
        template_path: Path to the template xlsx file
        output_path: Path to save the rendered xlsx file
        data: Dictionary containing the data to render
        sheets: Optional list of sheet names to process. If None, all sheets are processed.
    """
    shutil.copy2(template_path, output_path)
    render_template(output_path, data, sheets)
```

## 3. **init**.py 수정

```python
from .renderer import render_template, render_template_to_file

__all__ = [
    "render_template",
    "render_template_to_file",
    ...
]
```

## 4. 테스트 수정

기존 테스트들은 `render_template(path, output, data)` 형태 → `render_template_to_file(path, output, data)` 로 변경

새 테스트 추가:

```python
class TestInplaceRendering:
    def test_inplace_rendering(self):
        """inplace 렌더링 테스트"""
        template_path = create_template([["{{ name }}"]])
        try:
            render_template(template_path, {"name": "홍길동"})
            result = read_output(template_path)
            assert result == [["홍길동"]]
        finally:
            os.unlink(template_path)
```

## 5. Examples 수정

`simple_usage.py`, `advanced_usage.py` 등에서:

- `render_template(template, output, data)` → `render_template_to_file(template, output, data)`