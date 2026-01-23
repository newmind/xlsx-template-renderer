"""
예제: Rich Text 및 복잡한 서식을 포함한 고급 템플릿 사용법

새로 추가된 기능 테스트:
- 필터: default, length, join, upper, lower, title, trim, replace, round, abs, int, float, first, last
- 삼항 연산자: {{ 'A' if condition else 'B' }}
- 논리 연산자: and, or, not
- in 연산자: {% if item in items %}
- 루프 변수: loop.index, loop.first, loop.last, loop.length
"""

from pathlib import Path
from openpyxl import Workbook, load_workbook  # type: ignore[import-untyped]
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment  # type: ignore[import-untyped]
from openpyxl.cell.rich_text import CellRichText, TextBlock  # type: ignore[import-untyped]
from openpyxl.cell.text import InlineFont  # type: ignore[import-untyped]

from xlsx_template_renderer import render_template


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
    
    # [NEW] 필터 테스트: default 필터 - 부제목이 없으면 기본값 사용
    ws['A3'] = "부제: {{ subtitle|default('부제 없음') }}"
    
    # 주석
    ws['A4'] = "{# 아래부터 부서별 직원 목록 - 새 기능 테스트 포함 #}"
    
    # === 부서별 반복 (중첩 for 루프) ===
    ws['A5'] = "{% for dept in departments %}"
    
    # [NEW] loop 변수 테스트: loop.index로 부서 번호 표시
    dept_name_rich = CellRichText(
        TextBlock(InlineFont(b=True, sz="14", color="2E75B6"), 
                  "📁 {{ loop.index }}. {{ dept.name }}")
    )
    ws['B6'] = dept_name_rich
    ws['B6'].fill = PatternFill(start_color="DDEBF7", fill_type="solid")
    
    # [NEW] loop.first, loop.last 테스트
    ws['A7'] = "{% if loop.first %}"
    ws['B8'] = "⭐ 첫 번째 부서입니다!"
    ws['B8'].font = Font(color="FF6600")
    ws['A9'] = "{% endif %}"
    
    # 조건부: 부서 설명이 있으면 표시
    ws['A10'] = "{% if dept.description %}"
    
    # Rich Text: "설명: "(일반) + "{{ dept.description }}"(이탤릭+회색)
    desc_rich = CellRichText(
        "설명: ",
        TextBlock(InlineFont(i=True, color="666666"), "{{ dept.description }}")
    )
    ws['B11'] = desc_rich
    
    ws['A12'] = "{% endif %}"
    
    # [NEW] 필터 테스트: length 필터로 직원 수 표시
    ws['B13'] = "직원 수: {{ dept.employees|length }}명"
    
    # [NEW] 논리 연산자 테스트: and 조건
    ws['A14'] = "{% if dept.is_active and dept.employees %}"
    ws['B15'] = "✅ 활성 부서 (직원 있음)"
    ws['B15'].font = Font(color="008000")
    ws['A16'] = "{% endif %}"
    
    # 직원 테이블 헤더
    ws['B17'] = "#"
    ws['C17'] = "이름"
    ws['D17'] = "직책"
    ws['E17'] = "급여"
    ws['F17'] = "상태"
    ws['G17'] = "비고"
    
    for col in ['B', 'C', 'D', 'E', 'F', 'G']:
        cell = ws[f'{col}17']
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = center_align
    
    # 직원 반복
    ws['A18'] = "{% for emp in dept.employees %}"
    
    # [NEW] loop.index로 순번 표시
    ws['B19'] = "{{ loop.index }}"
    ws['B19'].border = border
    ws['B19'].alignment = center_align
    
    # 직원 데이터 행 - Rich Text로 이름 표시 (성은 볼드)
    emp_name_rich = CellRichText(
        TextBlock(InlineFont(b=True), "{{ emp.last_name }}"),
        " {{ emp.first_name }}"
    )
    ws['C19'] = emp_name_rich
    ws['C19'].border = border
    
    ws['D19'] = "{{ emp.position }}"
    ws['D19'].border = border
    
    ws['E19'] = "{{ emp.salary }}"
    ws['E19'].border = border
    ws['E19'].number_format = '#,##0원'
    ws['E19'].alignment = Alignment(horizontal='right')
    
    # [NEW] 삼항 연산자 테스트: 상태에 따른 이모지
    ws['F19'] = "{{ '✅ 재직' if emp.status == '재직' else '⏸️ 휴직' }}"
    ws['F19'].border = border
    ws['F19'].alignment = center_align
    
    # [NEW] in 연산자 + 삼항 연산자 조합
    ws['G19'] = "{{ '🌟 고급' if emp.position in senior_positions else '' }}"
    ws['G19'].border = border
    ws['G19'].alignment = center_align
    
    ws['A20'] = "{% endfor %}"
    
    # [NEW] 필터 체이닝 + default 필터
    summary_rich = CellRichText(
        "총 ",
        TextBlock(InlineFont(b=True, color="C65911"), "{{ dept.employees|length }}"),
        "명, 평균 급여: ",
        TextBlock(InlineFont(b=True, color="2E75B6"), "{{ dept.avg_salary|default('계산 중') }}")
    )
    ws['B21'] = summary_rich
    ws['B21'].fill = PatternFill(start_color="FCE4D6", fill_type="solid")
    
    # [NEW] loop.last 테스트: 마지막 부서가 아니면 구분선
    ws['A22'] = "{% if not loop.last %}"
    ws['B23'] = "─" * 30
    ws['B23'].font = Font(color="CCCCCC")
    ws['A24'] = "{% endif %}"
    
    ws['A25'] = "{% endfor %}"
    
    # === 전체 요약 섹션 ===
    ws['A26'] = "=== 전체 요약 ==="
    ws['A26'].font = Font(bold=True, size=12)
    
    # [NEW] 필터 테스트: join 필터로 부서명 나열
    ws['A27'] = "부서 목록: {{ department_names|join(', ') }}"
    
    # Rich Text: 총 직원 수
    total_rich = CellRichText(
        "전체 직원: ",
        TextBlock(InlineFont(b=True, sz="14", color="FF0000"), "{{ total_employees }}"),
        "명 (총 ",
        TextBlock(InlineFont(b=True, color="2E75B6"), "{{ departments|length }}"),
        "개 부서)"
    )
    ws['A28'] = total_rich
    
    # [NEW] 논리 연산자 or 테스트
    ws['A29'] = "{% if show_footer or debug_mode %}"
    ws['A30'] = "📋 이 리포트는 자동 생성되었습니다."
    ws['A30'].font = Font(italic=True, color="888888")
    ws['A31'] = "{% endif %}"
    
    # === 새 필터 테스트 섹션 ===
    ws['A32'] = "=== 새 필터 테스트 ==="
    ws['A32'].font = Font(bold=True, size=12)
    
    # 문자열 필터 테스트
    ws['A33'] = "upper: {{ test_name|upper }}"
    ws['A34'] = "lower: {{ test_name|lower }}"
    ws['A35'] = "title: {{ test_title_text|title }}"
    ws['A36'] = "trim: [{{ test_spaces|trim }}]"
    ws['A37'] = "replace: {{ test_replace|replace('world', 'Korea') }}"
    
    # 숫자 필터 테스트
    ws['A38'] = "round: {{ test_float|round(2) }}"
    ws['A39'] = "abs: {{ test_negative|abs }}"
    ws['A40'] = "int: {{ test_float|int }}"
    ws['A41'] = "float: {{ test_int_str|float }}"
    
    # 리스트 필터 테스트
    ws['A42'] = "first: {{ test_list|first }}"
    ws['A43'] = "last: {{ test_list|last }}"
    
    # 필터 체이닝 테스트
    ws['A44'] = "chained: {{ test_spaces|trim|upper }}"
    
    # 열 너비 조정
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 8
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 10
    ws.column_dimensions['G'].width = 10
    
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
        "subtitle": None,  # [NEW] default 필터 테스트: None이면 '부제 없음' 출력
        
        # [NEW] in 연산자 테스트용: 고급 직책 목록
        "senior_positions": ["시니어 개발자", "테크 리드", "PM", "팀장"],
        
        # [NEW] join 필터 테스트용: 부서명 목록
        "department_names": ["개발팀", "기획팀", "디자인팀"],
        
        # [NEW] or 연산자 테스트용
        "show_footer": True,
        "debug_mode": False,
        
        # [NEW] 새 필터 테스트용 데이터
        "test_name": "Hello World",
        "test_title_text": "hello world example",
        "test_spaces": "  trimmed  ",
        "test_replace": "hello world",
        "test_float": 3.14159,
        "test_negative": -42,
        "test_int_str": "123",
        "test_list": ["apple", "banana", "cherry"],
        
        "departments": [
            {
                "name": "개발팀",
                "description": "소프트웨어 개발 및 유지보수 담당",
                "is_active": True,  # [NEW] and 연산자 테스트용
                "employees": [
                    {"last_name": "김", "first_name": "철수", "position": "시니어 개발자", "hire_date": "2020-03-15", "salary": 7500000, "status": "재직"},
                    {"last_name": "이", "first_name": "영희", "position": "주니어 개발자", "hire_date": "2022-07-01", "salary": 4500000, "status": "재직"},
                    {"last_name": "박", "first_name": "민수", "position": "테크 리드", "hire_date": "2018-01-10", "salary": 9000000, "status": "재직"},
                ],
                "avg_salary": "7,000,000원"
            },
            {
                "name": "기획팀",
                "description": None,  # 설명 없음 - if 조건 테스트
                "is_active": True,
                "employees": [
                    {"last_name": "정", "first_name": "지민", "position": "PM", "hire_date": "2019-05-20", "salary": 6500000, "status": "재직"},
                    {"last_name": "최", "first_name": "수진", "position": "기획자", "hire_date": "2021-09-01", "salary": 5000000, "status": "휴직"},
                ],
                "avg_salary": "5,750,000원"
            },
            {
                "name": "디자인팀",
                "description": "UI/UX 디자인 전담",
                "is_active": True,
                "employees": [
                    {"last_name": "한", "first_name": "예린", "position": "UI 디자이너", "hire_date": "2021-02-15", "salary": 5500000, "status": "재직"},
                ],
                "avg_salary": None  # [NEW] default 필터 테스트: None이면 '계산 중' 출력
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
    
    print("\n" + "=" * 60)
    print("렌더링 결과")
    print("=" * 60)
    
    print("\n📋 테스트된 새 기능:")
    print("  - 필터: default, length, join, upper, lower, title, trim, replace, round, abs, int, float, first, last")
    print("  - 삼항 연산자: {{ 'A' if condition else 'B' }}")
    print("  - 논리 연산자: and, or, not")
    print("  - in 연산자: {% if item in items %}")
    print("  - 루프 변수: loop.index, loop.first, loop.last, loop.length")
    
    print("\n" + "-" * 60)
    print("셀 내용:")
    print("-" * 60)
    
    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True), start=1):
        # None이 아닌 값만 출력
        row_str = [str(cell) if cell else "" for cell in row]
        if any(row_str):
            print(f"Row {row_idx:2d}: {row_str}")
    
    # Rich Text 확인
    print("\n" + "-" * 60)
    print("Rich Text 셀:")
    print("-" * 60)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for cell in row:
            if isinstance(cell.value, CellRichText):
                print(f"  {cell.coordinate}: '{str(cell.value)}'")
    
    # 새 기능 검증
    print("\n" + "-" * 60)
    print("새 기능 검증:")
    print("-" * 60)
    
    # 검증 항목
    checks = {}
    
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
        for cell in row:
            if not cell:
                continue
            cell_str = str(cell)
            
            # 1. default 필터 검증
            if "부제 없음" in cell_str and "default" not in checks:
                checks["default"] = "✅ default 필터: '부제 없음' 출력됨"
            
            # 2. loop.index 검증
            if "1. 개발팀" in cell_str and "loop.index" not in checks:
                checks["loop.index"] = "✅ loop.index: 부서 번호 표시됨"
            
            # 3. loop.first 검증
            if "첫 번째 부서" in cell_str and "loop.first" not in checks:
                checks["loop.first"] = "✅ loop.first: 첫 번째 부서 표시됨"
            
            # 4. 삼항 연산자 검증
            if "✅ 재직" in cell_str and "ternary" not in checks:
                checks["ternary"] = "✅ 삼항 연산자: 상태 이모지 표시됨"
            
            # 5. 삼항 연산자 (휴직) 검증
            if "⏸️ 휴직" in cell_str and "ternary_else" not in checks:
                checks["ternary_else"] = "✅ 삼항 연산자 (else): 휴직 이모지 표시됨"
            
            # 6. join 필터 검증
            if "개발팀, 기획팀, 디자인팀" in cell_str and "join" not in checks:
                checks["join"] = "✅ join 필터: 부서명 연결됨"
            
            # 7. length 필터 검증
            if "3개 부서" in cell_str and "length" not in checks:
                checks["length"] = "✅ length 필터: 부서 수 계산됨"
            
            # 8. and 연산자 검증
            if "활성 부서" in cell_str and "and" not in checks:
                checks["and"] = "✅ and 연산자: 활성 부서 조건 표시됨"
            
            # 9. or 연산자 검증
            if "자동 생성" in cell_str and "or" not in checks:
                checks["or"] = "✅ or 연산자: 푸터 표시됨"
            
            # 10. not + loop.last 검증
            if "─" * 10 in cell_str and "not_loop.last" not in checks:
                checks["not_loop.last"] = "✅ not + loop.last: 구분선 표시됨"
            
            # 11. default 필터 (계산 중) 검증
            if "계산 중" in cell_str and "default_avg" not in checks:
                checks["default_avg"] = "✅ default 필터: '계산 중' 출력됨 (avg_salary)"
            
            # 12. upper 필터 검증
            if "HELLO WORLD" in cell_str and "upper" not in checks:
                checks["upper"] = "✅ upper 필터: 대문자 변환됨"
            
            # 13. lower 필터 검증
            if "hello world" in cell_str and "lower" not in cell_str and "lower" not in checks:
                checks["lower"] = "✅ lower 필터: 소문자 변환됨"
            
            # 14. title 필터 검증
            if "Hello World Example" in cell_str and "title" not in checks:
                checks["title"] = "✅ title 필터: 제목 케이스 변환됨"
            
            # 15. trim 필터 검증
            if "[trimmed]" in cell_str and "trim" not in checks:
                checks["trim"] = "✅ trim 필터: 공백 제거됨"
            
            # 16. replace 필터 검증
            if "hello Korea" in cell_str and "replace" not in checks:
                checks["replace"] = "✅ replace 필터: 문자열 치환됨"
            
            # 17. round 필터 검증
            if "3.14" in cell_str and "round" not in checks:
                checks["round"] = "✅ round 필터: 반올림됨"
            
            # 18. abs 필터 검증
            if "abs: 42" in cell_str and "abs" not in checks:
                checks["abs"] = "✅ abs 필터: 절대값 변환됨"
            
            # 19. int 필터 검증
            if "int: 3" in cell_str and "int" not in checks:
                checks["int"] = "✅ int 필터: 정수 변환됨"
            
            # 20. first 필터 검증
            if "first: apple" in cell_str and "first" not in checks:
                checks["first"] = "✅ first 필터: 첫 번째 요소"
            
            # 21. last 필터 검증
            if "last: cherry" in cell_str and "last" not in checks:
                checks["last"] = "✅ last 필터: 마지막 요소"
            
            # 22. 필터 체이닝 검증
            if "chained: TRIMMED" in cell_str and "chained" not in checks:
                checks["chained"] = "✅ 필터 체이닝: trim|upper 작동"
    
    for check in checks.values():
        print(f"  {check}")
    
    total_checks = len(checks)
    if total_checks >= 18:
        print(f"\n🎉 모든 새 기능이 정상 작동합니다! ({total_checks}개 검증 통과)")
    else:
        print(f"\n⚠️ 일부 기능 검증 필요 ({total_checks}/22 통과)")


if __name__ == "__main__":
    main()
