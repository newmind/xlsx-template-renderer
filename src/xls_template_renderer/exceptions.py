"""
Custom exceptions for xls_template_renderer
"""


class TemplateError(Exception):
    """Base exception for template errors"""
    pass


class TemplateSyntaxError(TemplateError):
    """Raised when template syntax is invalid"""
    
    def __init__(self, message: str, row: int = None, col: int = None):
        self.row = row
        self.col = col
        location = ""
        if row is not None:
            location = f" at row {row}"
            if col is not None:
                location += f", col {col}"
        super().__init__(f"{message}{location}")


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails"""
    
    def __init__(self, message: str, row: int = None, col: int = None):
        self.row = row
        self.col = col
        location = ""
        if row is not None:
            location = f" at row {row}"
            if col is not None:
                location += f", col {col}"
        super().__init__(f"{message}{location}")
