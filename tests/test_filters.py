"""Tests for filter functions"""

import pytest
from xlsx_template_renderer.filters import (
    filter_default,
    filter_length,
    filter_join,
    filter_upper,
    filter_lower,
    filter_title,
    filter_trim,
    filter_replace,
    filter_round,
    filter_abs,
    filter_int,
    filter_float,
    filter_first,
    filter_last,
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


# === New Filter Tests ===

class TestFilterUpper:
    """Tests for upper filter"""
    
    def test_uppercase(self):
        assert filter_upper('hello') == 'HELLO'
        assert filter_upper('Hello World') == 'HELLO WORLD'
    
    def test_already_upper(self):
        assert filter_upper('HELLO') == 'HELLO'
    
    def test_none_returns_empty(self):
        assert filter_upper(None) == ''
    
    def test_number_to_string(self):
        assert filter_upper(123) == '123'


class TestFilterLower:
    """Tests for lower filter"""
    
    def test_lowercase(self):
        assert filter_lower('HELLO') == 'hello'
        assert filter_lower('Hello World') == 'hello world'
    
    def test_already_lower(self):
        assert filter_lower('hello') == 'hello'
    
    def test_none_returns_empty(self):
        assert filter_lower(None) == ''
    
    def test_number_to_string(self):
        assert filter_lower(123) == '123'


class TestFilterTitle:
    """Tests for title filter"""
    
    def test_title_case(self):
        assert filter_title('hello world') == 'Hello World'
        assert filter_title('HELLO WORLD') == 'Hello World'
    
    def test_single_word(self):
        assert filter_title('hello') == 'Hello'
    
    def test_none_returns_empty(self):
        assert filter_title(None) == ''
    
    def test_number_to_string(self):
        assert filter_title(123) == '123'


class TestFilterTrim:
    """Tests for trim filter"""
    
    def test_trim_spaces(self):
        assert filter_trim('  hello  ') == 'hello'
        assert filter_trim('\n\thello\n\t') == 'hello'
    
    def test_no_spaces(self):
        assert filter_trim('hello') == 'hello'
    
    def test_none_returns_empty(self):
        assert filter_trim(None) == ''
    
    def test_only_spaces(self):
        assert filter_trim('   ') == ''


class TestFilterReplace:
    """Tests for replace filter"""
    
    def test_replace_single(self):
        assert filter_replace('hello', 'l', 'x') == 'hexxo'
    
    def test_replace_substring(self):
        assert filter_replace('hello world', 'world', 'there') == 'hello there'
    
    def test_replace_not_found(self):
        assert filter_replace('hello', 'x', 'y') == 'hello'
    
    def test_none_returns_empty(self):
        assert filter_replace(None, 'a', 'b') == ''
    
    def test_replace_all_occurrences(self):
        assert filter_replace('aaa', 'a', 'b') == 'bbb'


class TestFilterRound:
    """Tests for round filter"""
    
    def test_round_default(self):
        assert filter_round(3.7) == 4.0
        assert filter_round(3.2) == 3.0
    
    def test_round_with_precision(self):
        assert filter_round(3.14159, 2) == 3.14
        assert filter_round(3.145, 2) == 3.15
    
    def test_none_returns_zero(self):
        assert filter_round(None) == 0.0
    
    def test_string_number(self):
        assert filter_round('3.7') == 4.0
    
    def test_invalid_returns_zero(self):
        assert filter_round('abc') == 0.0


class TestFilterAbs:
    """Tests for abs filter"""
    
    def test_negative_int(self):
        assert filter_abs(-5) == 5
    
    def test_negative_float(self):
        assert filter_abs(-3.14) == 3.14
    
    def test_positive(self):
        assert filter_abs(5) == 5
    
    def test_zero(self):
        assert filter_abs(0) == 0
    
    def test_none_returns_zero(self):
        assert filter_abs(None) == 0
    
    def test_string_number(self):
        assert filter_abs('-5') == 5.0


class TestFilterInt:
    """Tests for int filter"""
    
    def test_float_to_int(self):
        assert filter_int(3.7) == 3
        assert filter_int(3.2) == 3
    
    def test_string_to_int(self):
        assert filter_int('42') == 42
        assert filter_int('3.7') == 3
    
    def test_none_returns_default(self):
        assert filter_int(None) == 0
        assert filter_int(None, 10) == 10
    
    def test_invalid_returns_default(self):
        assert filter_int('abc') == 0
        assert filter_int('abc', 99) == 99


class TestFilterFloat:
    """Tests for float filter"""
    
    def test_int_to_float(self):
        assert filter_float(42) == 42.0
    
    def test_string_to_float(self):
        assert filter_float('3.14') == 3.14
        assert filter_float('42') == 42.0
    
    def test_none_returns_default(self):
        assert filter_float(None) == 0.0
        assert filter_float(None, 1.5) == 1.5
    
    def test_invalid_returns_default(self):
        assert filter_float('abc') == 0.0
        assert filter_float('abc', 9.9) == 9.9


class TestFilterFirst:
    """Tests for first filter"""
    
    def test_list_first(self):
        assert filter_first([1, 2, 3]) == 1
        assert filter_first(['a', 'b', 'c']) == 'a'
    
    def test_string_first(self):
        assert filter_first('hello') == 'h'
    
    def test_tuple_first(self):
        assert filter_first((1, 2, 3)) == 1
    
    def test_empty_returns_none(self):
        assert filter_first([]) is None
        assert filter_first('') is None
    
    def test_none_returns_none(self):
        assert filter_first(None) is None


class TestFilterLast:
    """Tests for last filter"""
    
    def test_list_last(self):
        assert filter_last([1, 2, 3]) == 3
        assert filter_last(['a', 'b', 'c']) == 'c'
    
    def test_string_last(self):
        assert filter_last('hello') == 'o'
    
    def test_tuple_last(self):
        assert filter_last((1, 2, 3)) == 3
    
    def test_empty_returns_none(self):
        assert filter_last([]) is None
        assert filter_last('') is None
    
    def test_none_returns_none(self):
        assert filter_last(None) is None


class TestGetFilterNewFilters:
    """Tests for get_filter with new filters"""
    
    def test_get_new_filters(self):
        assert get_filter('upper') is not None
        assert get_filter('lower') is not None
        assert get_filter('title') is not None
        assert get_filter('trim') is not None
        assert get_filter('replace') is not None
        assert get_filter('round') is not None
        assert get_filter('abs') is not None
        assert get_filter('int') is not None
        assert get_filter('float') is not None
        assert get_filter('first') is not None
        assert get_filter('last') is not None


class TestApplyFilterNewFilters:
    """Tests for apply_filter with new filters"""
    
    def test_apply_upper(self):
        assert apply_filter('hello', 'upper') == 'HELLO'
    
    def test_apply_round_with_args(self):
        assert apply_filter(3.14159, 'round', [2]) == 3.14
    
    def test_apply_replace_with_args(self):
        assert apply_filter('hello', 'replace', ['l', 'x']) == 'hexxo'
    
    def test_apply_first(self):
        assert apply_filter([1, 2, 3], 'first') == 1


class TestParseFilterExpressionNewFilters:
    """Tests for parse_filter_expression with new filters"""
    
    def test_upper_filter(self):
        base, filters = parse_filter_expression('name|upper')
        assert base == 'name'
        assert filters == [('upper', [])]
    
    def test_round_with_precision(self):
        base, filters = parse_filter_expression('price|round(2)')
        assert base == 'price'
        assert filters == [('round', [2])]
    
    def test_replace_with_args(self):
        base, filters = parse_filter_expression("text|replace('a', 'b')")
        assert base == 'text'
        assert filters == [('replace', ['a', 'b'])]
    
    def test_chained_new_filters(self):
        base, filters = parse_filter_expression('name|trim|upper')
        assert base == 'name'
        assert filters == [('trim', []), ('upper', [])]
