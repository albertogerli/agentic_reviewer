"""
Agent Tools System
Provides real executable tools for agents (Python execution, data validation, calculations).
"""

import json
import logging
import ast
import operator
import math
import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import traceback

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class SafePythonExecutor:
    """
    Executes Python code in a restricted safe environment.
    Allows only safe operations: math, basic data structures, common libraries.
    """
    
    # Safe built-ins allowed
    SAFE_BUILTINS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'list': list,
        'dict': dict,
        'set': set,
        'tuple': tuple,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'sorted': sorted,
        'reversed': reversed,
        'any': any,
        'all': all,
        'pow': pow,
        'divmod': divmod,
        'chr': chr,  # Convert int to character
        'ord': ord,  # Convert character to int
        'isinstance': isinstance,  # Type checking
        'type': type,  # Get type
        'map': map,  # Map function
        'filter': filter,  # Filter function
        'print': print,  # Debug output
    }
    
    # Safe modules/functions
    SAFE_MODULES = {
        'math': math,
    }
    
    def __init__(self):
        self.timeout = 5  # Max 5 seconds execution
        self.max_iterations = 1000
    
    def is_safe_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Check if code is safe to execute (no dangerous operations).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Dangerous patterns
        dangerous = [
            'import os', 'import sys', 'import subprocess',
            '__import__', 'eval', 'exec', 'compile',
            'open', 'file', 'input', 'raw_input',
            '__', 'globals', 'locals', 'vars',
            'delattr', 'setattr', 'getattr',
        ]
        
        code_lower = code.lower()
        for pattern in dangerous:
            if pattern in code_lower:
                return False, f"Dangerous operation detected: {pattern}"
        
        # Check AST for dangerous nodes
        for node in ast.walk(tree):
            # No imports except math
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in ['math']:
                        return False, f"Import not allowed: {alias.name}"
            
            # No from imports except math
            if isinstance(node, ast.ImportFrom):
                if node.module not in ['math']:
                    return False, f"Import from not allowed: {node.module}"
        
        return True, None
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute Python code safely with restricted environment.
        
        Args:
            code: Python code to execute
            context: Optional context variables (e.g., data to validate)
        
        Returns:
            ToolResult with output or error
        """
        import time
        start_time = time.time()
        
        # Safety check
        is_safe, error = self.is_safe_code(code)
        if not is_safe:
            return ToolResult(
                success=False,
                output=None,
                error=f"Unsafe code: {error}",
                execution_time=time.time() - start_time
            )
        
        try:
            # Create safe globals
            safe_globals = {
                '__builtins__': self.SAFE_BUILTINS,
                'math': math,
            }
            
            # Add context variables if provided
            if context:
                for key, value in context.items():
                    if isinstance(value, (int, float, str, list, dict, tuple, bool, type(None))):
                        safe_globals[key] = value
            
            # Create locals for execution
            safe_locals = {}
            
            # Execute code
            exec(code, safe_globals, safe_locals)
            
            # Get result (look for 'result' variable or last expression)
            if 'result' in safe_locals:
                output = safe_locals['result']
            elif safe_locals:
                # Get last assigned variable
                output = list(safe_locals.values())[-1]
            else:
                output = None
            
            execution_time = time.time() - start_time
            
            logger.info(f"Code executed successfully in {execution_time:.3f}s")
            
            return ToolResult(
                success=True,
                output=output,
                error=None,
                execution_time=execution_time
            )
            
        except NameError as e:
            execution_time = time.time() - start_time
            # Extract the undefined variable name
            var_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
            error_msg = f"NameError: Variable '{var_name}' is not defined.\n\n"
            error_msg += "💡 SOLUTION: You must extract and define '{var_name}' from the document text first.\n"
            error_msg += "Example:\n"
            error_msg += f"# Extract {var_name} from document\n"
            error_msg += f"import re\n"
            error_msg += f"{var_name} = []  # or parse from text\n"
            error_msg += f"# Then use {var_name} in calculations\n"
            logger.error(f"Code execution failed: NameError: {var_name} not defined")
            
            return ToolResult(
                success=False,
                output=None,
                error=error_msg,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Code execution failed: {error_msg}")
            
            return ToolResult(
                success=False,
                output=None,
                error=error_msg,
                execution_time=execution_time
            )


class AgentToolRegistry:
    """
    Registry of tools available to agents.
    Each tool has a schema (for OpenAI function calling) and an executor.
    """
    
    def __init__(self):
        self.tools = {}
        self.executor = SafePythonExecutor()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools for agents."""
        
        # Tool 1: Validate calculation
        self.register_tool(
            name="validate_calculation",
            description="""Validates a mathematical calculation or formula.
Use this to check if numbers add up correctly, verify percentages, validate growth rates, etc.
You can provide Python code to perform the calculation and it will be executed safely.

Example: To verify "Revenue grew 150% from €1M to €2.5M":
validate_calculation(
    description="Revenue growth calculation",
    code="initial = 1000000; final = 2500000; growth = ((final - initial) / initial) * 100; result = growth"
)
Returns: growth rate (should be 150.0)""",
            parameters={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What you are validating"
                    },
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Use 'result' variable for output."
                    }
                },
                "required": ["description", "code"]
            },
            executor=self._validate_calculation
        )
        
        # Tool 2: Analyze data consistency
        self.register_tool(
            name="analyze_data_consistency",
            description="""Analyzes consistency between multiple data points.
Use this to check if values in tables match text, if totals sum correctly, etc.

Example 1: Check if parts sum to whole (with data dict):
analyze_data_consistency(
    description="Check if Q1-Q4 sum to annual total",
    data={"Q1": 1.2, "Q2": 1.5, "Q3": 1.8, "Q4": 2.1, "Annual": 6.6},
    code="parts = [Q1, Q2, Q3, Q4]; total_calc = sum(parts); result = abs(total_calc - Annual) < 0.01"
)

Example 2: Check calculation (define data in code):
analyze_data_consistency(
    description="Verify revenue growth claim",
    code="initial = 1000000; final = 2500000; claimed_growth = 150; actual_growth = ((final - initial) / initial) * 100; result = abs(actual_growth - claimed_growth) < 0.1"
)
Returns: True if consistent, False otherwise""",
            parameters={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What consistency you are checking"
                    },
                    "data": {
                        "type": "object",
                        "description": "Optional dictionary of data points to analyze. If provided, variables will be available in code."
                    },
                    "code": {
                        "type": "string",
                        "description": "Python code to check consistency. You can define data in code or use 'data' parameter. Return result in 'result' variable."
                    }
                },
                "required": ["description", "code"]
            },
            executor=self._analyze_data_consistency
        )
        
        # Tool 3: Calculate statistics
        self.register_tool(
            name="calculate_statistics",
            description="""Calculates statistical measures (mean, median, std dev, etc.) from data.
Use this to verify statistical claims or analyze data distributions.

Example: Calculate average and check if claimed average is correct:
calculate_statistics(
    data=[12, 15, 18, 14, 16, 13],
    operations=["mean", "median", "min", "max"]
)
Returns: dict with calculated statistics""",
            parameters={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to analyze"
                    },
                    "operations": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["mean", "median", "min", "max", "sum", "count"]
                        },
                        "description": "Statistical operations to perform"
                    }
                },
                "required": ["data", "operations"]
            },
            executor=self._calculate_statistics
        )
    
    def register_tool(self, name: str, description: str, 
                     parameters: Dict[str, Any], executor: Callable):
        """Register a new tool."""
        self.tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            },
            "executor": executor
        }
        logger.info(f"Registered tool: {name}")
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all tools."""
        return [
            {
                "type": tool["type"],
                "function": tool["function"]
            }
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given arguments."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool not found: {tool_name}"
            )
        
        try:
            # Log what we received
            logger.debug(f"Executing tool '{tool_name}' with arguments: {arguments}")
            
            # Validate required parameters
            tool_schema = self.tools[tool_name]["function"]
            required_params = tool_schema["parameters"].get("required", [])
            
            missing_params = [p for p in required_params if p not in arguments]
            if missing_params:
                error_msg = f"Missing required parameters: {missing_params}. Received: {list(arguments.keys())}"
                logger.error(error_msg)
                return ToolResult(
                    success=False,
                    output=None,
                    error=error_msg
                )
            
            executor = self.tools[tool_name]["executor"]
            return executor(**arguments)
        except TypeError as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution error: {str(e)}"
            )
    
    # Tool executors
    
    def _validate_calculation(self, description: str, code: str) -> ToolResult:
        """Execute calculation validation."""
        logger.info(f"Validating calculation: {description}")
        logger.debug(f"Code: {code}")
        
        result = self.executor.execute(code)
        
        if result.success:
            logger.info(f"Calculation result: {result.output}")
        
        return result
    
    def _analyze_data_consistency(self, description: str, 
                                  data: Dict[str, Any] = None, 
                                  code: str = None) -> ToolResult:
        """Execute data consistency check."""
        logger.info(f"Analyzing consistency: {description}")
        
        # Validate inputs
        if code is None:
            return ToolResult(
                success=False,
                output=None,
                error="Missing 'code' parameter - Python code is required"
            )
        
        if data is None:
            logger.debug("No data dict provided, data will be defined in code")
            data = {}
        
        logger.debug(f"Data: {data}")
        logger.debug(f"Code: {code}")
        
        # Pass data as context
        result = self.executor.execute(code, context=data)
        
        if result.success:
            logger.info(f"Consistency check result: {result.output}")
        
        return result
    
    def _calculate_statistics(self, data: List[float], 
                             operations: List[str]) -> ToolResult:
        """Calculate statistical measures."""
        try:
            import statistics
            
            results = {}
            
            if "mean" in operations:
                results["mean"] = statistics.mean(data)
            
            if "median" in operations:
                results["median"] = statistics.median(data)
            
            if "min" in operations:
                results["min"] = min(data)
            
            if "max" in operations:
                results["max"] = max(data)
            
            if "sum" in operations:
                results["sum"] = sum(data)
            
            if "count" in operations:
                results["count"] = len(data)
            
            logger.info(f"Statistics calculated: {results}")
            
            return ToolResult(
                success=True,
                output=results,
                error=None
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )


# Global registry instance
_tool_registry = None

def get_tool_registry() -> AgentToolRegistry:
    """Get global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = AgentToolRegistry()
    return _tool_registry


