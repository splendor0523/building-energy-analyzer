import sys
from pathlib import Path
from mcp.server import MCPServer
from contextlib import redirect_stdout

from generate_report import run_report
from compare_cases import run_comparison
from analyze_energy import run_analysis
from mcp.server.mcpserver.exceptions import ToolError

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0,str(SCRIPTS_DIR))

mcp = MCPServer("Building Energy Analyzer")

@mcp.tool()
def generate_report(input_dir: str, output_path: str) -> dict[str,str]:
    """Generate a Markdown energy report from existing analysis results."""
    source = (ROOT / input_dir).resolve()
    destination = (ROOT / output_path).resolve()

    output_root = (ROOT / "output").resolve()

    if not source.is_relative_to(output_root):
        raise ValueError("Input must be inside the project output directory")

    if not destination.is_relative_to(output_root):
        raise ValueError("Output must be inside the project output directory.")

    if destination.suffix.lower() != ".md":
        raise ValueError("Report output must be a Markdown file.")

    if not source.is_dir():
        raise FileNotFoundError(f"Input directory not found: {source}")

    if destination.exists():
        raise ToolError(
            f"Report already exists: {destination}. "
            "Choose a new output filename"
        )

    run_report(source,destination)

    if not destination.is_file():
        raise RuntimeError(f"Report was not created: {destination}")

    return {
        "status": "success",
        "output_path": str(destination)
    }

@mcp.tool()
def compare_cases(
    baseline_dir: str,
    candidate_dir: str,
    output_dir: str,
) -> dict[str, str | list[str]]:
    """Compare no-shading and fixed-shading EnergyPlus cases and return a result summary."""
    baseline = (ROOT / baseline_dir).resolve()
    candidate = (ROOT / candidate_dir).resolve()
    destination = (ROOT / output_dir).resolve()

    # Restrict AI-controlled paths to the project output directory.
    output_root = (ROOT / "output").resolve()
    for directory in (baseline,candidate,destination):
        if not directory.is_relative_to(output_root):
            raise ValueError("Paths must stay inside the project output directory.")

    for directory in (baseline,candidate):
        for filename in("basic_metrics.csv", "monthly_energy.csv"):
            if not (directory / filename).is_file():
                raise FileNotFoundError(f"Missing: {directory / filename}")

    if destination.exists():
        if not destination.is_dir() or any(destination.iterdir()):
            raise ToolError(
                f"Output directory is not empty or is not a directory: "
                f"{destination}. Choose a new empty output directory."
            )

    with redirect_stdout(sys.stderr):
        run_comparison(baseline,candidate,destination)

        filenames = [
            "basic_metrics_comparison.csv",
            "monthly_energy_comparison.csv",
            "comparison_summary.md",
        ]

    for filename in filenames:
        if not (destination / filename).is_file():
            raise RuntimeError(f"Missing output: {destination / filename}")

    summary_path = destination / "comparison_summary.md"
    summary_text = summary_path.read_text(encoding="utf-8")

    return {
        "status": "success",
        "output_dir": str(destination),
        "generated_files": [str(destination / name) for name in filenames],
        "summary_text":summary_text,
    }

@mcp.tool()
def analyze_energy(
    input_path:str,
    output_dir:str,
) -> dict[str,str | list [str]]:
    """Analyze an EnergyPlus Excel workbook and generate structured energy results."""
    source = (ROOT / input_path).resolve()
    destination = (ROOT / output_dir).resolve()

    data_root = (ROOT / "data").resolve()
    output_root = (ROOT / "output").resolve()

    if not source.is_relative_to(data_root):
        raise ValueError("Input must be inside the project data directory.")

    if not destination.is_relative_to(output_root):
        raise ValueError("Output must be inside the project output directory.")

    if not source.is_file():
        raise ToolError(f"Input file not found: {source}")

    if source.suffix.lower() != ".xlsx":
        raise ValueError("Input must be an .xlsx file.")

    if destination.exists():
        if not destination.is_dir() or any(destination.iterdir()):
            raise ToolError(
                f"Output directory is not empty or is not a directory: "
                f"{destination}. Choose a new empty output directory."
            )

    with redirect_stdout(sys.stderr):
        run_analysis(source,destination)
    
    filenames = [
        "basic_metrics.csv",
        "monthly_energy.csv",
        "energy_contribution.csv",
        "peak_day_energy.csv",
        "selected_report_data.csv",
        "key_variables.csv",
        "workbook_overview.txt",
    ]

    for filename in filenames:
        if not (destination / filename).is_file():
            raise RuntimeError(f"Missing output: {destination / filename}")

    return {
        "status": "success",
        "input_path": str(source),
        "output_dir": str(destination),
        "generated_files": [str(destination / name) for name in filenames],
    }

if __name__ == "__main__":
    mcp.run()