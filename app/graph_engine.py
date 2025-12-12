import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models import (
    GraphDefinition, Node, Edge, NodeType,
    ExecutionLog, GraphRunResponse
)
from app.tools import tool_registry


class GraphEngine:
    """Core workflow/graph execution engine"""
    
    def __init__(self):
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
    
    def create_graph(self, graph_def: GraphDefinition, name: str = "unnamed") -> str:
        """Create and store a graph definition"""
        graph_id = str(uuid.uuid4())
        self.graphs[graph_id] = graph_def
        print(f"Graph '{name}' created with ID: {graph_id}")
        return graph_id
    
    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> GraphRunResponse:
        """Execute a graph with given initial state"""
        if graph_id not in self.graphs:
            raise ValueError(f"Graph {graph_id} not found")
        
        graph = self.graphs[graph_id]
        run_id = str(uuid.uuid4())
        
        # Initialize run tracking
        state = initial_state.copy()
        execution_logs: List[ExecutionLog] = []
        current_node_name = graph.start_node
        visited_nodes = set()
        max_iterations = 100  # Safety limit
        iteration = 0
        
        print(f"\n=== Starting graph execution (run_id: {run_id}) ===")
        
        # Build node and edge mappings
        nodes_map = {node.name: node for node in graph.nodes}
        edges_map = self._build_edges_map(graph.edges)
        
        while current_node_name and iteration < max_iterations:
            iteration += 1
            
            # Check if we reached an end node
            if current_node_name in graph.end_nodes:
                print(f"Reached end node: {current_node_name}")
                break
            
            # Get current node
            if current_node_name not in nodes_map:
                raise ValueError(f"Node '{current_node_name}' not found in graph")
            
            current_node = nodes_map[current_node_name]
            
            # Execute node
            print(f"\nExecuting node: {current_node_name} (type: {current_node.node_type})")
            state_before = state.copy()
            
            state = self._execute_node(current_node, state)
            
            # Log execution
            execution_logs.append(ExecutionLog(
                node_name=current_node_name,
                state_before=state_before,
                state_after=state.copy(),
                timestamp=datetime.now().isoformat()
            ))
            
            # Determine next node
            next_node = self._get_next_node(
                current_node, 
                current_node_name, 
                edges_map, 
                state
            )
            
            if next_node == current_node_name and current_node.node_type == NodeType.LOOP:
                # Loop condition check
                if not self._check_loop_condition(current_node, state):
                    # Exit loop, find next node after loop
                    next_node = self._find_exit_node(current_node_name, edges_map, state)
                    print(f"Loop condition not met, exiting to: {next_node}")
            
            current_node_name = next_node
        
        if iteration >= max_iterations:
            print(f"WARNING: Max iterations ({max_iterations}) reached")
        
        # Store run results
        self.runs[run_id] = {
            "graph_id": graph_id,
            "state": state,
            "logs": execution_logs,
            "status": "completed",
            "current_node": None
        }
        
        print(f"\n=== Graph execution completed ===")
        
        return GraphRunResponse(
            run_id=run_id,
            final_state=state,
            execution_logs=execution_logs,
            status="completed"
        )
    
    def _execute_node(self, node: Node, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node"""
        # Get the tool function
        tool_func = tool_registry.get(node.tool_name)
        
        # Execute the tool
        return tool_func(state)
    
    def _build_edges_map(self, edges: List[Edge]) -> Dict[str, List[Edge]]:
        """Build a mapping of from_node -> list of edges"""
        edges_map = {}
        for edge in edges:
            if edge.from_node not in edges_map:
                edges_map[edge.from_node] = []
            edges_map[edge.from_node].append(edge)
        return edges_map
    
    def _get_next_node(
        self, 
        current_node: Node, 
        current_node_name: str, 
        edges_map: Dict[str, List[Edge]], 
        state: Dict[str, Any]
    ) -> Optional[str]:
        """Determine the next node to execute"""
        
        if current_node_name not in edges_map:
            return None
        
        edges = edges_map[current_node_name]
        
        # Handle conditional nodes
        if current_node.node_type == NodeType.CONDITIONAL:
            for edge in edges:
                if edge.condition and self._evaluate_condition(edge.condition, state):
                    print(f"Condition '{edge.condition}' met, going to: {edge.to_node}")
                    return edge.to_node
            
            # Default edge (no condition)
            for edge in edges:
                if not edge.condition:
                    return edge.to_node
        
        # Handle loop nodes
        elif current_node.node_type == NodeType.LOOP:
            if self._check_loop_condition(current_node, state):
                # Continue loop
                return current_node_name
            else:
                # Exit loop
                return self._find_exit_node(current_node_name, edges_map, state)
        
        # Simple node - return first edge
        return edges[0].to_node if edges else None
    
    def _check_loop_condition(self, node: Node, state: Dict[str, Any]) -> bool:
        """Check if loop should continue"""
        if not node.condition:
            return False
        
        condition_str = node.condition.get("expression", "")
        return not self._evaluate_condition(condition_str, state)
    
    def _find_exit_node(
        self, 
        loop_node: str, 
        edges_map: Dict[str, List[Edge]], 
        state: Dict[str, Any]
    ) -> Optional[str]:
        """Find the exit node from a loop"""
        if loop_node not in edges_map:
            return None
        
        edges = edges_map[loop_node]
        
        # Look for an exit edge (usually marked with condition "exit")
        for edge in edges:
            if edge.condition and "exit" in edge.condition.lower():
                return edge.to_node
        
        # If no explicit exit edge, return last edge
        return edges[-1].to_node if edges else None
    
    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate a condition string against state"""
        try:
            # Simple condition evaluation
            # Format: "key operator value" e.g., "quality_score >= 70"
            
            # Replace state variables
            eval_str = condition
            for key, value in state.items():
                eval_str = eval_str.replace(key, str(value))
            
            # Safely evaluate
            result = eval(eval_str, {"__builtins__": {}}, {})
            return bool(result)
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def get_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of a completed run"""
        return self.runs.get(run_id)


# Global engine instance
graph_engine = GraphEngine()