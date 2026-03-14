import subprocess
from src.logger import get_logger
from src.config import BASE_DIR
log = get_logger('agent')

OPENCODE_WORKDIR = str(BASE_DIR)

def run_agent(url: str, chat_id: str) -> str:

    prompt = f"Tailor the CV for this job offer: {url}"
    
    log.info(f"Agent started | chat_id={chat_id} | url={url}")
    print(f'Running agent for cv tailoring')

    process = subprocess.Popen(
        ['opencode', 'run', prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=OPENCODE_WORKDIR   # opencode picks up AGENTS.md and opencode.json from here
    )

    output_lines = []

    for line in process.stdout:
        line = line.strip()
        if line:
            log.debug(f'[opencode] {line}')
            output_lines.append(line)
    # Capture any errors
    stderr = process.stderr.read().strip()
    process.wait()

    if process.returncode != 0:
        log.error(f'Agent failed | chat_id={chat_id} | error={stderr}')
        raise RuntimeError(f'OpenCode error: {stderr}')

    log.info(f'Agent finished | chat_id={chat_id} | lines={len(output_lines)}')
    return '\n'.join(output_lines)
