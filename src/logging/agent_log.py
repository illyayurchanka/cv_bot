from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentStep:
    iteration: int
    thought: str
    tool: str | None
    args: dict | None
    result: str | None
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

class AgentTrace:
    def __init__(self):
        self.steps: list[AgentStep] = []

    def add(self, **kwargs):
        step = AgentStep(**kwargs)
        self.steps.append(step)
        self._print(step)

    def _print(self, step: AgentStep):
        print(f"\n{'='*50}")
        print(f"[{step.timestamp}] Iteration {step.iteration}")
        if step.thought:
            print(f"Thought: {step.thought[:300]}")
        if step.tool:
            print(f"Tool: {step.tool}")
            print(f"Args: {step.args}")
        if step.result:
            print(f"Result: {step.result[:300]}")
        print(f"{'='*50}")
