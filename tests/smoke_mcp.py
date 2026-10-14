import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parent.parent

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(ROOT / "scripts" / "mcp_server.py")]
)

async def main():
    async with Client(server_params) as client:
        result = await client.list_tools()

        for tool in result.tools:
            print("Tool name:", tool.name)
            print("Description", tool.description)
            print("Input schema:", tool.input_schema)

        result = await client.call_tool(
            "generate_report",
            {
                "input_dir":"output/cases/baseline",
                "output_path":"output/cases/baseline/mcp_smoke_report.md",
            },
        )

        print("Is error:", result.is_error)
        print("Structured result:", result.structured_content)

if __name__ == "__main__":
    asyncio.run(main())