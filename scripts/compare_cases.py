from pathlib import Path

from plot_energy import load_plot_data

import calendar

BASE_DIR = Path(__file__).resolve().parent.parent

BASELINE_DIR = BASE_DIR / "output" / "cases" / "baseline"
FIXED_SHADING_DIR = BASE_DIR / "output" / "cases" / "fixed_shading"

COMPARISON_DIR = BASE_DIR / "output" / "comparison"

BASELINE_METRICS_PATH = BASELINE_DIR / "basic_metrics.csv"
FIXED_SHADING_METRICS_PATH = FIXED_SHADING_DIR / "basic_metrics.csv"

BASIC_COMPARISON_PATH = COMPARISON_DIR / "basic_metrics_comparison.csv"

BASELINE_MONTHLY_PATH = BASELINE_DIR / "monthly_energy.csv"
FIXED_SHADING_MONTHLY_PATH = FIXED_SHADING_DIR / "monthly_energy.csv"

MONTHLY_COMPARISON_PATH = COMPARISON_DIR / "monthly_energy_comparison.csv"

COMPARISON_SUMMARY_PATH = (
    COMPARISON_DIR / "comparison_summary.md"
)


# ------ 读取所需要的csv ------
def load_basic_metrics(path:Path,case_name:str):
    return load_plot_data(
        path,
        [
            "metric",
            "annual_energy_kwh",
            "peak_hourly_energy_kwh",
            "peak_datetime_start",
            "peak_datetime_end",
        ],
        f"{case_name} basic metrics",
    )

#------ 读取月度数据 ------
def load_monthly_energy(path:Path,case_name:str):
    return load_plot_data(
        path,
        [
            "month",
            "cooling_kwh",
            "heating_kwh",
        ],
        f"{case_name} monthly energy",
    )

# ------ 合并俩个基础参数工作表和对比 ------
def create_basic_metrics_comparison(
        baseline,
        candidate,
):
    baseline_data = baseline[
        [
            "metric",
            "annual_energy_kwh",
            "peak_hourly_energy_kwh",
            "peak_datetime_start",
            "peak_datetime_end",
        ]
    ].copy()

    candidate_data = candidate[
        [
            "metric",
            "annual_energy_kwh",
            "peak_hourly_energy_kwh",
            "peak_datetime_start",
            "peak_datetime_end",
        ]
    ].copy()

    baseline_data = baseline_data.rename(
        columns = {
            "annual_energy_kwh": "baseline_annual_kwh",
            "peak_hourly_energy_kwh": "baseline_peak_kwh",
            "peak_datetime_start": "baseline_peak_start",
            "peak_datetime_end": "baseline_peak_end",
        }
    )

    candidate_data = candidate_data.rename(
        columns = {
            "annual_energy_kwh": "candidate_annual_kwh",
            "peak_hourly_energy_kwh": "candidate_peak_kwh",
            "peak_datetime_start": "candidate_peak_start",
            "peak_datetime_end": "candidate_peak_end",
        }
    )

    comparison = baseline_data.merge(
        candidate_data,
        on = "metric",
        how = "inner",
    )

    comparison["annual_difference_kwh"] = (
        comparison["candidate_annual_kwh"]
        - comparison["baseline_annual_kwh"]
    )

    comparison["annual_change_percent"] = (
        comparison["annual_difference_kwh"]
        / comparison["baseline_annual_kwh"]
        * 100
    )

    comparison["peak_difference_kwh"] = (
    comparison["candidate_peak_kwh"]
    - comparison["baseline_peak_kwh"]
    )

    comparison["peak_change_percent"] = (
    comparison["peak_difference_kwh"]
    / comparison["baseline_peak_kwh"]
    * 100
    )

    return comparison

#------ 月度比较 ------
def create_monthly_energy_comparison(
        baseline,
        candidate,
):
    baseline_data = baseline.rename(
        columns={
            "cooling_kwh": "baseline_cooling_kwh",
            "heating_kwh": "baseline_heating_kwh",
        }
    )

    candidate_data = candidate.rename(
        columns={
            "cooling_kwh": "candidate_cooling_kwh",
            "heating_kwh": "candidate_heating_kwh",
        }
    )

    comparison = baseline_data.merge(
        candidate_data,
        on = "month",
        how = "inner"
    )

    comparison["cooling_difference_kwh"] = (
        comparison["candidate_cooling_kwh"]
        - comparison["baseline_cooling_kwh"]
    )

    comparison["heating_difference_kwh"] = (
        comparison["candidate_heating_kwh"]
        - comparison["baseline_heating_kwh"]
    )

    comparison["cooling_change_percent"] = (
        comparison["cooling_difference_kwh"]
        / comparison["baseline_cooling_kwh"]
        * 100
    ).where(
        comparison["baseline_cooling_kwh"] != 0
    )

    comparison["heating_change_percent"] = (
        comparison["heating_difference_kwh"]
        / comparison["baseline_heating_kwh"]
        * 100
    ).where(
        comparison["baseline_heating_kwh"] != 0
    )

    return comparison

