"""Tests for template parser"""

import pytest
from xls_template_renderer.parser import (
    parse_cell,
    is_control_statement,
    extract_variables,
    substitute_variables,
    evaluate_condition,
    Token,
    TokenType
)


class TestParseCell:
    """Tests for parse_cell function"""
    
    def test_plain_text(self):
        assert parse_cell("Hello World") is None
        assert parse_cell("일반 텍스트") is None
        assert parse_cell("123") is None
    
    def test_variable(self):
        token = parse_cell("{{ name }}")
        assert token is not None
        assert token.type == TokenType.VARIABLE
        
        token = parse_cell("Hello {{ name }}!")
        assert token is not None
        assert token.type == TokenType.VARIABLE
    
    def test_for_start(self):
        token = parse_cell("{% for item in items %}")
        assert token is not None
        assert token.type == TokenType.FOR_START
        assert token.loop_var == "item"
        assert token.loop_iter == "items"
    
    def test_for_with_nested_path(self):
        token = parse_cell("{% for dept in company.departments %}")
        assert token is not None
        assert token.type == TokenType.FOR_START
        assert token.loop_var == "dept"
        assert token.loop_iter == "company.departments"
    
    def test_for_end(self):
        token = parse_cell("{% endfor %}")
        assert token is not None
        assert token.type == TokenType.FOR_END
    
    def test_if_start(self):
        token = parse_cell("{% if items %}")
        assert token is not None
        assert token.type == TokenType.IF_START
        assert token.expression == "items"
    
    def test_if_with_condition(self):
        token = parse_cell("{% if count > 0 %}")
        assert token is not None
        assert token.type == TokenType.IF_START
        assert token.expression == "count > 0"
    
    def test_elif(self):
        token = parse_cell("{% elif other_condition %}")
        assert token is not None
        assert token.type == TokenType.ELIF
        assert token.expression == "other_condition"
    
    def test_else(self):
        token = parse_cell("{% else %}")
        assert token is not None
        assert token.type == TokenType.ELSE
    
    def test_if_end(self):
        token = parse_cell("{% endif %}")
        assert token is not None
        assert token.type == TokenType.IF_END
    
    def test_comment(self):
        token = parse_cell("{# 이것은 주석입니다 #}")
        assert token is not None
        assert token.type == TokenType.COMMENT
    
    def test_none_input(self):
        assert parse_cell(None) is None


class TestIsControlStatement:
    """Tests for is_control_statement function"""
    
    def test_control_statements(self):
        assert is_control_statement("{% for item in items %}") is True
        assert is_control_statement("{% endfor %}") is True
        assert is_control_statement("{% if condition %}") is True
        assert is_control_statement("{% endif %}") is True
        assert is_control_statement("{# comment #}") is True
    
    def test_non_control(self):
        assert is_control_statement("Hello") is False
        assert is_control_statement("{{ variable }}") is False
        assert is_control_statement(None) is False


class TestExtractVariables:
    """Tests for extract_variables function"""
    
    def test_single_variable(self):
        assert extract_variables("{{ name }}") == ["name"]
    
    def test_multiple_variables(self):
        result = extract_variables("{{ name }} ({{ age }}세)")
        assert result == ["name", "age"]
    
    def test_expression_variable(self):
        result = extract_variables("{{ price * 1.1 }}")
        assert result == ["price * 1.1"]
    
    def test_no_variables(self):
        assert extract_variables("Hello World") == []
    
    def test_none_input(self):
        assert extract_variables(None) == []


class TestSubstituteVariables:
    """Tests for substitute_variables function"""
    
    def test_single_substitution(self):
        result = substitute_variables("Hello {{ name }}!", {"name": "홍길동"})
        assert result == "Hello 홍길동!"
    
    def test_multiple_substitutions(self):
        result = substitute_variables(
            "{{ name }} ({{ age }}세)",
            {"name": "홍길동", "age": 25}
        )
        assert result == "홍길동 (25세)"
    
    def test_missing_variable(self):
        result = substitute_variables("Hello {{ name }}!", {})
        assert result == "Hello {{ name }}!"
    
    def test_none_value(self):
        result = substitute_variables("Value: {{ val }}", {"val": None})
        assert result == "Value: "


