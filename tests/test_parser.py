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