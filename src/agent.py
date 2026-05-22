from dotenv import load_dotenv
from src.tools import execute_tool, get_tool_schemas
from ollama import Client
import logging
from src.logging.agent_log import AgentTrace

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()
MODEL = "gemma4"
client = Client(host="http://localhost:11434")

with open("AGENTS.md", 'r', encoding='utf-8') as file:
    SYSTEM_PROMPT = file.read()
    logger.info("Load System Prompt")

def run_agent(task: str, max_iterations: int = 10, summarize: bool = True) -> str:
    """Run the agent on a task until completion."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task}
            ]
    logger.info("Load prompts.")
    tools = get_tool_schemas()
    # logger.info(f"Tools available: {[t['function']['name'] for t in tools]}") 
    # logger.info(f"Tools available: {[t['function']['parameters'] for t in tools]}") 
    trace = AgentTrace()
    
    page_read = False
    cv_changed = False
    cv_compiled = False
    if summarize:
        cv_compiled = True
        cv_changed = True

    for i in range(max_iterations):
        response = client.chat(model=MODEL, messages=messages, tools=tools)
        message = response.message
        messages.append({"role": "assistant", 
                         "content": message.content or "",
                         "tool_calls": message.tool_calls
                        })

        if not message.tool_calls:
            trace.add(
                    iteration = i+1,
                    thought=message.content or "",
                    tool=None,
                    args=None,
                    result="[FINAL ANSWER]"
            )

            result = message.content or ""
            if not cv_changed:
                logger.warning("Agent never called write_file!")
                messages.append({
                    "role": "user",
                    "content": f"You forgot to save the file. Call write_file now to save the updated CV."
                    })
                continue
            if not cv_compiled:
                logger.warning("Agent did not compiled file!")
                messages.append({
                    "role": "user",
                    "content": f"You did not compile file succesfully, please compile file."
                    })
                continue

            logger.info("Sending result to the user.")
            result = message.content or ""
            return result

        trace.add(
                iteration = i+1,
                thought=message.content or "(no thought)",
                tool=None,
                args=None,
                result=None
        )
        for tc in message.tool_calls:
            name = tc.function.name
            logger.info(f"Agent is using tool: {name}")
            if not page_read and name != 'web_fetch':
                messages.append({
                    "role": "user",
                    "content": f"You must read page from link first."
                    })
                break
            elif name == 'web_fetch':
                page_read = True
            elif name == 'write_file':
                cv_changed = True
                cv_compiled = False

            arguments = tc.function.arguments

            result = execute_tool(name, arguments)
            logger.info(f"Tool result: {result[:300]}")

            if name == 'compile_latex':
                if "failed" in str(result).lower() or "error" in str(result).lower():
                    cv_compiled = False
                    cv_changed = False
                    logger.warning("LaTeX compilation failed. Keeping cv_compiled = False")
                else:
                    cv_compiled = True

            trace.add(
                    iteration = i+1,
                    thought=None,
                    tool=name,
                    args=arguments,
                    result=str(result)
            )

            messages.append({
                "role":    "tool",
                "content": str(result),
                "name":    name,
            })
    result = "Max iterations reached."
    return "Agent reached max iterations without completing the task."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        task = "".join(sys.argv[1:])
    else:
        task = input("What should I do? ->")
    print(f"Working on task")
    result = run_agent(task)
    print(f"Result: {result}")


# import json
# from datetime import datetime
# import os
# def save_trace(messages: list, task: str, result: str):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     path = os.path.expanduser(f"~/projects/cv_bot/logs/trace_{timestamp}.txt")
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#
#     with open(path, "w") as f:
#         f.write(f"TASK: {task}\n")
#         f.write(f"TIME: {timestamp}\n")
#         f.write("=" * 60 + "\n\n")
#
#         for msg in messages:
#             role = msg["role"].upper()
#             f.write(f"[{role}]\n")
#
#             # tool calls block
#             if msg.get("tool_calls"):
#                 for tc in msg["tool_calls"]:
#                     f.write(f"  >> TOOL CALL: {tc.function.name}\n")
#                     f.write(f"  >> ARGS: {json.dumps(tc.function.arguments, indent=6)}\n")
#
#             # main content
#             if msg.get("content"):
#                 f.write(f"{msg['content']}\n")
#
#             # tool result
#             if role == "TOOL":
#                 f.write(f"  (tool: {msg.get('name', '?')})\n")
#
#             f.write("\n" + "-" * 60 + "\n\n")
#
#         f.write(f"FINAL RESULT:\n{result}\n")
#
#     logger.info(f"Trace saved to {path}")
