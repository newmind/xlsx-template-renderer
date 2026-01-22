"""
예제: Rich Text 및 복잡한 서식을 포함한 고급 템플릿 사용법
"""

from pathlib import Path
from openpyxl import Workbook, load_workbook  # type: ignore[import-untyped]
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment  # type: ignore[import-untyped]
from openpyxl.cell.rich_text import CellRichText, TextBlock  # type: ignore[import-untyped]
from openpyxl.cell.text import InlineFont  # type: ignore[import-untyped]

from xls_template_renderer import render_template


def create_advanced_template():
    """Rich Text 및 복잡한 서식을 포함한 고급 템플릿 생성"""
    wb = Workbook()
    ws = wb.active
    ws.title = "직원 리포트"
    
    # 스타일 정의
    title_font = Font(bold=True, size=16, color="1F4E79")
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(bold=True, size=11, color="FFFFFF")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    thick_border = Border(
        left=Side(style='medium'),
        right=Side(style='medium'),
        top=Side(style='medium'),
        bottom=Side(style='medium')
    )
    center_align = Alignment(horizontal='center', vertical='center')
    
    # === 제목 섹션 ===
    ws['A1'] = "{{ company_name }} 직원 현황 리포트"
    ws['A1'].font = title_font
    
    # Rich Text: "작성일: "(일반) + "{{ report_date }}"(볼드+파란색)
    rich_date = CellRichText(
        "작성일: ",
        TextBlock(InlineFont(b=True, color="0066CC"), "{{ report_date }}")
    )
    ws['A2'] = rich_date
    
    # 주석
    ws['A3'] = "{# 아래부터 부서별 직원 목록 #}"
    
    # === 부서별 반복 (중첩 for 루프) ===
    ws['A4'] = "{% for dept in departments %}"
    
    # 부서명 (Rich Text)
    dept_name_rich = CellRichText(
        TextBlock(InlineFont(b=True, sz="14", color="2E75B6"), "📁 {{ dept.name }}")
    )
    ws['B5'] = dept_name_rich
    ws['B5'].fill = PatternFill(start_color="DDEBF7", fill_type="solid")
    
    # 조건부: 부서 설명이 있으면 표시
    ws['A6'] = "{% if dept.description %}"
    
    # Rich Text: "설명: "(일반) + "{{ dept.description }}"(이탤릭+회색)
    desc_rich = CellRichText(
        "설명: ",
        TextBlock(InlineFont(i=True, color="666666"), "{{ dept.description }}")
    )
    ws['B7'] = desc_rich
    
    ws['A8'] = "{% endif %}"
    
    # 직원 테이블 헤더
    ws['B9'] = "이름"
    ws['C9'] = "직책"
    ws['D9'] = "급여"
    ws['E9'] = "상태"
    
    for col in ['B', 'C', 'D', 'E']:
        cell = ws[f'{col}9']
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = center_align
    
    # 직원 반복
    ws['A10'] = "{% for emp in dept.employees %}"
    
    # 직원 데이터 행 - Rich Text로 이름 표시 (성은 볼드)
    emp_name_rich = CellRichText(
        TextBlock(InlineFont(b=True), "{{ emp.last_name }}"),
        " {{ emp.first_name }}"
    )
    ws['B11'] = emp_name_rich
    ws['B11'].border = border
    
    ws['C11'] = "{{ emp.position }}"
    ws['C11'].border = border
    
    ws['D11'] = "{{ emp.salary }}"
    ws['D11'].border = border
    ws['D11'].number_format = '#,##0원'
    ws['D11'].alignment = Alignment(horizontal='right')
    
    # 상태 표시
    ws['E11'] = "{{ emp.status }}"
    ws['E11'].border = border
    ws['E11'].alignment = center_align
    
    ws['A12'] = "{% endfor %}"
    
    # 부서 요약 - Rich Text
    summary_rich = CellRichText(
        "총 ",
        TextBlock(InlineFont(b=True, color="C65911"), "{{ dept.employee_count }}"),
        "명, 평균 급여: ",
        TextBlock(InlineFont(b=True, color="2E75B6"), "{{ dept.avg_salary }}")
    )
    ws['B13'] = summary_rich
    ws['B13'].fill = PatternFill(start_color="FCE4D6", fill_type="solid")
    
    # 빈 행 (부서 간 구분)
    ws['A14'] = ""
    
    ws['A15'] = "{% endfor %}"
    
    # === 전체 요약 섹션 ===
    ws['A16'] = "=== 전체 요약 ==="
    ws['A16'].font = Font(bold=True, size=12)
    
    # Rich Text: 총 직원 수
    total_rich = CellRichText(
        "전체 직원: ",
        TextBlock(InlineFont(b=True, sz="14", color="FF0000"), "{{ total_employees }}"),
        "명"
    )
    ws['A17'] = total_rich
    
    # 열 너비 조정
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    
    # 저장
    template_path = Path(__file__).parent / "advanced_template.xlsx"
    wb.save(template_path)
    print(f"고급 템플릿 생성됨: {template_path}")
    return template_path


def main():
    # 템플릿 생성
    template_path = create_advanced_template()
    output_path = Path(__file__).parent / "advanced_output.xlsx"
    
    # 렌더링할 데이터
    data = {
        "company_name": "메이크스타",
        "report_date": "2024-01-20",
        "departments": [
            {
                "name": "개발팀",
                "description": "소프트웨어 개발 및 유지보수 담당",
                "employees": [
                    {"last_name": "김", "first_name": "철수", "position": "시니어 개발자", "hire_date": "2020-03-15", "salary": 7500000, "status": "재직"},
                    {"last_name": "이", "first_name": "영희", "position": "주니어 개발자", "hire_date": "2022-07-01", "salary": 4500000, "status": "재직"},
                    {"last_name": "박", "first_name": "민수", "position": "테크 리드", "hire_date": "2018-01-10", "salary": 9000000, "status": "재직"},
                ],
                "employee_count": 3,
                "avg_salary": "7,000,000원"
            },
            {
                "name": "기획팀",
                "description": None,  # 설명 없음 - if 조건 테스트
                "employees": [
                    {"last_name": "정", "first_name": "지민", "position": "PM", "hire_date": "2019-05-20", "salary": 6500000, "status": "재직"},
                    {"last_name": "최", "first_name": "수진", "position": "기획자", "hire_date": "2021-09-01", "salary": 5000000, "status": "휴직"},
                ],
                "employee_count": 2,
                "avg_salary": "5,750,000원"
            },
            {
                "name": "디자인팀",
                "description": "UI/UX 디자인 전담",
                "employees": [
                    {"last_name": "한", "first_name": "예린", "position": "UI 디자이너", "hire_date": "2021-02-15", "salary": 5500000, "status": "재직"},
                ],
                "employee_count": 1,
                "avg_salary": "5,500,000원"
            }
        ],
        "total_employees": 6
    }
    
    # 렌더링 실행
    render_template(str(template_path), str(output_path), data)
    print(f"렌더링 완료: {output_path}")
    
    # 결과 확인
    wb = load_workbook(output_path, rich_text=True)
    ws = wb.active
    
    print("\n=== 렌더링 결과 (텍스트만) ===")
    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True), start=1):
        # None이 아닌 값만 출력
        row_str = [str(cell) if cell else "" for cell in row]
        if any(row_str):
            print(f"Row {row_idx}: {row_str}")
    
    # Rich Text 확인
    print("\n=== Rich Text 확인 ===")
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for cell in row:
            if isinstance(cell.value, CellRichText):
                print(f"{cell.coordinate}: Rich Text - '{str(cell.value)}'")


if __name__ == "__main__":
    main()
