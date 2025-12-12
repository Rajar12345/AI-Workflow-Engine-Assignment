from app.models import GraphDefinition, Node, Edge, NodeType


def get_code_review_workflow() -> GraphDefinition:
    """
    Define the Code Review workflow:
    1. Extract functions
    2. Check complexity
    3. Detect issues
    4. Suggest improvements
    5. Calculate quality score
    6. Loop until quality_score >= 70 or max 3 iterations
    """
    
    nodes = [
        Node(
            name="extract",
            node_type=NodeType.SIMPLE,
            tool_name="extract_functions"
        ),
        Node(
            name="complexity",
            node_type=NodeType.SIMPLE,
            tool_name="check_complexity"
        ),
        Node(
            name="issues",
            node_type=NodeType.SIMPLE,
            tool_name="detect_issues"
        ),
        Node(
            name="suggestions",
            node_type=NodeType.SIMPLE,
            tool_name="suggest_improvements"
        ),
        Node(
            name="quality_check",
            node_type=NodeType.LOOP,
            tool_name="calculate_quality_score",
            condition={
                "expression": "quality_score >= 70 or iteration >= 3"
            }
        ),
        Node(
            name="end",
            node_type=NodeType.SIMPLE,
            tool_name="extract_functions"  # Dummy tool for end node
        )
    ]
    
    edges = [
        Edge(from_node="extract", to_node="complexity"),
        Edge(from_node="complexity", to_node="issues"),
        Edge(from_node="issues", to_node="suggestions"),
        Edge(from_node="suggestions", to_node="quality_check"),
        # Loop back to issues if quality not met
        Edge(from_node="quality_check", to_node="issues"),
        # Exit to end when loop condition is met
        Edge(from_node="quality_check", to_node="end", condition="exit")
    ]
    
    return GraphDefinition(
        nodes=nodes,
        edges=edges,
        start_node="extract",
        end_nodes=["end"]
    )