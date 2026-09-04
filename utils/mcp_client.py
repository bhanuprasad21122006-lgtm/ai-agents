from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPToolBridge:
    """
    Bridge to connect agents with MCP servers (e.g. filesystem tools).
    """

    def __init__(self, workspace_path: str, mcp_command: str = "npx", mcp_args: list = None):
        if mcp_args is None:
            mcp_args = ["-y", "@modelcontextprotocol/server-filesystem", workspace_path]
            
        self.server_parameters = StdioServerParameters(
            command=mcp_command,
            args=mcp_args,
        )

    async def initialize(self):
        """Legacy low-level connection factory; ADK should use create_toolset instead."""
        return stdio_client(self.server_parameters)

    def create_toolset(self):
        """Return ADK-managed MCP tools with confirmation required for server actions."""
        from google.adk.tools.mcp_tool import McpToolset

        return McpToolset(
            connection_params=self.server_parameters,
            require_confirmation=True,
        )
