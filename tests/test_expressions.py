"""Tests for expression evaluator"""

import pytest
from xls_template_renderer.expressions import (
    evaluate_expression,
    resolve_path,
    ExpressionEvaluator
)


class TestResolvePath:
    """Tests for resolve_path function"""
    
    def test_simple_key(self):
        data = {"name": "홍길동"}
        assert resolve_path(data, "name") == "홍길동"
    
    def test_nested_dict(self):
        data = {"user": {"name": "홍길동", "age": 30}}
        assert resolve_path(data, "user.name") == "홍길동"
        assert resolve_path(data, "user.age") == 30
    
    def test_list_index(self):
        data = {"items": ["a", "b", "c"]}
        assert resolve_path(data, "items[0]") == "a"
        assert resolve_path(data, "items[2]") == "c"
    
    def test_nested_list_dict(self):
        data = {
            "users": [
                {"name": "김철수"},
                {"name": "이영희"}
            ]
        }
        assert resolve_path(data, "users[0].name") == "김철수"
        assert resolve_path(data, "users[1].name") == "이영희"
    
    def test_deep_nesting(self):
        data = {
            "company": {
                "departments": [
                    {
                        "name": "개발팀",
                        "members": [
                            {"name": "김철수", "role": "백엔드"}
                        ]
                    }
                ]
            }
        }
        assert resolve_path(data, "company.departments[0].name") == "개발팀"
        assert resolve_path(data, "company.departments[0].members[0].name") == "김철수"
    
    def test_missing_key(self):
        data = {"name": "홍길동"}
        assert resolve_path(data, "age") is None
        assert resolve_path(data, "user.name") is None
    
    def test_index_out_of_range(self):
        data = {"items": ["a", "b"]}
        assert resolve_path(data, "items[5]") is None


class TestEvaluateExpression:
    """Tests for evaluate_expression function"""
    
    def test_simple_variable(self):
        context = {"name": "홍길동", "age": 25}
        assert evaluate_expression("name", context) == "홍길동"
        assert evaluate_expression("age", context) == 25
    
    def test_arithmetic_add(self):
        context = {"price": 1000}
        assert evaluate_expression("10 + 5", context) == 15
        assert evaluate_expression("price + 500", context) == 1500
    
    def test_arithmetic_subtract(self):
        context = {"age": 25}
        assert evaluate_expression("age - 1", context) == 24
    
    def test_arithmetic_multiply(self):
        context = {"price": 1000}
        assert evaluate_expression("price * 1.1", context) == 1100.0
    
    def test_arithmetic_divide(self):
        context = {"total": 100}
        assert evaluate_expression("total / 2", context) == 50.0
    
    def test_string_concatenation(self):
        context = {"name": "홍길동"}
        assert evaluate_expression('"안녕" + "하세요"', context) == "안녕하세요"
        assert evaluate_expression('name + "님"', context) == "홍길동님"
    
    def test_attribute_access(self):
        context = {"item": {"name": "상품A", "price": 1000}}
        assert evaluate_expression("item.name", context) == "상품A"
        assert evaluate_expression("item.price", context) == 1000
    
    def test_index_access(self):
        context = {"items": [{"name": "A"}, {"name": "B"}]}
        assert evaluate_expression("items[0].name", context) == "A"
        assert evaluate_expression("items[1].name", context) == "B"
    
    def test_missing_variable(self):
        context = {"name": "홍길동"}
        assert evaluate_expression("unknown", context) is None
    
    def test_complex_expression(self):
        context = {"item": {"price": 1000, "quantity": 3}}
        assert evaluate_expression("item.price * item.quantity", context) == 3000
    
    def test_negative_number(self):
        context = {"value": 10}
        assert evaluate_expression("-value", context) == -10
        assert evaluate_expression("-5", context) == -5
