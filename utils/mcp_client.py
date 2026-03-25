import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

class MCPToolBridge:
    """
    Bridge to connect agents with MCP servers (e.g. filesystem tools).
    """

    def __init__(self, mcp_command: str = "node", mcp_args: list = None):
        if mcp_args is None:
            # Example: Default to using npx with a standard file system server if installed
            mcp_args = ["-y", "@modelcontextprotocol/server-filesystem", "./generated_game"]
            
        self.server_parameters = StdioServerParameters(
            command=mcp_command,
            args=mcp_args,
        )

    async def initialize(self):
        """Initializes the MCP Server Connection."""
        self.client = stdio_client(self.server_parameters)
        return self.client
