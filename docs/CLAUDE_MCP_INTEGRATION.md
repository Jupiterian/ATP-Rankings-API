# CLAUDE MCP INTEGRATION

The following details how to integrate the MCP server with Claude Desktop

## 1. Download and Install Claude Desktop
If you haven't done so already, download and install claude desktop here: [text](https://www.claude.com/download)

## 2. Configure the MCPServer in the file
Now, you must configure your MCP server file

For Mac:
Go to ```~/Library/Application Support/Claude```
For Windows:
Go to ```%APPDATA%\Claude```

Make a new file called claude_desktop_config.json

Paste in the following contents:

```
{
  "mcpServers": {
    "atp-rankings": {
      "command": "python",
      "args": ["C:\\full\\path\\to\\atp_mcp_bridge.py"]
    }
  }
}
```

## 3. Python File

The MCP server is dependent on the following python code. Create a new file and update the path in claude_desktop_config.json. Make sure you have all the installed modules.

```
#!/usr/bin/env python3
import asyncio
import httpx
import sys
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

MCP_SERVER_URL = "https://atp-rankings-data-visualization.onrender.com/mcp"

server = Server("atp-rankings-bridge")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools from remote MCP server"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MCP_SERVER_URL}/manifest")
            manifest = response.json()
            
            print(f"Manifest received: {json.dumps(manifest, indent=2)}", file=sys.stderr)
            
            # FIX: Tools are under capabilities.tools, not at root
            remote_tools = manifest.get("capabilities", {}).get("tools", [])
            
            print(f"Found {len(remote_tools)} tools", file=sys.stderr)
            
            # Convert to Tool objects
            tools = []
            for tool in remote_tools:
                tool_obj = Tool(
                    name=tool.get("name", ""),
                    description=tool.get("description", ""),
                    inputSchema=tool.get("inputSchema", {})
                )
                tools.append(tool_obj)
                print(f"Registered tool: {tool_obj.name}", file=sys.stderr)
            
            return tools
    except Exception as e:
        print(f"Error listing tools: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Forward tool calls to remote MCP server"""
    try:
        print(f"Calling tool: {name} with args: {arguments}", file=sys.stderr)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{name}",
                json=arguments or {}
            )
            result = response.json()
            
            print(f"Tool result: {result}", file=sys.stderr)
            
            # Convert result to string for text content
            result_text = json.dumps(result, indent=2)
            
            return [TextContent(
                type="text",
                text=result_text
            )]
    except Exception as e:
        error_msg = f"Error calling tool {name}: {e}"
        print(error_msg, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return [TextContent(
            type="text",
            text=error_msg
        )]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="atp-rankings-bridge",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
        await server.run(
            read_stream,
            write_stream,
            init_options
        )

if __name__ == "__main__":
    asyncio.run(main())
```