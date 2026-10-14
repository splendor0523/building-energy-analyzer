import sys
from pathlib import Path
from mcp.server import MCPServer


SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0,str(SCRIPTS_DIR))

from generate_report import run_report

mcp = MCPServer("Building Energy Analyzer")

@mcp.tool()
def generate_report(input_dir: str, output_path: str) -> dict[str,str]:
    """Generate a Markdown energy report from existing analysis results."""
    source = (ROOT / input_dir).resolve()
    destination = (ROOT / output_path).resolve()

    if not source.is_dir():
        raise FileNotFoundError(f"Input directory not found: {source}")

    run_report(source,destination)

    if not destination.is_file():
        raise RuntimeError(f"Report was not created: {destination}")

    return {
        "status": "success",
        "output_path": str(destination)
    }

if __name__ == "__main__":
    mcp.run()