# AGENTS.md

## Project Overview

Python library for rendering xlsx templates using Jinja2-style syntax. Preserves cell formatting, Rich Text, and merged cells.

## Build/Test Commands

```bash
# Install (development)
pip install -e .
pip install -e ".[dev]"  # with dev dependencies

# Run all tests
pytest

# Run single test file
pytest tests/test_renderer.py

# Run single test class
pytest tests/test_renderer.py::TestVariableSubstitution

# Run single test
pytest tests/test_renderer.py::TestVariableSubstitution::test_simple_variable

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=xlsx_template_renderer

# Type checking (no mypy configured, use pyright if needed)
# pyright src/

# CLI usage
xlsx-render template.xlsx data.json -o output.xlsx
```

## Project Structure

```
src/xlsx_template_renderer/
  __init__.py      # Public API exports
  renderer.py      # Main rendering logic
  parser.py        # Template syntax parsing
  expressions.py   # Expression evaluation (arithmetic, filters, ternary)
  filters.py       # Filter implementations (default, length, join, etc.)
  exceptions.py    # Custom exceptions
  cli.py           # Command-line interface

tests/
  test_renderer.py    # Main renderer tests
  test_parser.py      # Parser tests
  test_expressions.py # Expression evaluator tests
  test_filters.py     # Filter tests
  test_exceptions.py  # Exception tests
```

## Code Style Guidelines

### Imports

```python
# Standard library first
import re
import copy
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto

# Third-party
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Local imports (relative)
from .parser import parse_cell, is_control_statement
from .expressions import evaluate_expression
from .exceptions import TemplateSyntaxError
```

### Type Hints

- Use type hints for all function signatures
- Use `Optional[X]` for nullable types
- Use `Dict[str, Any]` for context/data dictionaries
- Use `List[X]` for lists, `Tuple[X, Y]` for tuples

```python
def render_template(
    template_path: str,
    data: Dict[str, Any],
    sheets: Optional[List[str]] = None
) -> None:
```

### Naming Conventions

- **Functions/methods**: `snake_case` - `render_template`, `_process_rows`
- **Private functions**: prefix with `_` - `_render_sheet`, `_copy_cell_style`
- **Classes**: `PascalCase` - `LoopContext`, `ExpressionEvaluator`
- **Constants**: `UPPER_SNAKE_CASE` - `VARIABLE_PATTERN`, `OPERATORS`
- **Variables**: `snake_case` - `row_idx`, `cell_data`

### Docstrings

Use triple-quoted docstrings with Args/Returns sections:

```python
def resolve_path(data: Dict[str, Any], path: str) -> Any:
    """
    Resolve a dotted path with optional index access from data.
    
    Examples:
        - "name" -> data["name"]
        - "item.name" -> data["item"]["name"]
    
    Args:
        data: Dictionary containing the data
        path: Dotted path string
    
    Returns:
        The resolved value, or None if path cannot be resolved.
    """
```

### Error Handling

- Use custom exceptions from `exceptions.py`
- `TemplateSyntaxError` for invalid template syntax
- `TemplateRenderError` for runtime rendering errors
- Include row/col info when available

```python
raise TemplateSyntaxError(f"Missing {{% endfor %}}", row=row_idx + 1)
raise TemplateRenderError(f"Sheet '{sheet_name}' not found")
```

### Regex Patterns

Define patterns as module-level constants:

```python
VARIABLE_PATTERN = re.compile(r'\{\{\s*(.+?)\s*\}\}')
CONTROL_PATTERN = re.compile(r'^\s*\{%\s*(.+?)\s*%\}\s*$')
FOR_START_PATTERN = re.compile(r'^for\s+(\w+)\s+in\s+(.+)$')
```

### Testing Patterns

- Use pytest fixtures and classes for organization
- Create temporary files with `tempfile.mkstemp()`
- Always clean up temp files in `finally` blocks
- Use descriptive test names in Korean when appropriate

```python
class TestVariableSubstitution:
    def test_simple_variable(self):
        template_path = create_template([["{{ name }}"]])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template_to_file(template_path, output_path, {"name": "value"})
            result = read_output(output_path)
            assert result == [["value"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
```

## Template Syntax Reference

```
Variables:     {{ name }}, {{ item.price }}, {{ price * 1.1 }}
For loops:     {% for item in items %}...{% endfor %}
Conditionals:  {% if cond %}...{% elif cond %}...{% else %}...{% endif %}
Set:           {% set var = value %}
Comments:      {# comment #}
Filters:       {{ value|default('N/A') }}, {{ items|length }}
Ternary:       {{ 'yes' if active else 'no' }}
Loop vars:     {{ loop.index }}, {{ loop.first }}, {{ loop.last }}
```

## Key Implementation Notes

1. **Control statements must be in column A** - The first cell of a row determines if it's a control row
2. **Rich Text preservation** - Use `rich_text=True` when loading workbooks
3. **Merged cells** - Cannot span control statement rows
4. **Style copying** - Use `copy.copy()` for openpyxl style objects
5. **Index conventions** - Internal processing uses 0-based; openpyxl uses 1-based

## Dependencies

- `openpyxl>=3.1.0` - Excel file handling
- `pytest>=7.0.0` (dev) - Testing
- `pytest-cov>=4.0.0` (dev) - Coverage

---

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: `npx openskills read <skill-name>` (run in your shell)
  - For multiple: `npx openskills read skill-one,skill-two`
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>xlsx</name>
<description>Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. Use when working with .xlsx files.</description>
<location>project</location>
</skill>

<skill>
<name>commit</name>
<description>Create commit messages following Sentry conventions. Use when committing code changes.</description>
<location>project</location>
</skill>

<skill>
<name>code-review</name>
<description>Perform code reviews following Sentry engineering practices.</description>
<location>project</location>
</skill>

<skill>
<name>create-pr</name>
<description>Create pull requests following Sentry conventions.</description>
<location>project</location>
</skill>

<skill>
<name>find-bugs</name>
<description>Find bugs, security vulnerabilities, and code quality issues in local branch changes.</description>
<location>project</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
