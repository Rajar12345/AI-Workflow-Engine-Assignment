"""
Workflow Engine Application Package

A minimal workflow/graph execution engine that supports:
- Node-based workflow execution
- State management across nodes
- Conditional branching
- Loop support
- Tool registry for extensible functions
"""

__version__ = "1.0.0"
__author__ = "AI Engineering Intern"

# Import main components for easy access
from app.graph_engine import graph_engine
from app.tools import tool_registry
from app.models import (
    GraphDefinition,
    Node,
    Edge,
    NodeType,
    GraphCreateRequest,
    GraphRunRequest,
)

__all__ = [
    "graph_engine",
    "tool_registry",
    "GraphDefinition",
    "Node",
    "Edge",
    "NodeType",
    "GraphCreateRequest",
    "GraphRunRequest",
]