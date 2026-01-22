"""Tests for template renderer"""

import pytest
import tempfile
import os
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

from xls_template_renderer import render_template
from xls_template_renderer.exceptions import TemplateSyntaxError


def create_template(rows_data: list) -> str:
    """Create a temporary template file with given row data."""
    wb = Workbook()
    ws = wb.active
    
    for row_idx, row in enumerate(rows_data, start=1):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    fd, path = tempfile.mkstemp(suffix='.xlsx')
    os.close(fd)
    wb.save(path)
    return path


def read_output(path: str) -> list:
    """Read all cell values from output file."""
    wb = load_workbook(path)
    ws = wb.active
    
    result = []
    for row in ws.iter_rows(values_only=True):
        # Filter out completely empty rows
        if any(cell is not None for cell in row):
            # Remove trailing None values
            row_list = list(row)
            while row_list and row_list[-1] is None:
                row_list.pop()
            result.append(row_list)
    return result


class TestVariableSubstitution:
    """Tests for variable substitution"""
    
    def test_simple_variable(self):
        template_path = create_template([
            ["{{ name }}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "홍길동"})
            result = read_output(output_path)
            assert result == [["홍길동"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_mixed_text_and_variable(self):
        template_path = create_template([
            ["이름: {{ name }}님"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "홍길동"})
            result = read_output(output_path)
            assert result == [["이름: 홍길동님"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_multiple_variables_in_cell(self):
        template_path = create_template([
            ["{{ name }} ({{ age }}세)"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "홍길동", "age": 25})
            result = read_output(output_path)
            assert result == [["홍길동 (25세)"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_missing_variable_kept(self):
        template_path = create_template([
            ["{{ unknown }}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {})
            result = read_output(output_path)
            assert result == [["{{ unknown }}"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_nested_variable(self):
        template_path = create_template([
            ["{{ user.name }}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"user": {"name": "홍길동"}})
            result = read_output(output_path)
            assert result == [["홍길동"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_arithmetic_expression(self):
        template_path = create_template([
            ["{{ price * 1.1 }}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"price": 1000})
            result = read_output(output_path)
            assert result == [[1100.0]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestForLoop:
    """Tests for for loop"""
    
    def test_simple_for_loop(self):
        template_path = create_template([
            ["{% for item in items %}"],
            ["", "{{ item }}"],
            ["{% endfor %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"items": ["A", "B", "C"]})
            result = read_output(output_path)
            assert result == [
                [None, "A"],
                [None, "B"],
                [None, "C"]
            ]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_for_loop_with_dict_items(self):
        template_path = create_template([
            ["{% for item in items %}"],
            ["", "{{ item.name }}", "{{ item.price }}"],
            ["{% endfor %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            data = {
                "items": [
                    {"name": "상품A", "price": 1000},
                    {"name": "상품B", "price": 2000}
                ]
            }
            render_template(template_path, output_path, data)
            result = read_output(output_path)
            assert result == [
                [None, "상품A", 1000],
                [None, "상품B", 2000]
            ]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_empty_list(self):
        template_path = create_template([
            ["Header"],
            ["{% for item in items %}"],
            ["", "{{ item }}"],
            ["{% endfor %}"],
            ["Footer"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"items": []})
            result = read_output(output_path)
            assert result == [["Header"], ["Footer"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_nested_for_loop(self):
        template_path = create_template([
            ["{% for dept in departments %}"],
            ["", "{{ dept.name }}"],
            ["{% for member in dept.members %}"],
            ["", "", "{{ member }}"],
            ["{% endfor %}"],
            ["{% endfor %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            data = {
                "departments": [
                    {"name": "개발팀", "members": ["김철수", "이영희"]},
                    {"name": "기획팀", "members": ["박지민"]}
                ]
            }
            render_template(template_path, output_path, data)
            result = read_output(output_path)
            assert result == [
                [None, "개발팀"],
                [None, None, "김철수"],
                [None, None, "이영희"],
                [None, "기획팀"],
                [None, None, "박지민"]
            ]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestIfStatement:
    """Tests for if statement"""
    
    def test_if_true(self):
        template_path = create_template([
            ["{% if show %}"],
            ["", "표시됨"],
            ["{% endif %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"show": True})
            result = read_output(output_path)
            assert result == [[None, "표시됨"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_if_false(self):
        template_path = create_template([
            ["{% if show %}"],
            ["", "표시됨"],
            ["{% endif %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"show": False})
            result = read_output(output_path)
            assert result == []
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_if_else(self):
        template_path = create_template([
            ["{% if show %}"],
            ["", "YES"],
            ["{% else %}"],
            ["", "NO"],
            ["{% endif %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"show": False})
            result = read_output(output_path)
            assert result == [[None, "NO"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_if_elif_else(self):
        template_path = create_template([
            ["{% if status == 1 %}"],
            ["", "상태1"],
            ["{% elif status == 2 %}"],
            ["", "상태2"],
            ["{% else %}"],
            ["", "기타"],
            ["{% endif %}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            # Test status == 1
            render_template(template_path, output_path, {"status": 1})
            assert read_output(output_path) == [[None, "상태1"]]
            
            # Test status == 2
            render_template(template_path, output_path, {"status": 2})
            assert read_output(output_path) == [[None, "상태2"]]
            
            # Test else
            render_template(template_path, output_path, {"status": 3})
            assert read_output(output_path) == [[None, "기타"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestComments:
    """Tests for comments"""
    
    def test_comment_removed(self):
        template_path = create_template([
            ["Header"],
            ["{# 이것은 주석입니다 #}"],
            ["Footer"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {})
            result = read_output(output_path)
            assert result == [["Header"], ["Footer"]]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestStylePreservation:
    """Tests for style preservation"""
    
    def test_font_preserved(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ name }}"
        ws['A1'].font = Font(bold=True, size=14, color="FF0000")
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "홍길동"})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            assert ws_out['A1'].value == "홍길동"
            assert ws_out['A1'].font.bold is True
            assert ws_out['A1'].font.size == 14
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_fill_preserved(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ value }}"
        ws['A1'].fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"value": "테스트"})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            assert ws_out['A1'].value == "테스트"
            assert ws_out['A1'].fill.start_color.rgb == "00FFFF00"
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_border_preserved(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ value }}"
        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        ws['A1'].border = thin_border
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"value": "테두리 테스트"})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            assert ws_out['A1'].value == "테두리 테스트"
            assert ws_out['A1'].border.left.style == 'thin'
            assert ws_out['A1'].border.right.style == 'thin'
            assert ws_out['A1'].border.top.style == 'thin'
            assert ws_out['A1'].border.bottom.style == 'thin'
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_alignment_preserved(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ value }}"
        ws['A1'].alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"value": "정렬 테스트"})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            assert ws_out['A1'].value == "정렬 테스트"
            assert ws_out['A1'].alignment.horizontal == 'center'
            assert ws_out['A1'].alignment.vertical == 'top'
            assert ws_out['A1'].alignment.wrap_text is True
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_number_format_preserved(self):
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ price }}"
        ws['A1'].number_format = '#,##0'
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"price": 1234567})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            assert ws_out['A1'].value == 1234567
            assert ws_out['A1'].number_format == '#,##0'
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_style_preserved_in_for_loop(self):
        """for loop 내에서 스타일이 복제되는지 테스트"""
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{% for item in items %}"
        # 본문 행
        ws['B2'] = "{{ item.name }}"
        ws['B2'].font = Font(bold=True, color="0000FF")
        ws['B2'].fill = PatternFill(start_color="FFFF00", fill_type="solid")
        ws['C2'] = "{{ item.price }}"
        ws['C2'].number_format = '#,##0'
        ws['C2'].alignment = Alignment(horizontal='right')
        ws['A3'] = "{% endfor %}"
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            data = {
                "items": [
                    {"name": "상품A", "price": 1000},
                    {"name": "상품B", "price": 2000},
                    {"name": "상품C", "price": 3000}
                ]
            }
            render_template(template_path, output_path, data)
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            # 3개 행 모두 스타일이 유지되어야 함
            for row_idx in range(1, 4):
                # name 열 스타일 확인
                name_cell = ws_out.cell(row=row_idx, column=2)
                assert name_cell.font.bold is True
                assert name_cell.fill.start_color.rgb == "00FFFF00"
                
                # price 열 스타일 확인
                price_cell = ws_out.cell(row=row_idx, column=3)
                assert price_cell.number_format == '#,##0'
                assert price_cell.alignment.horizontal == 'right'
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_multiple_styles_combined(self):
        """여러 스타일이 함께 적용된 셀 테스트"""
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "{{ value }}"
        ws['A1'].font = Font(bold=True, italic=True, size=12)
        ws['A1'].fill = PatternFill(start_color="00FF00", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].border = Border(
            left=Side(style='thick', color='FF0000'),
            bottom=Side(style='double', color='0000FF')
        )
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"value": "복합 스타일"})
            
            wb_out = load_workbook(output_path)
            ws_out = wb_out.active
            
            cell = ws_out['A1']
            assert cell.value == "복합 스타일"
            assert cell.font.bold is True
            assert cell.font.italic is True
            assert cell.font.size == 12
            assert cell.fill.start_color.rgb == "0000FF00"
            assert cell.alignment.horizontal == 'center'
            assert cell.alignment.vertical == 'center'
            assert cell.border.left.style == 'thick'
            assert cell.border.bottom.style == 'double'
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestComplexTemplate:
    """Tests for complex templates"""
    
    def test_mixed_template(self):
        """Test a template with for loop, if, and variables"""
        template_path = create_template([
            ["리포트: {{ title }}"],
            ["{# 상품 목록 #}"],
            ["{% for item in items %}"],
            ["{% if item.active %}"],
            ["", "{{ item.name }}", "{{ item.price }}"],
            ["{% endif %}"],
            ["{% endfor %}"],
            ["합계", "", "{{ total }}"]
        ])
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            data = {
                "title": "월간 리포트",
                "items": [
                    {"name": "상품A", "price": 1000, "active": True},
                    {"name": "상품B", "price": 2000, "active": False},
                    {"name": "상품C", "price": 3000, "active": True}
                ],
                "total": 4000
            }
            render_template(template_path, output_path, data)
            result = read_output(output_path)
            
            assert result == [
                ["리포트: 월간 리포트"],
                [None, "상품A", 1000],
                [None, "상품C", 3000],
                ["합계", None, 4000]
            ]
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestRichTextPreservation:
    """Tests for Rich Text (partial formatting) preservation"""
    
    def test_rich_text_variable_formatting_preserved(self):
        """변수 부분에 적용된 서식이 유지되는지 테스트"""
        wb = Workbook()
        ws = wb.active
        
        # "이름: " + "{{ name }}"(파란색 볼드) + "님"
        rich_text = CellRichText(
            "이름: ",
            TextBlock(InlineFont(b=True, color="0000FF"), "{{ name }}"),
            "님"
        )
        ws['A1'] = rich_text
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "홍길동"})
            
            wb_out = load_workbook(output_path, rich_text=True)
            ws_out = wb_out.active
            
            result = ws_out['A1'].value
            assert isinstance(result, CellRichText), f"Expected CellRichText, got {type(result)}"
            
            # 전체 텍스트 확인
            assert str(result) == "이름: 홍길동님"
            
            # 서식 확인: 두 번째 파트가 볼드+파란색
            parts = list(result)
            assert len(parts) == 3
            assert parts[0] == "이름: "
            assert isinstance(parts[1], TextBlock)
            assert parts[1].text == "홍길동"
            assert parts[1].font.b is True  # bold
            assert parts[2] == "님"
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_rich_text_multiple_variables(self):
        """Rich Text 내 여러 변수 치환 테스트"""
        wb = Workbook()
        ws = wb.active
        
        # "{{ name }}"(빨간색) + " - " + "{{ title }}"(볼드)
        rich_text = CellRichText(
            TextBlock(InlineFont(color="FF0000"), "{{ name }}"),
            " - ",
            TextBlock(InlineFont(b=True), "{{ title }}")
        )
        ws['A1'] = rich_text
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {"name": "김철수", "title": "개발자"})
            
            wb_out = load_workbook(output_path, rich_text=True)
            ws_out = wb_out.active
            
            result = ws_out['A1'].value
            assert isinstance(result, CellRichText)
            assert str(result) == "김철수 - 개발자"
            
            parts = list(result)
            assert len(parts) == 3
            assert isinstance(parts[0], TextBlock)
            assert parts[0].text == "김철수"
            assert parts[1] == " - "
            assert isinstance(parts[2], TextBlock)
            assert parts[2].text == "개발자"
            assert parts[2].font.b is True
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_rich_text_in_for_loop(self):
        """for loop 내 Rich Text 서식 유지 테스트"""
        wb = Workbook()
        ws = wb.active
        
        ws['A1'] = "{% for item in items %}"
        # Rich Text: "상품: " + "{{ item.name }}"(볼드)
        rich_text = CellRichText(
            "상품: ",
            TextBlock(InlineFont(b=True, color="008000"), "{{ item.name }}")
        )
        ws['B2'] = rich_text
        ws['A3'] = "{% endfor %}"
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            data = {
                "items": [
                    {"name": "사과"},
                    {"name": "바나나"},
                    {"name": "오렌지"}
                ]
            }
            render_template(template_path, output_path, data)
            
            wb_out = load_workbook(output_path, rich_text=True)
            ws_out = wb_out.active
            
            # 3개 행 모두 Rich Text 서식 유지 확인
            expected_names = ["사과", "바나나", "오렌지"]
            for row_idx, expected_name in enumerate(expected_names, start=1):
                result = ws_out.cell(row=row_idx, column=2).value
                assert isinstance(result, CellRichText), f"Row {row_idx}: Expected CellRichText"
                assert str(result) == f"상품: {expected_name}"
                
                parts = list(result)
                assert isinstance(parts[1], TextBlock)
                assert parts[1].text == expected_name
                assert parts[1].font.b is True
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_rich_text_no_variables(self):
        """변수 없는 Rich Text가 그대로 유지되는지 테스트"""
        wb = Workbook()
        ws = wb.active
        
        rich_text = CellRichText(
            "일반 텍스트 ",
            TextBlock(InlineFont(b=True), "볼드 텍스트")
        )
        ws['A1'] = rich_text
        
        fd, template_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(template_path)
        
        output_path = template_path.replace('.xlsx', '_out.xlsx')
        
        try:
            render_template(template_path, output_path, {})
            
            wb_out = load_workbook(output_path, rich_text=True)
            ws_out = wb_out.active
            
            result = ws_out['A1'].value
            assert isinstance(result, CellRichText)
            assert str(result) == "일반 텍스트 볼드 텍스트"
        finally:
            os.unlink(template_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
