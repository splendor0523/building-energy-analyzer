import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parent.parent

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "scripts" / "mcp_server.py")]
    )

    async with Client(server_params) as client:
        result = await client.call_tool(
            "analyze_energy",
            {
                "input_path":"data/cases/baseline/run_sql_export.xlsx",
                "output_dir":"output/cases/mcp_smoke_baseline",
            },
            read_timeout_seconds = 1200,
        )

    print("Is error",result.is_error)
    print("Structured result",result.structured_content)

    if result.is_error :
        print("Error details:",result.content)

if __name__ == "__main__":
    asyncio.run(main())