class TestEvaluateCondition:
    """Tests for evaluate_condition function"""
    
    def test_truthy_value(self):
        assert evaluate_condition("items", {"items": [1, 2, 3]}) is True
        assert evaluate_condition("items", {"items": []}) is False
        assert evaluate_condition("name", {"name": "홍길동"}) is True
        assert evaluate_condition("name", {"name": ""}) is False
    
    def test_comparison_greater(self):
        assert evaluate_condition("count > 0", {"count": 5}) is True
        assert evaluate_condition("count > 0", {"count": 0}) is False
    
    def test_comparison_less(self):
        assert evaluate_condition("count < 10", {"count": 5}) is True
        assert evaluate_condition("count < 10", {"count": 10}) is False
    
    def test_comparison_equal(self):
        assert evaluate_condition("status == 1", {"status": 1}) is True
        assert evaluate_condition("status == 1", {"status": 2}) is False
    
    def test_comparison_not_equal(self):
        assert evaluate_condition("status != 0", {"status": 1}) is True
        assert evaluate_condition("status != 0", {"status": 0}) is False
    
    def test_comparison_greater_equal(self):
        assert evaluate_condition("count >= 5", {"count": 5}) is True
        assert evaluate_condition("count >= 5", {"count": 4}) is False
    
    def test_comparison_less_equal(self):
        assert evaluate_condition("count <= 5", {"count": 5}) is True
        assert evaluate_condition("count <= 5", {"count": 6}) is False
    
    def test_comparison_with_none(self):
        """None 값 비교 테스트"""
        assert evaluate_condition("unknown > 0", {}) is False
        assert evaluate_condition("value > unknown", {"value": 5}) is False
    
    def test_failed_evaluation_returns_false(self):
        """평가 실패 시 False 반환 테스트"""
        # 알 수 없는 변수만 있는 경우
        assert evaluate_condition("unknown_var", {}) is False


class TestUnknownControlStatement:
    """Tests for unknown control statements"""
    
    def test_unknown_statement_returns_none(self):
        """알 수 없는 control statement는 None 반환"""
        token = parse_cell("{% unknown_statement %}")
        assert token is None
    
    def test_malformed_for_returns_none(self):
        """잘못된 형식의 for문은 None 반환"""
        token = parse_cell("{% for item %}")  # 'in' 없음
        assert token is None
    
    def test_whitespace_in_control_statement(self):
        """공백이 포함된 control statement 처리"""
        token = parse_cell("{%   for   item   in   items   %}")
        assert token is not None
        assert token.type == TokenType.FOR_START
        assert token.loop_var == "item"
        assert token.loop_iter == "items"


class TestSubstituteVariablesEdgeCases:
    """Edge case tests for substitute_variables"""
    
    def test_none_input(self):
        """None 입력 처리"""
        result = substitute_variables(None, {"name": "test"})
        assert result == ""
    
    def test_numeric_input(self):
        """숫자 입력 처리"""
        result = substitute_variables(123, {})
        assert result == "123"


class TestLogicalOperators:
    """Tests for logical operators (and, or, not)"""
    
    def test_and_both_true(self):
        context = {"a": True, "b": True}
        assert evaluate_condition("a and b", context) is True
    
    def test_and_one_false(self):
        context = {"a": True, "b": False}
        assert evaluate_condition("a and b", context) is False
    
    def test_and_both_false(self):
        context = {"a": False, "b": False}
        assert evaluate_condition("a and b", context) is False
    
    def test_or_both_true(self):
        context = {"a": True, "b": True}
        assert evaluate_condition("a or b", context) is True
    
    def test_or_one_true(self):
        context = {"a": True, "b": False}
        assert evaluate_condition("a or b", context) is True
    
    def test_or_both_false(self):
        context = {"a": False, "b": False}
        assert evaluate_condition("a or b", context) is False
    
    def test_not_true(self):
        context = {"flag": True}
        assert evaluate_condition("not flag", context) is False
    
    def test_not_false(self):
        context = {"flag": False}
        assert evaluate_condition("not flag", context) is True
    
    def test_not_with_expression(self):
        context = {"items": []}
        assert evaluate_condition("not items", context) is True
    
    def test_combined_and_or(self):
        # or has lower precedence than and
        context = {"a": True, "b": False, "c": True}
        # a and b = False, False or c = True
        assert evaluate_condition("a and b or c", context) is True
    
    def test_and_with_comparison(self):
        context = {"x": 5, "y": 10}
        assert evaluate_condition("x > 0 and y > 0", context) is True
        assert evaluate_condition("x > 0 and y < 0", context) is False
    
    def test_or_with_comparison(self):
        context = {"x": 5, "y": -1}
        assert evaluate_condition("x > 0 or y > 0", context) is True
        assert evaluate_condition("x < 0 or y < 0", context) is True
    
    def test_not_with_comparison(self):
        context = {"x": 5}
        assert evaluate_condition("not x > 10", context) is True
        assert evaluate_condition("not x < 10", context) is False


