#!/usr/bin/env python3
"""
Google Spreadsheet를 xlsx 파일로 다운로드하는 스크립트

사용법:
    python download_gsheet.py <url_or_id> <output_file>

예시:
    python download_gsheet.py -f https://docs.google.com/spreadsheets/d/1O03AkQ53F0SB2lj8ANsb8uKMgEMlRKC1q7yMu26kPOI/edit output.xlsx
    python download_gsheet.py -f 1O03AkQ53F0SB2lj8ANsb8uKMgEMlRKC1q7yMu26kPOI output.xlsx

설정:
    .env 파일에 다음 환경변수 설정:
    GOOGLE_CLIENT_ID=xxx
    GOOGLE_CLIENT_SECRET=xxx
    GOOGLE_REFRESH_TOKEN=xxx
"""

import argparse
import os
import re
import sys
from pathlib import Path


def extract_spreadsheet_id(url_or_id: str) -> str:
    """URL 또는 ID에서 spreadsheet ID 추출"""
    # 이미 ID 형식인 경우 (알파벳, 숫자, 하이픈, 언더스코어로 구성)
    if re.match(r'^[a-zA-Z0-9_-]+$', url_or_id) and '/' not in url_or_id:
        return url_or_id
    
    # URL에서 ID 추출
    # https://docs.google.com/spreadsheets/d/{ID}/edit...
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)
    
    raise ValueError(f"유효하지 않은 URL 또는 ID: {url_or_id}")


def load_env_file():
    """프로젝트 루트의 .env 파일 로드"""
    # 스크립트 위치 기준으로 상위 폴더의 .env 찾기
    script_dir = Path(__file__).parent
    env_file = script_dir.parent / '.env'
    
    if not env_file.exists():
        return
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())


def get_oauth2_credentials():
    """OAuth2 credentials 생성"""
    from google.oauth2.credentials import Credentials
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "OAuth2 인증 정보가 없습니다.\n"
            ".env 파일에 다음을 설정하세요:\n"
            "GOOGLE_CLIENT_ID=xxx\n"
            "GOOGLE_CLIENT_SECRET=xxx\n"
            "GOOGLE_REFRESH_TOKEN=xxx"
        )
    
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri='https://oauth2.googleapis.com/token',
    )


def download_spreadsheet(spreadsheet_id: str, output_path: str) -> None:
    """Google Spreadsheet를 xlsx로 다운로드"""
    try:
        import gspread
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("필요한 라이브러리 설치: pip install gspread google-auth", file=sys.stderr)
        sys.exit(1)
    
    # .env 파일 로드
    load_env_file()
    
    # OAuth2 인증
    credentials = get_oauth2_credentials()
    gc = gspread.authorize(credentials)
    
    # 스프레드시트 열기
    print(f"스프레드시트 ID: {spreadsheet_id}")
    spreadsheet = gc.open_by_key(spreadsheet_id)
    print(f"스프레드시트 이름: {spreadsheet.title}")
    
    # xlsx 형식으로 내보내기
    xlsx_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    content = gc.export(spreadsheet_id, format=xlsx_mime)
    
    # 파일 저장
    output_file = Path(output_path)
    output_file.write_bytes(content)
    print(f"다운로드 완료: {output_file.absolute()}")


def confirm_overwrite(filepath: Path) -> bool:
    """파일 덮어쓰기 확인"""
    while True:
        response = input(f"파일이 이미 존재합니다: {filepath}\n덮어쓰시겠습니까? [y/N]: ").strip().lower()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no', ''):
            return False
        print("y 또는 n을 입력하세요.")


def main():
    parser = argparse.ArgumentParser(
        description='Google Spreadsheet를 xlsx 파일로 다운로드',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'url_or_id',
        help='Google Spreadsheet URL 또는 ID'
    )
    parser.add_argument(
        'output',
        help='출력 파일 경로 (예: output.xlsx)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='기존 파일이 있어도 확인 없이 덮어쓰기'
    )
    
    args = parser.parse_args()
    
    # 파일 존재 여부 확인
    output_file = Path(args.output)
    if output_file.exists() and not args.force:
        if not confirm_overwrite(output_file):
            print("취소되었습니다.")
            sys.exit(0)
    
    try:
        spreadsheet_id = extract_spreadsheet_id(args.url_or_id)
        download_spreadsheet(spreadsheet_id, args.output)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
