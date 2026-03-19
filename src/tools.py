import ast
import os
import operator
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def search_web_ddg(query: str, max_results: int = 3) -> str:
    """Searches the web using DuckDuckGo and returns a summary of results."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."

        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nLink: {r.get('href')}")

        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {e}"

def search_web_tavily(query: str, max_results: int = 3) -> str:
    """Searches the web using Tavily and returns a summary of results."""
    try:
        from tavily import TavilyClient
        client = TavilyClient()
        response = client.search(query=query, max_results=max_results)
        results = response.get("results", [])
        if not results:
            return "No results found."

        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('content')}\nLink: {r.get('url')}")

        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {e}"

def search_web(query: str, max_results: int = 3) -> str:
    """Searches the web using Tavily (if TAVILY_API_KEY is set) or DuckDuckGo."""
    if os.environ.get("TAVILY_API_KEY"):
        return search_web_tavily(query, max_results)
    return search_web_ddg(query, max_results)

def calculate(expression: str) -> str:
    """
    Safely evaluates a basic mathematical expression.
    Supported operators: +, -, *, /, **
    """
    allowed_operators = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg
    }

    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](_eval(node.operand))
        else:
            raise TypeError(node)

    try:
        # Replace common string mistakes
        safe_expr = expression.replace('^', '**')
        tree = ast.parse(safe_expr, mode='eval').body
        result = _eval(tree)
        return str(result)
    except Exception as e:
        return f"Error calculating '{expression}': Invalid mathematical expression. Ensure it only contains numbers and basic operators (+, -, *, /, **)."

def read_webpage(url: str) -> str:
    """Reads the main text content of a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        # Collapse whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Return first 4000 characters to avoid huge context limits if page is giant
        return text[:4000] + ("..." if len(text) > 4000 else "")
    except requests.RequestException as e:
        return f"Error reading webpage {url}: {e}"

# Tool Registry for easy access in the agent
TOOLS = {
    "search_web": search_web,
    "calculate": calculate,
    "read_webpage": read_webpage
}