# ------ 提取最有意义的月度数据 ------
def extract_monthly_comparison_summary(monthly_comparison):
    max_cooling_reduction = monthly_comparison.loc[
        monthly_comparison["cooling_difference_kwh"].idxmin()
    ]

    max_heating_increase = monthly_comparison.loc[
        monthly_comparison["heating_difference_kwh"].idxmax()
    ]

    return {
        "max_cooling_reduction_month": int(
            max_cooling_reduction["month"]
        ),
        "max_cooling_reduction_kwh": float(
            max_cooling_reduction["cooling_difference_kwh"]
        ),
        "max_heating_increase_month": int(
            max_heating_increase["month"]
        ),
        "max_heating_increase_kwh": float(
            max_heating_increase["heating_difference_kwh"]
        ),
    }

# ------ 生成md文档 ------
def build_comparison_summary(
        basic_comparison,
        monthly_summary,
):
    cooling = basic_comparison[
        basic_comparison["metric"] == "cooling_demand"
    ].iloc[0]

    heating = basic_comparison[
        basic_comparison["metric"] == "heating_demand"
    ].iloc[0]

    cooling_month = calendar.month_name[
        monthly_summary["max_cooling_reduction_month"]
    ]

    heating_month = calendar.month_name[
        monthly_summary["max_heating_increase_month"]
    ]

    lines = [
        "# Simulation Case Comparison",
        "",
        "## Cases",
        "",
        "- Baseline: no shading",
        "- Candidate: fixed shading",
        "",
        "## Annual Energy Demand",
        "",
        (
            f"- Cooling demand change: "
            f"**{cooling['annual_difference_kwh'] / 1000:,.2f} MWh** "
            f"({cooling['annual_change_percent']:.2f}%)"
        ),
        (
            f"- Heating demand change: "
            f"**{heating['annual_difference_kwh'] / 1000:,.2f} MWh** "
            f"({heating['annual_change_percent']:.2f}%)"
        ),
        "",
        "## Peak Load Change",
        "",
        (
            f"- Cooling peak change: "
            f"**{cooling['peak_difference_kwh']:,.2f} kWh** "
            f"({cooling['peak_change_percent']:.2f}%)"
        ),
        (
            f"- Heating peak change: "
            f"**{heating['peak_difference_kwh']:,.2f} kWh** "
            f"({heating['peak_change_percent']:.2f}%)"
        ),
        "",
        "## Peak Time",
        "",
        (
            f"- Baseline cooling peak: "
            f"{cooling['baseline_peak_start'][:16]}"
            f"–{cooling['baseline_peak_end'][11:16]}"
        ),
        (
            f"- Fixed-shading cooling peak: "
            f"{cooling['candidate_peak_start'][:16]}"
            f"–{cooling['candidate_peak_end'][11:16]}"
        ),
        (
            f"- Baseline heating peak: "
            f"{heating['baseline_peak_start'][:16]}"
            f"–{heating['baseline_peak_end'][11:16]}"
        ),
        (
            f"- Fixed-shading heating peak: "
            f"{heating['candidate_peak_start'][:16]}"
            f"–{heating['candidate_peak_end'][11:16]}"
        ),
        "",
        "## Monthly Extremes",
        "",
        (
            f"- Largest monthly cooling reduction: "
            f"**{cooling_month}**, "
            f"{monthly_summary['max_cooling_reduction_kwh'] / 1000:,.2f} MWh"
        ),
        (
            f"- Largest monthly heating increase: "
            f"**{heating_month}**, "
            f"+{monthly_summary['max_heating_increase_kwh'] / 1000:,.2f} MWh"
        ),
        "",
        "## Interpretation",
        "",
        (
            "Fixed shading reduces annual cooling demand and cooling peak load, "
            "while increasing annual heating demand and heating peak load."
        ),
        (
            "This indicates a cooling-benefit and heating-penalty trade-off "
            "for the fixed-shading strategy."
        ),
        "",
    ]

    return "\n".join(lines)

def main():
    baseline = load_basic_metrics(
        BASELINE_METRICS_PATH,
        "Baseline",
    )

    fixed_shading = load_basic_metrics(
        FIXED_SHADING_METRICS_PATH,
        "Fixed shading",
    )

    comparison = create_basic_metrics_comparison(
        baseline,
        fixed_shading,
    )

    COMPARISON_DIR.mkdir(
        parents=True,
            exist_ok=True
    )

    comparison.to_csv(
        BASIC_COMPARISON_PATH,
        index=False,
    )

    baseline_monthly = load_monthly_energy(
        BASELINE_MONTHLY_PATH,
        "Baseline"
    )
    fixed_shading_monthly = load_monthly_energy(
        FIXED_SHADING_MONTHLY_PATH,
        "Fixed shading",
    )

    monthly_comparison = create_monthly_energy_comparison(
        baseline_monthly,
        fixed_shading_monthly
    )

    monthly_comparison.to_csv(
        MONTHLY_COMPARISON_PATH,
        index=False,
    )

    monthly_summary = extract_monthly_comparison_summary(
        monthly_comparison
    )

    comparison_summary = build_comparison_summary(
        comparison,
        monthly_summary,
    )

    COMPARISON_SUMMARY_PATH.write_text(
        comparison_summary,
        encoding = "utf-8"
    )

    print(
        f"Basic metrics comparison saved: "
        f"{BASIC_COMPARISON_PATH}"
    )

    print(
        f"Monthly energy comparison saved: "
        f"{MONTHLY_COMPARISON_PATH}"
    )

    print(monthly_summary)

    print(
    f"Comparison summary saved: "
    f"{COMPARISON_SUMMARY_PATH}"
    )

if __name__ == "__main__":
    main()
