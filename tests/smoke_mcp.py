import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(ROOT / "scripts" / "mcp_server.py")]
)

async def check_tool(
    client,
    name,
    arguments,
    expected_file,
    error_phrase,
):
    first = await client.call_tool(name, arguments)

    assert not first.is_error,(
        f"{name} first call failed: {first.content}"
    )
    assert first.structured_content is not None
    assert first.structured_content["status"] == "success"
    assert expected_file.is_file(), f"Missing: {expected_file}"

    second = await client.call_tool(name,arguments)

    assert second.is_error, f"{name} allowed overwrite"

    error_text = " ".join(
        part.text
        for part in second.content
        if part.type == "text"
    )

    assert error_phrase in error_text, error_text

async def main():
    async with Client(server_params) as client:
        result = await client.list_tools()

        names = {tool.name for tool in result.tools}
        required = {
            "generate_report",
            "compare_cases",
            "analyze_energy",
        }

        assert required.issubset(names), (
            f"Missing tools: {required - names}"
        )

        with TemporaryDirectory(
            prefix="mcp_smoke_",
            dir = ROOT / "output",
        ) as temp_dir:
            test_root = Path(temp_dir)

            report_path = (
                test_root / "report.md"
            ).relative_to(ROOT).as_posix()

            comparison_dir = (
                test_root / "comparison"
            ).relative_to(ROOT).as_posix()

            await check_tool(
                client,
                "generate_report",
                {
                    "input_dir": "output/cases/baseline",
                    "output_path": report_path,
                },
                test_root / "report.md",
                "already exists",
            )

            await check_tool(
                client,
                "compare_cases",
                {
                    "baseline_dir": "output/cases/baseline",
                    "candidate_dir": "output/cases/fixed_shading",
                    "output_dir": comparison_dir,
                },
                test_root / "comparison" / "comparison_summary.md",
                "not empty",
            )
    print("PASS: MCP smoke tests")


if __name__ == "__main__":
    asyncio.run(main())