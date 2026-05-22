from pydantic import BaseModel, field_validator
from typing import Optional
import os

def _no_traversal(v: str) -> str:
    resolved = os.path.realpath(v)
    cwd = os.path.realpath(os.getcwd())
    if not resolved.startswith(cwd):
        raise ValueError(f"Access outside working directory now allowed: {v}")
    return v

class ReadFileArgs(BaseModel):
    path: str
    _check = field_validator("path", mode="after")(_no_traversal)

class WriteFileArgs(BaseModel):
    path: str
    content: str
    _check = field_validator("path", mode="after")(_no_traversal)

class CompileLatexArgs(BaseModel):
    path: str
    engine: str = "pdflatex"
    output_dir: Optional[str] = None
    _check = field_validator("path", mode="after")(_no_traversal)

    @field_validator("engine")
    @classmethod
    def valid_engine(cls, v):
        allowed = {"pdflatex", "xelatex", "lualatex"}
        if v not in allowed:
            raise ValueError(f"Engine must be one of {allowed}")
        return v

class WebSearchArgs(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def clean_query(cls, v):
        if len(v) > 200:
            raise ValueError("Query too long (max 200 chars)")
        return v.strip()


ALLOWED_SCHEMES  = {"http", "https"}
BLOCKED_HOSTNAMES = {
    "localhost",
    "169.254.169.254",       # AWS metadata
    "metadata.google.internal",
    "169.254.170.2",         # ECS metadata
}



import ipaddress
import socket
from urllib.parse import urlparse

class WebFetchArgs(BaseModel):
    url: str
    format: str = "markdown"

    @field_validator("url")
    @classmethod
    def safe_url(cls, v: str) -> str:
        v = v.strip()

        try:
            parsed = urlparse(v)
        except Exception:
            raise ValueError("Could not parse URL")

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ValueError(
                    f"Scheme '{parsed.scheme}' not allowed - use http or https"
                    )

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            raise ValueError("URL has no hostname")

        if hostname in BLOCKED_HOSTNAMES:
            raise ValueError(f"Access to '{hostname}'  is not allowed")
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValueError(
                        f"Access to private/internal address {ip} is not allowed"
                        )
        except socket.gaierror:
            pass
        except ValueError:
            raise

        return v

    @field_validator("format")
    @classmethod
    def valid_format(cls, v: str) -> str:
        allowed = {"markdown", "text", "html"}
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v