def execute_agent_with_tools(client, model: str, messages: List[Dict[str, Any]], 
                             tools: Optional[List[Dict[str, Any]]] = None,
                             max_tool_iterations: int = 15) -> str:
    """
    Execute agent conversation with tool calling support.
    
    This function handles the tool calling loop:
    1. Send messages to model with available tools
    2. If model wants to call a tool, execute it
    3. Send tool result back to model
    4. Repeat until model gives final answer
    
    Args:
        client: OpenAI client
        model: Model to use
        messages: Conversation messages
        tools: Tool schemas (if None, uses all registered tools)
        max_tool_iterations: Maximum tool call iterations
    
    Returns:
        Final assistant response
    """
    registry = get_tool_registry()
    
    if tools is None:
        tools = registry.get_tool_schemas()
    
    if not tools:
        # No tools, just regular completion
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1.0
        )
        return response.choices[0].message.content
    
    # Tool calling loop
    current_messages = messages.copy()
    
    for iteration in range(max_tool_iterations):
        logger.debug(f"Tool calling iteration {iteration + 1}/{max_tool_iterations}")
        
        # Request with tools
        response = client.chat.completions.create(
            model=model,
            messages=current_messages,
            tools=tools,
            temperature=1.0
        )
        
        message = response.choices[0].message
        
        # Check if model wants to call tools
        if not message.tool_calls:
            # No more tool calls, return final response
            logger.info("Agent completed without tool calls" if iteration == 0 
                       else f"Agent completed after {iteration} tool calls")
            return message.content
        
        # Add assistant message with tool calls to conversation
        current_messages.append(message)
        
        # Execute each tool call
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
            
            logger.info(f"🔧 Executing tool: {tool_name}")
            logger.debug(f"   Arguments: {arguments}")
            
            # Execute tool
            result = registry.execute_tool(tool_name, arguments)
            
            # Format result message
            if result.success:
                content = json.dumps({
                    "success": True,
                    "output": result.output,
                    "execution_time": result.execution_time
                }, indent=2)
                logger.info(f"✅ Tool succeeded: {result.output}")
            else:
                # Enhanced error message for unsafe code
                error_msg = result.error
                
                # Check for NameError (undefined variables)
                if "NameError" in error_msg or "name '" in error_msg:
                    # Extract variable name from error
                    match = re.search(r"name '(\w+)' is not defined", error_msg)
                    var_name = match.group(1) if match else "the variable"
                    
                    error_msg += f"""\n\n⚠️ UNDEFINED VARIABLE ERROR!

You tried to use '{var_name}' but it doesn't exist in the Python context!

🔴 REMEMBER: Your code runs in an EMPTY environment.
Only variables YOU define exist!

❌ WRONG - Assuming variables exist:
```python
# These variables DON'T exist automatically:
result = {var_name}  # ❌ Not defined!
result = dump_summary['value']  # ❌ Not defined!
result = container.data  # ❌ Not defined!
```

✅ CORRECT - Define ALL values yourself:
```python
# Extract values from the document text
# Example: "Revenue €2.5M" and "Previous €1M"
old_revenue = 1000000  # Define from document
new_revenue = 2500000  # Define from document

# Now calculate
growth = ((new_revenue - old_revenue) / old_revenue) * 100
result = growth  # Returns: 150.0
```

💡 FIX:
1. Look at the document text
2. Extract the numerical values you need
3. DEFINE them as variables in your code
4. Then perform calculations

Please rewrite your code and DEFINE all variables first!"""
                
                # Check for eval/exec
                elif "eval" in error_msg.lower() or "exec" in error_msg.lower():
                    error_msg += """\n\n⚠️ FORBIDDEN OPERATION DETECTED!

You tried to use eval() or exec(), which are NOT ALLOWED for security reasons.

✅ CORRECT APPROACH - Use direct calculations:
```python
# Calculate directly
old_value = 1000000
new_value = 2500000
growth = ((new_value - old_value) / old_value) * 100
result = growth  # Returns: 150.0
```

❌ WRONG APPROACH - DON'T do this:
```python
# DON'T USE eval()!
result = eval("((2500000 - 1000000) / 1000000) * 100")  # ❌ FORBIDDEN!
```

Please rewrite your code using direct calculations, variables, and basic math operations."""
                
                content = json.dumps({
                    "success": False,
                    "error": error_msg
                }, indent=2)
                logger.warning(f"❌ Tool failed: {result.error}")
            
            # Add tool result to conversation
            current_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": content
            })
    
    # Max iterations reached - get final summary anyway
    logger.warning(f"⚠️ Max tool iterations ({max_tool_iterations}) reached - Data Validator couldn't complete all calculations")
    logger.info(f"💡 Requesting summary of completed analysis...")
    
    # Ask for summary of what was completed
    current_messages.append({
        "role": "user",
        "content": """Max iterations reached. Please provide a summary of your analysis based on what you were able to validate. 
        Include:
        1. What calculations/data you successfully verified
        2. What issues you encountered
        3. Any recommendations despite incomplete validation
        
        Be concise and practical."""
    })
    
    # Get final response
    response = client.chat.completions.create(
        model=model,
        messages=current_messages,
        temperature=1.0
    )
    
    return response.choices[0].message.content