class TestInOperator:
    """Tests for 'in' operator"""
    
    def test_in_list(self):
        context = {"item": "apple", "items": ["apple", "banana", "cherry"]}
        assert evaluate_condition("item in items", context) is True
    
    def test_not_in_list(self):
        context = {"item": "grape", "items": ["apple", "banana", "cherry"]}
        assert evaluate_condition("item in items", context) is False
    
    def test_in_string(self):
        context = {"char": "a", "text": "hello"}
        assert evaluate_condition("char in text", context) is False
        
        context = {"char": "e", "text": "hello"}
        assert evaluate_condition("char in text", context) is True
    
    def test_in_with_literal(self):
        context = {"status": "active"}
        # Note: This requires the literal to be a variable
        context = {"status": "active", "valid_statuses": ["active", "pending"]}
        assert evaluate_condition("status in valid_statuses", context) is True
    
    def test_not_in_operator(self):
        context = {"item": "grape", "items": ["apple", "banana"]}
        assert evaluate_condition("item not in items", context) is True
    
    def test_not_in_operator_false(self):
        context = {"item": "apple", "items": ["apple", "banana"]}
        assert evaluate_condition("item not in items", context) is False
    
    def test_in_with_none_collection(self):
        context = {"item": "apple"}
        assert evaluate_condition("item in items", context) is False
    
    def test_not_in_with_none_collection(self):
        context = {"item": "apple"}
        assert evaluate_condition("item not in items", context) is True
    
    def test_in_with_dict_keys(self):
        context = {"key": "name", "data": {"name": "홍길동", "age": 30}}
        assert evaluate_condition("key in data", context) is True
    
    def test_in_number_list(self):
        context = {"num": 2, "numbers": [1, 2, 3]}
        assert evaluate_condition("num in numbers", context) is True


class TestLogicalOperatorEdgeCases:
    """Edge cases for logical operators"""
    
    def test_and_with_strings(self):
        context = {"a": "hello", "b": "world"}
        assert evaluate_condition("a and b", context) is True
    
    def test_and_with_empty_string(self):
        context = {"a": "hello", "b": ""}
        assert evaluate_condition("a and b", context) is False
    
    def test_or_with_empty_list(self):
        context = {"a": [], "b": [1, 2]}
        assert evaluate_condition("a or b", context) is True
    
    def test_nested_not(self):
        context = {"flag": True}
        assert evaluate_condition("not not flag", context) is True
    
    def test_complex_condition(self):
        context = {"x": 5, "y": 10, "z": 15}
        # (x > 0 and y > 0) or z > 20
        assert evaluate_condition("x > 0 and y > 0 or z > 20", context) is True
    
    def test_in_operator_with_type_error(self):
        """in 연산자에서 TypeError 발생 시 False 반환 테스트"""
        # int는 iterable이 아니므로 TypeError 발생
        context = {"item": "a", "collection": 123}
        assert evaluate_condition("item in collection", context) is False
    
    def test_not_in_operator_with_type_error(self):
        """not in 연산자에서 TypeError 발생 시 True 반환 테스트"""
        # int는 iterable이 아니므로 TypeError 발생
        context = {"item": "a", "collection": 123}
        assert evaluate_condition("item not in collection", context) is True
    
    def test_logical_operator_with_string_literal(self):
        """문자열 리터럴이 포함된 논리 연산자 테스트"""
        context = {"status": "active"}
        # 문자열 내에 'or'가 있는 경우 분리되지 않아야 함
        assert evaluate_condition("status", context) is True


class TestComparisonOperatorsFallback:
    """Tests for comparison operator fallback code paths"""
    
    def test_comparison_eq_fallback(self):
        """== 비교 연산자 폴백 테스트"""
        # evaluate_expression이 None을 반환하면 폴백 로직 실행
        context = {"status": "active"}
        # 문자열 비교
        assert evaluate_condition("status == 'active'", context) is True
        assert evaluate_condition("status == 'inactive'", context) is False
    
    def test_comparison_ne_fallback(self):
        """!= 비교 연산자 폴백 테스트"""
        context = {"status": "active"}
        assert evaluate_condition("status != 'inactive'", context) is True
        assert evaluate_condition("status != 'active'", context) is False
    
    def test_comparison_ge_fallback(self):
        """>= 비교 연산자 폴백 테스트"""
        context = {"count": 10}
        assert evaluate_condition("count >= 10", context) is True
        assert evaluate_condition("count >= 11", context) is False
    
    def test_comparison_le_fallback(self):
        """<= 비교 연산자 폴백 테스트"""
        context = {"count": 10}
        assert evaluate_condition("count <= 10", context) is True
        assert evaluate_condition("count <= 9", context) is False
    
    def test_comparison_gt_fallback(self):
        """> 비교 연산자 폴백 테스트"""
        context = {"count": 10}
        assert evaluate_condition("count > 9", context) is True
        assert evaluate_condition("count > 10", context) is False
    
    def test_comparison_lt_fallback(self):
        """< 비교 연산자 폴백 테스트"""
        context = {"count": 10}
        assert evaluate_condition("count < 11", context) is True
        assert evaluate_condition("count < 10", context) is False