import subprocess
import os
from typing import Optional
from .registry import tool
from .schemas import CompileLatexArgs
from src.context import get_chat_id
from src.database import DATABASE
from pathlib import Path

def get_user_pdf_path() -> Path:
    chat_id = get_chat_id()
    if not chat_id:
        raise RuntimeError("No chat_id saved")

    return DATABASE.get_pdf_path(chat_id)

@tool(
        name="compile_latex",
        model=CompileLatexArgs,
        description="Compile a LaTeX file and return any erros or success status.",
        parameters={
            "path": {"type": "string", "description": "Path to the .tex file to compile"},
            "output_dir": {"type": "string", "description": "Path to the .pdf output"}
            }
        )
def compile_latex(path: str, output_dir: Optional[str] = "./output/") -> str:
    if not os.path.exists(path):
        return f"Error: File not found {path}"
    if not path.endswith(".tex"):
        return f"Error: Not a .tex file, got: {path}"
    
    work_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(work_dir, exist_ok=True)

    try:
        cmd = ["pdflatex", "-interaction=nonstopmode", "-output-directory", get_user_pdf_path(), os.path.abspath(path)]
        result = subprocess.run(
                cmd,
                capture_output = True,
                text=True,
                timeout=60
                )
        if result.returncode == 0:
            pdf_name = os.path.splitext(os.path.basename(path))[0] + ".pdf"
            pdf_path = os.path.join(work_dir, pdf_name)
            return f"Compiled successful. PDF saved to: {pdf_path}"
        else:
            errors = _extract_latex_errors(result.stdout + result.stderr)
            return f"Compilation failed.\n\n{errors}"

    except FileNotFoundError:
        return "Error: pdflatex not found. Install TeX Live or MiKTeX."
    except subprocess.TimeoutExpired:
        return "Error: Compilation timed out after 60 seconds."
    except Exception as e:
        return f"Unexpected error: {e}"


def _extract_latex_errors(log: str) -> str:
    """Pull error/warning lines from pdflatex log output."""
    lines = log.splitlines()
    relevant = []
    for i, line in enumerate(lines):
        if line.startswith("!"):          # hard errors
            relevant.append(line)
            # grab the next couple of lines for context (line number, etc.)
            relevant.extend(lines[i+1:i+4])
        elif "Warning" in line:           # warnings (optional, can remove)
            relevant.append(line)

    if not relevant:
        # fallback: return the last 30 lines if nothing matched
        relevant = lines[-30:]

    return "\n".join(relevant)
