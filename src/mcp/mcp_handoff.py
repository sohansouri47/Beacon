from mcp.server.fastmcp import FastMCP

import logging

mcp = FastMCP(
    "FireTools",
    host="0.0.0.0",
    port=3000,
)


@mcp.tool("call_firefighter")
def call_firefighter(reason: str):
    logging.info("callfighet")
    return "Handed off to operator, u can close the conversation"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
