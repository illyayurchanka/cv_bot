from contextvars import ContextVar
from typing import Optional

chat_id_var: ContextVar[Optional[str]] = ContextVar('chat_id', default=None)

def get_chat_id() -> Optional[str]:
    return chat_id_var.get()
