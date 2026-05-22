import os
from .registry import tool
from .schemas import ReadFileArgs, WriteFileArgs

DEFAULT_CV = os.path.expanduser('/Users/kuwe/projects/cv_bot/cv/377270414/cv.tex')

@tool(
        name="read_file",
        model=ReadFileArgs,
        description="read teh contents  of a local file.",
        parameters={
            "path": {"type": "string", "description": "Path to the file."}
            }
        )
def read_file(file_path: str | None = None, path: str | None = None) -> str:
    try:
        actualpath = file_path or path
        path = os.path.expanduser(DEFAULT_CV)
        with open(path, "r") as f:
            content = f.read()
            return content[:10_000]
    except Exception as e:
        return f"error reading file: {e}"

@tool(
        name="write_file",
        model=WriteFileArgs,
        description=(
            f"Write text content to a file on disk. "
            f"Use this to save the updated CV. "
            f"The CV path is: {DEFAULT_CV}"
        ),
        parameters={
            "content": {"type": "string", "description": "Full text content to write to the file"},
            "path": {"type": "string", "description": "Path to the file."}
            }
        )
def write_file(content: str, file_path: str | None = None, path: str | None = None) -> str:
    try:
        path = os.path.expanduser(DEFAULT_CV)
        with open(path, "w") as f:
            f.write(content)
        return f"successfully wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"error writing file: {e}"


