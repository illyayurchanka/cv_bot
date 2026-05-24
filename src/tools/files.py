import os
from .registry import tool
from .schemas import ReadFileArgs, WriteFileArgs

from src.context import get_chat_id
from src.database import DATABASE
from pathlib import Path

def get_user_cv_path() -> Path:
    chat_id = get_chat_id()
    if not chat_id:
        raise RuntimeError("No chat_id saved")

    return DATABASE.get_cv_path(chat_id)


@tool(
        name="read_cv",
        model=ReadFileArgs,
        description="read teh contents  of a cv file.",
        parameters={
            }
        )
def read_cv() -> str:
    try:
        actualpath = get_user_cv_path()

        path = os.path.expanduser(actualpath)
        with open(path, "r") as f:
            content = f.read()
            return content[:10_000]
    except Exception as e:
        return f"error reading file: {e}"

@tool(
        name="write_cv",
        model=WriteFileArgs,
        description=(
            f"Write text content to a file on disk. "
            f"Use this to save the updated CV. "
            # f"The CV path is: {DEFAULT_CV}"
        ),
        parameters={
            "content": {"type": "string", "description": "Full text content to write to the file"},
            }
        )
def write_cv(content: str) -> str:
    try:
        actualpath = get_user_cv_path()

        path = os.path.expanduser(actualpath)
        with open(path, "w") as f:
            f.write(content)
        return f"successfully wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"error writing file: {e}"


