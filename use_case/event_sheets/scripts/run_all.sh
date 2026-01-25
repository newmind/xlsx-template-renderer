#!/bin/bash
# 전체 케이스 일괄 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CASES_DIR="$BASE_DIR/cases"
TEMPLATE="$BASE_DIR/template.xlsx"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "이벤트 시트 테스트 - 전체 케이스 실행"
echo "========================================"
echo ""

# 템플릿 파일 확인
if [ ! -f "$TEMPLATE" ]; then
    echo -e "${RED}[ERROR] 템플릿 파일이 없습니다: $TEMPLATE${NC}"
    exit 1
fi

# 케이스 목록
CASES=(
    "01_fansign_event"
    "02_photo_event"
    "03_game_event"
    "04_bakery_event"
    "05_daily_host"
    "06_special_event_gacha"
    "07_special_event_other"
    "08_videocall_event"
    "09_videocall_event_unit"
    "10_videocall_event_individual"
    "11_online_twoshot_event"
    "12_combo_1_2_and_3"
    "13_combo_1_2_and_3_4"
    "14_combo_1_2_3_and_4"
)

PASS_COUNT=0
FAIL_COUNT=0

for case in "${CASES[@]}"; do
    CASE_DIR="$CASES_DIR/$case"
    DATA_FILE="$CASE_DIR/data.json"
    OUTPUT_FILE="$CASE_DIR/output.xlsx"
    
    echo -n "[$case] "
    
    if [ ! -f "$DATA_FILE" ]; then
        echo -e "${YELLOW}SKIP${NC} - data.json 없음"
        continue
    fi
    
    # 렌더링 실행 (render_event_sheets.py 사용)
    if uv run python "$SCRIPT_DIR/render_event_sheets.py" "$TEMPLATE" "$DATA_FILE" -o "$OUTPUT_FILE" 2>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
        ((PASS_COUNT++))
    else
        echo -e "${RED}FAIL${NC}"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "========================================"
echo "결과: ${GREEN}PASS: $PASS_COUNT${NC}, ${RED}FAIL: $FAIL_COUNT${NC}"
echo "========================================"

# 검증 스크립트 실행 제안
if [ $PASS_COUNT -gt 0 ]; then
    echo ""
    echo "검증을 실행하려면:"
    echo "  python $SCRIPT_DIR/verify.py"
fi

exit $FAIL_COUNT
