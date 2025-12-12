from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    GraphCreateRequest, GraphCreateResponse,
    GraphRunRequest, GraphRunResponse,
    StateResponse
)
from app.graph_engine import graph_engine
from app.workflows.code_review import get_code_review_workflow
import uvicorn

app = FastAPI(
    title="Workflow Engine API",
    description="A minimal workflow/graph execution engine",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "endpoints": {
            "POST /graph/create": "Create a new graph",
            "POST /graph/run": "Run a graph with initial state",
            "GET /graph/state/{run_id}": "Get the state of a run",
            "GET /graph/example": "Get example code review workflow"
        }
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(request: GraphCreateRequest):
    """
    Create a new workflow graph
    
    Example request body:
    ```json
    {
        "name": "my_workflow",
        "graph_definition": {
            "nodes": [...],
            "edges": [...],
            "start_node": "node1",
            "end_nodes": ["end"]
        }
    }
    ```
    """
    try:
        graph_id = graph_engine.create_graph(
            request.graph_definition,
            request.name or "unnamed_graph"
        )
        return GraphCreateResponse(
            graph_id=graph_id,
            message=f"Graph '{request.name}' created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest):
    """
    Run a graph with the given initial state
    
    Example request body:
    ```json
    {
        "graph_id": "uuid-here",
        "initial_state": {
            "code": "def hello():\\n    print('world')"
        }
    }
    ```
    """
    try:
        result = graph_engine.run_graph(
            request.graph_id,
            request.initial_state
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_run_state(run_id: str):
    """
    Get the current state of a workflow run
    """
    run_data = graph_engine.get_run_state(run_id)
    
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    return StateResponse(
        run_id=run_id,
        current_state=run_data["state"],
        current_node=run_data.get("current_node"),
        status=run_data["status"],
        execution_logs=run_data["logs"]
    )


@app.get("/graph/example")
async def get_example_workflow():
    """
    Get the pre-defined code review workflow as an example
    """
    workflow = get_code_review_workflow()
    
    # Create the workflow
    graph_id = graph_engine.create_graph(workflow, "code_review_example")
    
    return {
        "graph_id": graph_id,
        "workflow_definition": workflow.dict(),
        "example_initial_state": {
            "code": """def calculate_total(items):
    total = 0
    for item in items:
        if item['price'] > 0:
            if item['quantity'] > 0:
                total += item['price'] * item['quantity']
    return total

def process_order(order):
    if order:
        if order['status'] == 'pending':
            if order['payment_method']:
                print('Processing order')
"""
        },
        "description": "A code review workflow that extracts functions, checks complexity, detects issues, and loops until quality score >= 70"
    }


@app.get("/tools")
async def list_tools():
    """List all registered tools"""
    from app.tools import tool_registry
    return {
        "tools": tool_registry.list_tools()
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)