# Utility: Create data validator agent with tools
def create_data_validator_instructions_with_tools() -> str:
    """Get instructions for data validator agent with tool usage."""
    return """You are a data validation expert with Python programming capabilities.

Your task is to verify numerical accuracy, calculations, and data consistency in the document.

YOU HAVE ACCESS TO PYTHON TOOLS TO EXECUTE REAL CALCULATIONS:

1. **validate_calculation** - Use this to verify any mathematical claim:
   - Growth rates, percentages
   - Revenue calculations
   - Financial projections
   - Any numerical formula

2. **analyze_data_consistency** - Use this to check if data is consistent:
   - Do parts sum to the whole?
   - Are values in tables consistent with text?
   - Do trends make sense?

3. **calculate_statistics** - Use this to compute statistical measures:
   - Averages, medians
   - Min/max values
   - Verify statistical claims

IMPORTANT: ACTUALLY USE THE TOOLS!
- When you find a calculation to verify, call validate_calculation
- When you find data to check, call analyze_data_consistency
- When you find statistics to verify, call calculate_statistics

Don't just SAY what you would check - ACTUALLY CHECK IT by calling the tools!

⚠️ PYTHON CODE SAFETY RESTRICTIONS:
Your Python code runs in a SAFE SANDBOX with the following rules:
- ✅ ALLOWED: math operations (+, -, *, /, **, %), math module, basic functions (sum, len, min, max, round)
- ✅ ALLOWED: variables, lists, dicts, loops, conditionals
- ❌ FORBIDDEN: eval(), exec(), compile(), __import__()
- ❌ FORBIDDEN: file operations (open, read, write)
- ❌ FORBIDDEN: system operations (os, sys, subprocess)
- ❌ FORBIDDEN: network operations

🔴 CRITICAL: VARIABLE SCOPE
Your code runs in an EMPTY CONTEXT. Only these variables exist:
- Variables YOU define in your code
- The 'data' dict (if you provide it as a parameter)
- Built-in functions (sum, len, etc.)

❌ THESE DO NOT EXIST (will cause NameError):
- Variables from the document (dump_summary, container, revenue, etc.)
- External data structures
- Anything not explicitly defined in your code

You must DEFINE ALL VALUES yourself from the document text!

✅ CORRECT Python Example:
```python
# Extract values from document text and define them
old_value = 1000000  # From document: "€1M in 2023"
new_value = 2500000  # From document: "€2.5M in 2024"

# Now calculate
growth = ((new_value - old_value) / old_value) * 100
result = growth  # Returns: 150.0
```

❌ INCORRECT Python Example (will cause NameError):
```python
# DON'T reference undefined variables!
result = dump_summary['revenue']  # ❌ dump_summary not defined!
result = container.value  # ❌ container not defined!
```

❌ ALSO WRONG - Don't use eval():
```python
expression = "((2500000 - 1000000) / 1000000) * 100"
result = eval(expression)  # ❌ eval() is forbidden!
```

💡 If you receive a "NameError" error:
- Check: Did you define ALL variables in your code?
- Don't assume variables exist from the document
- Extract values from text and assign to variables FIRST
- Then perform calculations on those variables

💡 If you receive an "Unsafe code" error:
- Check if you used eval(), exec(), or other forbidden operations
- Rewrite using direct calculations instead
- Use simple Python: variables, math operations, loops

For each issue found:
1. Use tools to verify the claim
2. Report the tool result
3. State if correct or incorrect (with evidence from tool)
4. Provide correction if needed

Example:
Document claims: "Revenue grew 150% from €1M to €2.5M"

You should:
1. Call validate_calculation with code to compute growth (NO eval!)
2. See the tool returns 150.0
3. Report: "✅ VERIFIED: Growth rate is correct (150%)"

OR if wrong:
1. Tool returns 250.0
2. Report: "❌ ERROR: Actual growth is 250%, not 150%"

Be thorough, use tools for EVERY numerical claim!"""

