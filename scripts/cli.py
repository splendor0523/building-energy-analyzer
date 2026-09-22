import argparse
from pathlib import Path

from analyze_energy import run_analysis
from compare_cases import run_comparison
from generate_report import run_report
from generate_ai_report import run_ai_report


def creat_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Building Energy Result Analyzer"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

# ------ 增加分析子解析器 ------
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze an EnergyPlus workbook",
    )

    analyze_parser.add_argument(
        "--input",
        required=True,
        help="Path to the EnergyPlus Excel workbook"
    )

    analyze_parser.add_argument(
        "--output",
        required=True,
        help="Directory for analysis outputs",
    )

# ------ 增加比较子解析器 ------
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare simulation cases",
    )

    compare_parser.add_argument(
        "--baseline",
        required=True,
        help="Directory containing baseline analysis results",
    )

    compare_parser.add_argument(
    "--candidate",
    required=True,
    help="Directory containing candidate analysis results",
    )

    compare_parser.add_argument(
    "--output",
    required=True,
    help="Directory for comparison outputs",
    )
# ------ 增加报告生成子解析器 ------
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a deterministic analysis report",
    )

    report_parser.add_argument(
        "--input",
        required=True,
        help="Directory containing analysis results",
    )

    report_parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated Markdown report",
    )

# ------ 增加AI报告生成子解析器 ------
    ai_report_parser = subparsers.add_parser(
        "ai-report",
        help="Generate an AI-assisted analysis report",
    )

    ai_report_parser.add_argument(
        "--input",
        required=True,
        help="Path to the comparison summary Markdown file",
    )

    ai_report_parser.add_argument(
    "--output",
    required=True,
    help="Path for the AI-generated Markdown report",
    )

    return parser

def main():
    parser = creat_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        run_analysis(
        Path(args.input),
        Path(args.output),
    )
    elif args.command == "compare":
        run_comparison(
            Path(args.baseline),
            Path(args.candidate),
            Path(args.output),
        )
    elif args.command == "report":
        run_report(
            Path(args.input),
            Path(args.output),
    )
    elif args.command == "ai-report":
        run_ai_report(
            Path(args.input),
            Path(args.output),
    )

if __name__ == "__main__":
    main()