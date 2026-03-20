import subprocess
from pathlib import Path
import os

def compile_latex(OUTPUT_DIR: Path, CV_PATH: Path) -> Path:
    result = subprocess.run(
            ['pdflatex', '-output-directory', str(OUTPUT_DIR), str(CV_PATH)],
            capture_output=True,
            text=True,
            timeout=60
    )
    
    pdf_path = OUTPUT_DIR / 'cv.pdf'

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"Pdf not genrated.\n{result.stdout}\n{result.stderr}")

    print(f'PDF COMPILED')
    return pdf_path
