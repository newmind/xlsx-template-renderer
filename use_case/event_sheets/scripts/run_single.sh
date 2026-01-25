#!/bin/bash
# 단일 케이스 실행 스크립트 (수동 테스트용)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CASES_DIR="$BASE_DIR/cases"
TEMPLATE="$BASE_DIR/template.xlsx"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
    echo "사용법: $0 <케이스명>"
    echo ""
    echo "사용 가능한 케이스:"
    echo "  대면 이벤트:"
    echo "    01_fansign_event          - 팬사인회"
    echo "    02_photo_event            - 포토회"
    echo "    03_game_event             - 게임회"
    echo "    04_bakery_event           - 베이커리 이벤트"
    echo ""
    echo "  스페셜 이벤트:"
    echo "    05_daily_host             - 일일점장"
    echo "    06_special_event_gacha    - 스페셜(가챠)"
    echo "    07_special_event_other    - 스페셜(가챠 외)"
    echo ""
    echo "  비대면/영상통화:"
    echo "    08_videocall_event        - 영상통화"
    echo "    09_videocall_event_unit   - 유닛 영상통화"
    echo "    10_videocall_event_individual - 개인 영상통화"
    echo "    11_online_twoshot_event   - 온라인 투샷회"
    echo ""
    echo "  복수 이벤트 조합:"
    echo "    12_combo_1_2_and_3        - (1+2부, 3부)"
    echo "    13_combo_1_2_and_3_4      - (1+2부, 3+4부)"
    echo "    14_combo_1_2_3_and_4      - (1+2+3부, 4부)"
    echo ""
    echo "예시:"
    echo "  $0 01_fansign_event"
    echo "  $0 12_combo_1_2_and_3"
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

CASE_NAME="$1"
CASE_DIR="$CASES_DIR/$CASE_NAME"
DATA_FILE="$CASE_DIR/data.json"
OUTPUT_FILE="$CASE_DIR/output.xlsx"
README_FILE="$CASE_DIR/README.md"

# 케이스 디렉토리 확인
if [ ! -d "$CASE_DIR" ]; then
    echo -e "${RED}[ERROR] 케이스를 찾을 수 없습니다: $CASE_NAME${NC}"
    echo ""
    usage
    exit 1
fi

# 템플릿 파일 확인
if [ ! -f "$TEMPLATE" ]; then
    echo -e "${RED}[ERROR] 템플릿 파일이 없습니다: $TEMPLATE${NC}"
    exit 1
fi

# data.json 확인
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}[ERROR] data.json이 없습니다: $DATA_FILE${NC}"
    exit 1
fi

echo "========================================"
echo -e "${CYAN}케이스: $CASE_NAME${NC}"
echo "========================================"
echo ""

# README 내용 출력 (있으면)
if [ -f "$README_FILE" ]; then
    echo -e "${YELLOW}[테스트 정보]${NC}"
    # 예상 시트명 부분만 추출
    grep -A 5 "## 예상 시트명" "$README_FILE" 2>/dev/null || true
    echo ""
fi

echo -e "${YELLOW}[실행 중...]${NC}"
echo "템플릿: $TEMPLATE"
echo "데이터: $DATA_FILE"
echo "출력: $OUTPUT_FILE"
echo ""

# 렌더링 실행 (render_event_sheets.py 사용, verbose)
if uv run python "$SCRIPT_DIR/render_event_sheets.py" "$TEMPLATE" "$DATA_FILE" -o "$OUTPUT_FILE" -v; then
    echo ""
    echo -e "${GREEN}[SUCCESS] 렌더링 완료${NC}"
    echo ""
    echo "결과 파일 열기:"
    echo "  open $OUTPUT_FILE"
    echo ""
    echo "검증 실행:"
    echo "  uv run python $SCRIPT_DIR/verify.py $CASE_NAME"
else
    echo ""
    echo -e "${RED}[FAILED] 렌더링 실패${NC}"
    exit 1
fi
