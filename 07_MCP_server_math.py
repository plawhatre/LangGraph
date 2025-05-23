import mcp
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: float, b: float) -> float:
    "Add the given two numbers"
    return a+b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    "Multiply the given two numbers"
    return a*b

if __name__ == "__main__":
    print("Starting MCP Math Server.")
    mcp.run(transport="stdio")
