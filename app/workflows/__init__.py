"""
Workflows Package

Contains pre-defined workflow definitions that can be used as examples
or templates for creating custom workflows.

Available workflows:
- code_review: A code quality analysis workflow
"""

from app.workflows.code_review import get_code_review_workflow

__all__ = [
    "get_code_review_workflow",
]