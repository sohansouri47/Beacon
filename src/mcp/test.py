# import asyncio
# import logging
# from mcp.client.streamable_http import streamablehttp_client
# from mcp import ClientSession  # Make sure this import matches your installed MCP SDK

# # logging.basicConfig(level=logging.DEBUG)


# async def main():
#     mcp_url = "http://localhost:3000/mcp"
#     # If you need authorization headers, add them as headers={"Authorization": "Bearer ..."}
#     async with streamablehttp_client(mcp_url) as (reader, writer, *_):
#         async with ClientSession(reader, writer) as session:
#             print("Client connected!")
#             await session.initialize()  # Must call initialize before tool interactions

#             # List available tools
#             tools = await session.list_tools()
#             logging.info(tools)
#             print("Available tools:", [t.name for t in tools.tools])
#             logging.info([t.name for t in tools.tools])

#             # Call the operator_handoff tool (no arguments for this tool)
#             result = await session.call_tool(name="operator_handoff", arguments={})
#             print(result)


# if __name__ == "__main__":
#     asyncio.run(main())
