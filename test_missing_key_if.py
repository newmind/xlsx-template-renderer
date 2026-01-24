#!/usr/bin/env python3
"""
존재하지 않는 키에 대한 if 조건문 동작 테스트
"""

from src.xlsx_template_renderer.expressions import evaluate_expression

# 테스트 1: 단순 키가 없는 경우
context1 = {"name": "홍길동"}
result1 = evaluate_expression("age", context1)
print(f"테스트 1 - 존재하지 않는 키 'age': {result1}")
print(f"  -> if 조건에서: {'참' if result1 else '거짓'}")

# 테스트 2: 중첩 키가 없는 경우 (a.b.c)
context2 = {}
result2 = evaluate_expression("a.b.c", context2)
print(f"\n테스트 2 - 존재하지 않는 중첩 키 'a.b.c' (빈 컨텍스트): {result2}")
print(f"  -> if 조건에서: {'참' if result2 else '거짓'}")

# 테스트 3: 중간 키가 없는 경우
context3 = {"a": {"x": 1}}
result3 = evaluate_expression("a.b.c", context3)
print(f"\n테스트 3 - 존재하지 않는 중첩 키 'a.b.c' (a는 있지만 b가 없음): {result3}")
print(f"  -> if 조건에서: {'참' if result3 else '거짓'}")

# 테스트 4: 마지막 키만 없는 경우
context4 = {"a": {"b": {"x": 1}}}
result4 = evaluate_expression("a.b.c", context4)
print(f"\n테스트 4 - 존재하지 않는 중첩 키 'a.b.c' (a.b는 있지만 c가 없음): {result4}")
print(f"  -> if 조건에서: {'참' if result4 else '거짓'}")

# 테스트 5: 모든 키가 있는 경우
context5 = {"a": {"b": {"c": "값"}}}
result5 = evaluate_expression("a.b.c", context5)
print(f"\n테스트 5 - 존재하는 중첩 키 'a.b.c': {result5}")
print(f"  -> if 조건에서: {'참' if result5 else '거짓'}")

# 테스트 6: 값이 False인 경우
context6 = {"a": {"b": {"c": False}}}
result6 = evaluate_expression("a.b.c", context6)
print(f"\n테스트 6 - 존재하지만 False인 'a.b.c': {result6}")
print(f"  -> if 조건에서: {'참' if result6 else '거짓'}")

# 테스트 7: 값이 0인 경우
context7 = {"a": {"b": {"c": 0}}}
result7 = evaluate_expression("a.b.c", context7)
print(f"\n테스트 7 - 존재하지만 0인 'a.b.c': {result7}")
print(f"  -> if 조건에서: {'참' if result7 else '거짓'}")

# 테스트 8: 값이 빈 문자열인 경우
context8 = {"a": {"b": {"c": ""}}}
result8 = evaluate_expression("a.b.c", context8)
print(f"\n테스트 8 - 존재하지만 빈 문자열인 'a.b.c': '{result8}'")
print(f"  -> if 조건에서: {'참' if result8 else '거짓'}")
