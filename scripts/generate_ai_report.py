import os
from pathlib import Path

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

ENERGY_REPORT_PATH = OUTPUT_DIR / "report.md"
COMPARISON_REPORT_PATH = (
    OUTPUT_DIR / "comparison" / "comparison_summary.md"
)

AI_REPORT_PATH = OUTPUT_DIR / "ai_report.md"

def load_text_file(path:Path, file_name:str) -> str:
    if not path.exists():
        raise FileExistsError(
            f"{file_name} not found: {path}"
        )

    return path.read_text(encoding="utf=8")

def load_report_context(comparison_report_path:Path,) -> str:
    comparison_report = load_text_file(
        comparison_report_path,
        "Case comparison report",
    )

    return (
        "# Case Comparison Data\n\n"
        + comparison_report
    )

def build_ai_prompt(report_context: str) -> str:
    return f"""
You are analyzing building energy simulation results.

Use only the numerical facts and case definitions provided in the source data below.

Important rules:

1. Do not recalculate or alter any numerical values.
2. Do not invent missing simulation results.
3. Clearly distinguish cooling benefits from heating penalties.
4. Do not describe Ideal Loads results as actual HVAC electricity consumption.
5. Do not claim that the shading strategy improves total building performance
   without qualification.
6. Explain the trade-off between reduced cooling demand and increased heating demand.
7. If the source data does not support a conclusion, explicitly say that further
   analysis is required.
8. Do not infer thermal comfort, daylight, glare, or indoor temperature performance
   from energy-demand data alone.
9. Keep all percentages and energy values consistent with the source.
10. Write in clear technical English suitable for an engineering analysis report.

Please organize the report using these sections:

# AI-Assisted Building Energy Analysis

## 1. Executive Summary

Summarize the most important differences between the baseline and fixed-shading case.

## 2. Annual Energy Demand

Explain the annual cooling and heating changes.

## 3. Peak Hourly Demand

Explain the changes in peak hourly cooling and heating demand and any change in peak timing.
Do not convert the reported kWh values to kW.

## 4. Monthly Performance

Explain the months with the largest cooling benefit and heating penalty.

## 5. Cooling-Heating Trade-off

Explain the physical interpretation of the observed trade-off without making claims
that are not supported by the supplied results.

## 6. Limitations

State that the results represent EnergyPlus Ideal Loads demand rather than actual HVAC
electricity consumption, and note that energy-demand results alone are insufficient
to evaluate thermal comfort, daylight, glare, or overall building performance.

Source data:

{report_context}
""".strip()

def call_deepseek(prompt:str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "DEEPSEEK_API_KEY is not set."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    response = client.chat.completions.create(
        model = "deepseek-flash",
        messages=[
            {
                "role":"system",
                "content":(
                    "You are a careful building energy "
                    "analysis assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=False
    )

    report_text = response.choices[0].message.content

    if not report_text:
        raise ValueError(
            "DeepSeek returned an empty response."
        )

    return report_text.strip()

def save_ai_report(report_text:str,
                   report_path:Path,
) -> None:
    report_path = Path(report_path)

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        report_text + "\n",
        encoding="utf-8",
    )

def run_ai_report(
    comparison_report_path: Path,
    output_path: Path,
) -> None:
    report_context = load_report_context(
        comparison_report_path
    )

    ai_prompt = build_ai_prompt(
        report_context
    )

    ai_report = call_deepseek(
        ai_prompt
    )

    save_ai_report(
        ai_report,
        output_path,
    )

    print(
        f"AI report saved to: {output_path}"
    )

def main():
    run_ai_report(
        COMPARISON_REPORT_PATH,
        AI_REPORT_PATH,
    )


if __name__ == "__main__":
    main()