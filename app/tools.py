from typing import Dict, Any, Callable


class ToolRegistry:
    """Registry for managing workflow tools (functions)"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        """Register a new tool"""
        self._tools[name] = func
        print(f"Tool '{name}' registered")
    
    def get(self, name: str) -> Callable:
        """Get a tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]
    
    def list_tools(self) -> list:
        """List all registered tools"""
        return list(self._tools.keys())


# Global tool registry instance
tool_registry = ToolRegistry()


# Code Review Tools
def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract functions from code"""
    code = state.get("code", "")
    # Simple function extraction (counts def keywords)
    functions = []
    for i, line in enumerate(code.split('\n')):
        if 'def ' in line:
            func_name = line.split('def ')[1].split('(')[0].strip()
            functions.append({
                "name": func_name,
                "line": i + 1
            })
    
    state["functions"] = functions
    state["function_count"] = len(functions)
    print(f"Extracted {len(functions)} functions")
    return state


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Check code complexity"""
    code = state.get("code", "")
    lines = code.split('\n')
    
    # Simple complexity metrics
    complexity_score = 0
    for line in lines:
        # Count control flow statements
        if any(keyword in line for keyword in ['if', 'for', 'while', 'elif']):
            complexity_score += 1
    
    state["complexity_score"] = complexity_score
    state["complexity_level"] = "high" if complexity_score > 10 else "medium" if complexity_score > 5 else "low"
    print(f"Complexity score: {complexity_score} ({state['complexity_level']})")
    return state


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect basic code issues"""
    code = state.get("code", "")
    issues = []
    
    lines = code.split('\n')
    for i, line in enumerate(lines):
        # Check for long lines
        if len(line) > 100:
            issues.append({
                "line": i + 1,
                "type": "long_line",
                "message": "Line exceeds 100 characters"
            })
        
        # Check for missing docstrings
        if 'def ' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line.startswith('"""') and not next_line.startswith("'''"):
                issues.append({
                    "line": i + 1,
                    "type": "missing_docstring",
                    "message": "Function missing docstring"
                })
    
    state["issues"] = issues
    state["issue_count"] = len(issues)
    print(f"Found {len(issues)} issues")
    return state


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """Suggest code improvements"""
    suggestions = []
    
    complexity_level = state.get("complexity_level", "low")
    issue_count = state.get("issue_count", 0)
    
    if complexity_level == "high":
        suggestions.append("Consider breaking down complex functions into smaller ones")
    
    if issue_count > 5:
        suggestions.append("Address code style issues for better readability")
    
    if state.get("function_count", 0) > 10:
        suggestions.append("Consider organizing code into multiple modules")
    
    state["suggestions"] = suggestions
    print(f"Generated {len(suggestions)} suggestions")
    return state


def calculate_quality_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall quality score"""
    # Simple scoring algorithm
    base_score = 100
    
    # Deduct points for issues
    issue_count = state.get("issue_count", 0)
    base_score -= issue_count * 5
    
    # Deduct points for high complexity
    complexity_score = state.get("complexity_score", 0)
    if complexity_score > 15:
        base_score -= 20
    elif complexity_score > 10:
        base_score -= 10
    
    # Ensure score is between 0 and 100
    quality_score = max(0, min(100, base_score))
    
    state["quality_score"] = quality_score
    state["iteration"] = state.get("iteration", 0) + 1
    print(f"Quality score: {quality_score} (iteration {state['iteration']})")
    return state


# Register all tools
tool_registry.register("extract_functions", extract_functions)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("detect_issues", detect_issues)
tool_registry.register("suggest_improvements", suggest_improvements)
tool_registry.register("calculate_quality_score", calculate_quality_score)