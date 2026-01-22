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
    
    def test_positive_unary(self):
        """Test unary plus operator"""
        context = {"value": 10}
        assert evaluate_expression("+value", context) == 10
        assert evaluate_expression("+5", context) == 5
    
    def test_empty_expression(self):
        """Test empty expression returns None"""
        context = {"name": "test"}
        assert evaluate_expression("", context) is None
        assert evaluate_expression("   ", context) is None
    
    def test_invalid_syntax(self):
        """Test invalid syntax returns None"""
        context = {"name": "test"}
        assert evaluate_expression("name +", context) is None
        assert evaluate_expression("(unclosed", context) is None
    
    def test_unsupported_binary_operator(self):
        """Test unsupported operators return None"""
        context = {"a": 5, "b": 3}
        # Modulo is not supported
        assert evaluate_expression("a % b", context) is None
        # Power is not supported
        assert evaluate_expression("a ** b", context) is None
    
    def test_unsupported_unary_operator(self):
        """Test unsupported unary operators return None"""
        context = {"flag": True}
        # Bitwise not is not supported
        assert evaluate_expression("~flag", context) is None
    
    def test_unsupported_node_type(self):
        """Test unsupported AST node types return None"""
        context = {"items": [1, 2, 3]}
        # List comprehension is not supported
        assert evaluate_expression("[x for x in items]", context) is None
        # Lambda is not supported
        assert evaluate_expression("lambda x: x", context) is None
    
    def test_operation_with_none_operand(self):
        """Test binary operation with None operand returns None"""
        context = {"a": 5}
        assert evaluate_expression("a + unknown", context) is None
        assert evaluate_expression("unknown - a", context) is None
    
    def test_unary_operation_with_none(self):
        """Test unary operation on None returns None"""
        context = {}
        assert evaluate_expression("-unknown", context) is None


class TestResolvePathEdgeCases:
    """Additional edge case tests for resolve_path"""
    
    def test_empty_path(self):
        """Test empty path returns None"""
        data = {"name": "test"}
        assert resolve_path(data, "") is None
    
    def test_invalid_token(self):
        """Test invalid token pattern returns None"""
        data = {"name": "test"}
        # Special characters that don't match the pattern
        assert resolve_path(data, "name@invalid") is None
    
    def test_hasattr_object_access(self):
        """Test attribute access on object with hasattr"""
        class Person:
            def __init__(self, name):
                self.name = name
        
        data = {"person": Person("홍길동")}
        assert resolve_path(data, "person.name") == "홍길동"
    
    def test_hasattr_missing_attribute(self):
        """Test missing attribute on object returns None"""
        class Person:
            def __init__(self, name):
                self.name = name
        
        data = {"person": Person("홍길동")}
        assert resolve_path(data, "person.age") is None
    
    def test_index_on_non_sequence(self):
        """Test index access on non-sequence returns None"""
        data = {"value": 123}
        assert resolve_path(data, "value[0]") is None
    
    def test_tuple_index_access(self):
        """Test index access on tuple"""
        data = {"coords": (10, 20, 30)}
        assert resolve_path(data, "coords[0]") == 10
        assert resolve_path(data, "coords[2]") == 30


class TestExpressionEvaluatorPaths:
    """Tests for attribute and subscript path building"""
    
    def test_attribute_after_subscript(self):
        """Test attribute access after subscript: items[0].name"""
        context = {
            "items": [
                {"name": "first"},
                {"name": "second"}
            ]
        }
        assert evaluate_expression("items[0].name", context) == "first"
    
    def test_nested_subscript(self):
        """Test nested subscript: matrix[0][1]"""
        context = {
            "matrix": [
                [1, 2, 3],
                [4, 5, 6]
            ]
        }
        assert evaluate_expression("matrix[0][1]", context) == 2
    
    def test_subscript_after_attribute(self):
        """Test subscript after attribute: obj.items[0]"""
        context = {
            "obj": {
                "items": ["a", "b", "c"]
            }
        }
        assert evaluate_expression("obj.items[0]", context) == "a"
    
    def test_complex_nested_path(self):
        """Test complex nested path: data.users[0].orders[1].total"""
        context = {
            "data": {
                "users": [
                    {
                        "name": "user1",
                        "orders": [
                            {"total": 100},
                            {"total": 200}
                        ]
                    }
                ]
            }
        }
        assert evaluate_expression("data.users[0].orders[1].total", context) == 200
    
    def test_invalid_subscript_base(self):
        """Test subscript with invalid base returns empty path"""
        context = {"value": 123}
        # This should handle gracefully when base is not Name/Attribute/Subscript
        assert evaluate_expression("123[0]", context) is None
    
    def test_invalid_attribute_base(self):
        """Test attribute with invalid base returns empty path"""
        context = {}
        # Literal as base for attribute access
        assert evaluate_expression("123.attr", context) is None