from .registry import tool
from .schemas import WebSearchArgs, WebFetchArgs
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import logging

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

MAX_RESPONSE_BYTES = 5 * 1024 * 1024 
MAX_OUTPUT_CHARS   = 8_000           
REQUEST_TIMEOUT    = 30  

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
NOISE_TAGS = [
    "script", "style", "noscript", "iframe",
    "nav", "footer", "header", "aside",
    "form", "button", "svg", "figure",
    "meta", "link",
]


@tool(
        name="web_search",
        model=WebSearchArgs,
        description="Search the web and return top results with snippets.",
        parameters={
            "query": {"type": "string", "description": "Search query"}
        }
    )
def web_search(query: str) -> str:
    """Search using DuckDuckGo (no API key needed).
       Args: search query
       Reutrns: list with 5 results:
           1. header
              url
              description

           2. header
              url
              description
           ...
    """
    url = "https://html.duckduckgo.com/html/"
    
    try:
        resp = requests.post(url, data={"q": query}, headers={
            "User-Agent": BROWSER_UA}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for r in soup.select(".result")[:5]:
            title = r.select_one(".result__title")
            snippet = r.select_one(".result__snippet")
            url_tag = r.select_one(".result__url")
            
            link = r.select_one("a.result__a")
            href = str(link["href"]) if link else None
            url = _extract_real_url(href) if href else (url_tag.get_text(strip=True) if url_tag else "")

            if title and url:
                results.append({
                    "title": title.get_text(strip=True),
                    "url": url,
                    "snippet": snippet.get_text(strip=True)[:200] if snippet else "",
                    })

            if not results:
                return "No resulst found"

            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r['title']}")
                lines.append(f"   URL: {r['url']}")
                if r["snippet"]:
                    lines.append(f"   {r['snippet']}")
                lines.append("")

            return "\n".join(lines).strip()
    except requests.exceptions.RequestException as e:
        return f"Error: search request failed - {e}"
    except Exception as e:
        return f"Error: unexpected error - {e}"


@tool(
        name="web_fetch",
        model=WebFetchArgs,
        description=(
            "Fetch the contents of a public URL and return it as clean text. Use format='markdown' (default) for articles and docs, 'text' for plain content, 'html' for raw markup. Public URL only - internal/private addresse are blocked."
            ),
        parameters={
            "url": {"type": "string", "description": "URL to fetch (http/https only)"},
            "format": {"type": "string", "description": "Output format: markdown | text | html (default: markdown)"}
            }
        )
def web_fetch(url: str, format: str = 'markdown') -> str:
    """Parses the page from provided url.
    Args: url of a page (http or https) as string; formtat of return string - ['markdown', 'text', 'html']
    Returns: parsed page (smaller than 5 Mb) in a defined format
    """
    logger.info(f"Launching default browser session for URL {url}")

    jina_endpoint = f"https://r.jina.ai/{url}"
    
    headers = {
        # Optional: Add your Jina API token here if you run into global rate limits
        # "Authorization": "Bearer jina_xxx...",
        "Accept": "text/plain" 
    }
    
    try:
        # 2. Make a fast, standard HTTP request to Jina's proxy cloud
        response = requests.get(jina_endpoint, headers=headers, timeout=REQUEST_TIMEOUT)
        
        # Capture error states from the target page returned via Jina
        if response.status_code in [403, 401, 404, 500]:
            return f"Error: Proxy fetch failed with HTTP {response.status_code} - {response.reason}"
            
        # Jina returns pristine Markdown text by default
        markdown_content = response.text
        
    except requests.exceptions.Timeout:
        return f"Error: Connection timed out after {REQUEST_TIMEOUT}s while calling proxy gateway."
    except Exception as e:
        return f"Error: Failed to fetch through Jina gateway - {str(e)}"

    if not markdown_content.strip():
        return "No content found."

    # 3. Format the raw Markdown response to fit the user's requested format
    if format == "markdown":
        output = markdown_content
    elif format == "text":
        # Strip out markdown symbols to get raw plain copy
        output = _markdown_to_text(markdown_content)
    else:
        # If the model explicitly requests HTML format, we generate a basic version from the Markdown
        # (Since Jina doesn't return raw source HTML easily over r.jina.ai, we handle fallback gracefully)
        output = f"\n{markdown_content}"

    # 4. Respect token limits
    if len(output) > MAX_OUTPUT_CHARS:
        output = output[:MAX_OUTPUT_CHARS] + f"\n\n[truncated — {len(output)} total chars]"

    return output.strip() or "No content found."
# iternal tools
def _extract_real_url(href: str) -> str:
    """DuckDuckGo wraps URLs in //duckduckgo.com/l/?uddg=<encoded_url> — unwrap it."""
    if not href:
        return ""
    parsed = urlparse(href)
    from urllib.parse import parse_qs
    params = parse_qs(parsed.query)
    if "uddg" in params:
        from urllib.parse import unquote
        return unquote(params["uddg"][0])
    return href

def _markdown_to_text(md_content: str) -> str:
    """A quick utility to strip standard markdown syntax characters for plain-text mode."""
    import re
    # Strip markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', md_content)
    # Strip headers (# Title -> Title)
    text = re.sub(r'#+\s+', '', text)
    # Strip bold/italic markers (* or _)
    text = re.sub(r'[\*\_]', '', text)
    # Filter empty or trailing blank lines
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)
