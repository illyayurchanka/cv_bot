from .registry import tool
@tool(
        name="run_python",
        description="Execute python code and return the output.",
        parameters={
            "code": {"type": "string", "description": "Python code to execute"}
            }
        )
def run_python(code: str) -> str:
    import io, contextlib
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {"__builtins__":__builtins__})
        result = output.getvalue()
        return result if result else "Code executed successfully (no output)"
    except Exception as e:
        return f"Error: {e}"

@tool(
    name="get_current_time",
    description="Get the current date and time.",
    parameters={}
)
def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
