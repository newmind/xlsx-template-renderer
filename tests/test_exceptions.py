"""Tests for custom exceptions"""

import pytest
from xlsx_template_renderer.exceptions import (
    TemplateError,
    TemplateSyntaxError,
    TemplateRenderError
)


class TestTemplateError:
    """Tests for base TemplateError"""
    
    def test_basic_exception(self):
        error = TemplateError("기본 오류")
        assert str(error) == "기본 오류"
    
    def test_inheritance(self):
        error = TemplateError("테스트")
        assert isinstance(error, Exception)


class TestTemplateSyntaxError:
    """Tests for TemplateSyntaxError"""
    
    def test_message_only(self):
        error = TemplateSyntaxError("구문 오류")
        assert str(error) == "구문 오류"
        assert error.row is None
        assert error.col is None
    
    def test_with_row(self):
        error = TemplateSyntaxError("구문 오류", row=5)
        assert str(error) == "구문 오류 at row 5"
        assert error.row == 5
        assert error.col is None
    
    def test_with_row_and_col(self):
        error = TemplateSyntaxError("구문 오류", row=5, col=3)
        assert str(error) == "구문 오류 at row 5, col 3"
        assert error.row == 5
        assert error.col == 3
    
    def test_inheritance(self):
        error = TemplateSyntaxError("테스트")
        assert isinstance(error, TemplateError)
        assert isinstance(error, Exception)


class TestTemplateRenderError:
    """Tests for TemplateRenderError"""
    
    def test_message_only(self):
        error = TemplateRenderError("렌더링 오류")
        assert str(error) == "렌더링 오류"
        assert error.row is None
        assert error.col is None
    
    def test_with_row(self):
        error = TemplateRenderError("렌더링 오류", row=10)
        assert str(error) == "렌더링 오류 at row 10"
        assert error.row == 10
        assert error.col is None
    
    def test_with_row_and_col(self):
        error = TemplateRenderError("렌더링 오류", row=10, col=2)
        assert str(error) == "렌더링 오류 at row 10, col 2"
        assert error.row == 10
        assert error.col == 2
    
    def test_inheritance(self):
        error = TemplateRenderError("테스트")
        assert isinstance(error, TemplateError)
        assert isinstance(error, Exception)
