"""
예제: xls_template_renderer 사용법
"""

from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

from xls_template_renderer import render_template


def create_sample_template():
    """샘플 템플릿 파일 생성"""
    wb = Workbook()
    ws = wb.active
    ws.title = "리포트"
    
    # 스타일 정의
    header_font = Font(bold=True, size=14)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center')
    
    # 제목
    ws['A1'] = "{{ title }}"
    ws['A1'].font = header_font
    
    # 작성일
    ws['A2'] = "작성일: {{ date }}"
    
    # 빈 행
    ws['A3'] = ""
    
    # 주석 (결과에서 제거됨)
    ws['A4'] = "{# 아래는 상품 목록입니다 #}"
    
    # 테이블 헤더
    ws['A5'] = "번호"
    ws['B5'] = "상품명"
    ws['C5'] = "가격"
    ws['D5'] = "수량"
    ws['E5'] = "소계"
    
    for col in ['A', 'B', 'C', 'D', 'E']:
        cell = ws[f'{col}5']
        cell.fill = header_fill
        cell.font = header_font_white
        cell.border = border
        cell.alignment = center_align
    
    # For 루프 시작
    ws['A6'] = "{% for item in items %}"
    
    # 데이터 행 (서식 포함)
    ws['A7'] = "{{ loop_index }}"
    ws['B7'] = "{{ item.name }}"
    ws['C7'] = "{{ item.price }}"
    ws['D7'] = "{{ item.quantity }}"
    ws['E7'] = "{{ item.price * item.quantity }}"
    
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws[f'{col}7'].border = border
    ws['A7'].alignment = center_align
    ws['C7'].number_format = '#,##0'
    ws['E7'].number_format = '#,##0'
    
    # For 루프 종료
    ws['A8'] = "{% endfor %}"
    
    # 합계 행
    ws['A9'] = ""
    ws['D9'] = "합계:"
    ws['E9'] = "{{ total }}"
    ws['D9'].font = Font(bold=True)
    ws['E9'].font = Font(bold=True)
    ws['E9'].number_format = '#,##0'
    
    # 조건부 메시지
    ws['A10'] = "{% if discount %}"
    ws['A11'] = "할인 적용: {{ discount }}%"
    ws['A11'].font = Font(color="FF0000")
    ws['A12'] = "{% else %}"
    ws['A13'] = "할인 없음"
    ws['A14'] = "{% endif %}"
    
    # 열 너비 조정
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 15
    
    # 저장
    template_path = Path(__file__).parent / "simple_template.xlsx"
    wb.save(template_path)
    print(f"템플릿 생성됨: {template_path}")
    return template_path


def main():
    # 템플릿 생성
    template_path = create_sample_template()
    output_path = Path(__file__).parent / "simple_output.xlsx"
    
    # 렌더링할 데이터
    data = {
        "title": "2024년 1월 판매 리포트",
        "date": "2024-01-15",
        "items": [
            {"name": "노트북", "price": 1500000, "quantity": 2},
            {"name": "마우스", "price": 50000, "quantity": 10},
            {"name": "키보드", "price": 100000, "quantity": 5},
            {"name": "모니터", "price": 400000, "quantity": 3},
        ],
        "total": 5200000,
        "discount": 10,  # 할인율 (None이면 할인 없음)
        "loop_index": 1,  # 실제로는 렌더러에서 자동으로 설정되면 좋음
    }
    
    # loop_index를 각 아이템에 추가
    for idx, item in enumerate(data["items"], start=1):
        item["_index"] = idx
    
    # 데이터 수정 - loop_index 대신 item._index 사용
    # 참고: 현재 구현에서는 루프 인덱스 자동 지원이 없음
    
    # 렌더링 실행
    render_template(str(template_path), str(output_path), data)
    print(f"렌더링 완료: {output_path}")
    
    # 결과 확인
    from openpyxl import load_workbook
    wb = load_workbook(output_path)
    ws = wb.active
    
    print("\n=== 렌더링 결과 ===")
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
        print(row)


if __name__ == "__main__":
    main()
