"""
Command-line interface for xlsx-template-renderer.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .renderer import render_template, render_template_to_file
from .exceptions import TemplateError


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="xlsx-render",
        description="Render xlsx templates with JSON data",
    )
    
    parser.add_argument(
        "template",
        help="Path to the template xlsx file",
    )
    
    parser.add_argument(
        "data",
        help="Path to the JSON data file",
    )
    
    parser.add_argument(
        "-s", "--sheets",
        nargs="+",
        metavar="SHEET",
        help="Sheet names to render (default: all sheets)",
    )
    
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Output file path (default: modify template in-place)",
    )
    
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompts",
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    return parser.parse_args(args)


def main(args=None):
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)
    
    template_path = Path(parsed_args.template)
    data_path = Path(parsed_args.data)
    
    # Check if template file exists
    if not template_path.exists():
        print(f"오류: 템플릿 파일을 찾을 수 없습니다: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check if data file exists
    if not data_path.exists():
        print(f"오류: 데이터 파일을 찾을 수 없습니다: {data_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load JSON data
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파싱 실패: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if parsed_args.output:
            output_path = Path(parsed_args.output)
            
            # Check if output file already exists
            if output_path.exists() and not parsed_args.yes:
                print(f"경고: '{output_path}' 파일이 이미 존재합니다.")
                confirm = input("덮어쓰시겠습니까? [y/N]: ")
                if confirm.lower() != "y":
                    print("취소되었습니다.")
                    sys.exit(0)
            
            render_template_to_file(
                str(template_path),
                str(output_path),
                data,
                parsed_args.sheets,
            )
            print(f"완료: {output_path}")
        else:
            # In-place rendering - show warning
            if not parsed_args.yes:
                print(f"경고: '{template_path}' 파일이 직접 수정됩니다.")
                confirm = input("계속하시겠습니까? [y/N]: ")
                if confirm.lower() != "y":
                    print("취소되었습니다.")
                    sys.exit(0)
            
            render_template(
                str(template_path),
                data,
                parsed_args.sheets,
            )
            print(f"완료: {template_path}")
    
    except TemplateError as e:
        print(f"오류: 템플릿 렌더링 실패: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
