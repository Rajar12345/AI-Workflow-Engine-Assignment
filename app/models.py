from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class NodeType(str, Enum):
    SIMPLE = "simple"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class Node(BaseModel):
    name: str
    node_type: NodeType = NodeType.SIMPLE
    tool_name: str
    condition: Optional[Dict[str, Any]] = None  # For conditional/loop nodes
    
    class Config:
        use_enum_values = True


class Edge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Optional condition for branching


class GraphDefinition(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str
    end_nodes: List[str]


class GraphCreateRequest(BaseModel):
    graph_definition: GraphDefinition
    name: Optional[str] = "unnamed_graph"


class GraphCreateResponse(BaseModel):
    graph_id: str
    message: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class ExecutionLog(BaseModel):
    node_name: str
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    timestamp: str


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    execution_logs: List[ExecutionLog]
    status: str


class StateResponse(BaseModel):
    run_id: str
    current_state: Dict[str, Any]
    current_node: Optional[str]
    status: str
    execution_logs: List[ExecutionLog]