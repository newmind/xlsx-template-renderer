"""Tests for filter functions"""

import pytest
from xls_template_renderer.filters import (
    filter_default,
    filter_length,
    filter_join,
    get_filter,
    apply_filter,
    parse_filter_expression,
    _split_filters,
    _parse_single_filter,
    _parse_filter_args,
    _parse_arg_value,
)


class TestFilterDefault:
    """Tests for default filter"""
    
    def test_none_returns_default(self):
        assert filter_default(None, 'N/A') == 'N/A'
    
    def test_value_returns_value(self):
        assert filter_default('hello', 'N/A') == 'hello'
        assert filter_default(123, 0) == 123
    
    def test_empty_string_returns_empty(self):
        # Empty string is not None, so it returns as is
        assert filter_default('', 'N/A') == ''
    
    def test_zero_returns_zero(self):
        assert filter_default(0, 100) == 0
    
    def test_false_returns_false(self):
        assert filter_default(False, True) is False
    
    def test_default_empty_string(self):
        assert filter_default(None) == ''


class TestFilterLength:
    """Tests for length filter"""
    
    def test_list_length(self):
        assert filter_length([1, 2, 3]) == 3
        assert filter_length([]) == 0
    
    def test_string_length(self):
        assert filter_length('hello') == 5
        assert filter_length('') == 0
    
    def test_tuple_length(self):
        assert filter_length((1, 2)) == 2
    
    def test_dict_length(self):
        assert filter_length({'a': 1, 'b': 2}) == 2
    
    def test_none_returns_zero(self):
        assert filter_length(None) == 0
    
    def test_non_sequence_returns_zero(self):
        assert filter_length(123) == 0


class TestFilterJoin:
    """Tests for join filter"""
    
    def test_join_with_comma(self):
        assert filter_join(['a', 'b', 'c'], ',') == 'a,b,c'
    
    def test_join_with_space(self):
        assert filter_join(['hello', 'world'], ' ') == 'hello world'
    
    def test_join_empty_separator(self):
        assert filter_join(['a', 'b', 'c']) == 'abc'
    
    def test_join_empty_list(self):
        assert filter_join([], ',') == ''
    
    def test_join_single_item(self):
        assert filter_join(['only'], ',') == 'only'
    
    def test_join_tuple(self):
        assert filter_join(('a', 'b'), '-') == 'a-b'
    
    def test_join_none(self):
        assert filter_join(None, ',') == ''
    
    def test_join_non_list(self):
        assert filter_join('hello', ',') == 'hello'
    
    def test_join_with_numbers(self):
        assert filter_join([1, 2, 3], '-') == '1-2-3'


class TestGetFilter:
    """Tests for get_filter function"""
    
    def test_get_existing_filter(self):
        assert get_filter('default') is not None
        assert get_filter('length') is not None
        assert get_filter('join') is not None
    
    def test_get_nonexistent_filter(self):
        assert get_filter('nonexistent') is None


class TestApplyFilter:
    """Tests for apply_filter function"""
    
    def test_apply_default(self):
        assert apply_filter(None, 'default', ['N/A']) == 'N/A'
    
    def test_apply_length(self):
        assert apply_filter([1, 2, 3], 'length') == 3
    
    def test_apply_join(self):
        assert apply_filter(['a', 'b'], 'join', [',']) == 'a,b'
    
    def test_apply_nonexistent_filter(self):
        # Returns original value if filter not found
        assert apply_filter('hello', 'nonexistent') == 'hello'
    
    def test_apply_with_no_args(self):
        assert apply_filter(None, 'default') == ''


class TestParseFilterExpression:
    """Tests for parse_filter_expression function"""
    
    def test_no_filter(self):
        base, filters = parse_filter_expression('name')
        assert base == 'name'
        assert filters == []
    
    def test_single_filter(self):
        base, filters = parse_filter_expression("value|default('N/A')")
        assert base == 'value'
        assert len(filters) == 1
        assert filters[0] == ('default', ['N/A'])
    
    def test_filter_no_args(self):
        base, filters = parse_filter_expression('items|length')
        assert base == 'items'
        assert len(filters) == 1
        assert filters[0] == ('length', [])
    
    def test_filter_chaining(self):
        base, filters = parse_filter_expression("value|default('')|length")
        assert base == 'value'
        assert len(filters) == 2
        assert filters[0] == ('default', [''])
        assert filters[1] == ('length', [])
    
    def test_filter_with_multiple_args(self):
        # join with separator
        base, filters = parse_filter_expression("items|join(', ')")
        assert base == 'items'
        assert filters[0] == ('join', [', '])
    
    def test_pipe_in_string(self):
        # Pipe inside string should not be treated as filter separator
        base, filters = parse_filter_expression("'a|b'")
        assert base == "'a|b'"
        assert filters == []


class TestSplitFilters:
    """Tests for _split_filters function"""
    
    def test_simple_split(self):
        parts = _split_filters('a|b|c')
        assert parts == ['a', 'b', 'c']
    
    def test_split_with_strings(self):
        parts = _split_filters("value|default('|')")
        assert parts == ['value', "default('|')"]
    
    def test_split_with_parens(self):
        parts = _split_filters('func(a|b)|other')
        assert len(parts) == 2


class TestParseSingleFilter:
    """Tests for _parse_single_filter function"""
    
    def test_filter_with_args(self):
        name, args = _parse_single_filter("default('N/A')")
        assert name == 'default'
        assert args == ['N/A']
    
    def test_filter_no_args(self):
        name, args = _parse_single_filter('length')
        assert name == 'length'
        assert args == []
    
    def test_invalid_filter(self):
        name, args = _parse_single_filter('123invalid')
        assert name is None


class TestParseFilterArgs:
    """Tests for _parse_filter_args function"""
    
    def test_single_string_arg(self):
        args = _parse_filter_args("'hello'")
        assert args == ['hello']
    
    def test_multiple_args(self):
        args = _parse_filter_args("'a', 'b'")
        assert args == ['a', 'b']
    
    def test_integer_arg(self):
        args = _parse_filter_args('10')
        assert args == [10]
    
    def test_float_arg(self):
        args = _parse_filter_args('3.14')
        assert args == [3.14]
    
    def test_empty_args(self):
        args = _parse_filter_args('')
        assert args == []
    
    def test_double_quoted_string(self):
        args = _parse_filter_args('"hello"')
        assert args == ['hello']


class TestParseArgValue:
    """Tests for _parse_arg_value function"""
    
    def test_single_quoted_string(self):
        assert _parse_arg_value("'hello'") == 'hello'
    
    def test_double_quoted_string(self):
        assert _parse_arg_value('"world"') == 'world'
    
    def test_integer(self):
        assert _parse_arg_value('42') == 42
    
    def test_float(self):
        assert _parse_arg_value('3.14') == 3.14
    
    def test_plain_string(self):
        # Not quoted, not a number
        assert _parse_arg_value('hello') == 'hello'
