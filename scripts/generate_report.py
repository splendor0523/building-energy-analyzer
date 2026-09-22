from pathlib import Path

from plot_energy import load_plot_data

import calendar

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

BASIC_METRICS_PATH = OUTPUT_DIR / "basic_metrics.csv"
ENERGY_CONTRIBUTION_PATH = OUTPUT_DIR / "energy_contribution.csv"
MONTHLY_ENERGY_PATH = OUTPUT_DIR / "monthly_energy.csv"
PEAK_DAY_ENERGY_PATH = OUTPUT_DIR / "peak_day_energy.csv"

REPORT_PATH = OUTPUT_DIR / "report.md"

def load_report_data(input_dir:Path):
    input_dir = Path(input_dir)

    basic_metrics_path = (
        input_dir / "basic_metrics.csv"
    )
    energy_contribution_path = (
        input_dir / "energy_contribution.csv"
    )
    monthly_energy_path = (
        input_dir / "monthly_energy.csv"
    )
    peak_day_energy_path = (
        input_dir / "peak_day_energy.csv"
    )

    basic_metrics = load_plot_data(
        basic_metrics_path,
        [
            "metric",
            "annual_energy_kwh",
            "peak_hourly_energy_kwh",
            "peak_datetime_start",
            "peak_datetime_end",
        ],
        "Basic metrics data",
    )

    energy_contribution = load_plot_data(
        energy_contribution_path,
        [
            "component",
            "variable_name",
            "annual_energy_kwh",
            "contribution_percent",
        ],
        "Energy contribution data",
    )

    monthly_energy = load_plot_data(
        monthly_energy_path,
        [
            "month",
            "cooling_kwh",
            "heating_kwh",
        ],
        "Monthly energy data",
    )

    peak_day_energy = load_plot_data(
        peak_day_energy_path,
        [
            "load_type",
            "peak_date",
            "hour",
            "interval_start",
            "datetime",
            "energy_kwh",
        ],
        "Peak day energy data",
    )

    return (
        basic_metrics,
        energy_contribution,
        monthly_energy,
        peak_day_energy,
    )

def extract_report_metrics(
        basic_metrics,
        energy_contribution,
        monthly_energy,
        peak_day_energy,
):
    cooling = basic_metrics[
        basic_metrics["metric"] == "cooling_demand"
    ]

    heating = basic_metrics[
        basic_metrics["metric"] =="heating_demand"
    ]

    if len(cooling) != 1 or len(heating) != 1:
        raise ValueError(
            "Cooling or heating metrics are missing or duplicated."
        )

    cooling = cooling.iloc[0]
    heating = heating.iloc[0]

    cooling_peak_month_row = monthly_energy.loc[
        monthly_energy["cooling_kwh"].idxmax()   # .idmax()返回“最大值那一行的索引标签”，所以要用 .loc
    ]

    heating_peak_month_row = monthly_energy.loc[
        monthly_energy["heating_kwh"].idxmax()
    ]

    cooling_peak_month = int(cooling_peak_month_row["month"])
    heating_peak_month = int(heating_peak_month_row["month"])

    cooling_peak_day = peak_day_energy.loc[
        peak_day_energy["load_type"] == "cooling",
        "peak_date"
    ].iloc[0]

    heating_peak_day = peak_day_energy.loc[
        peak_day_energy["load_type"] == "heating",
        "peak_date"
    ].iloc[0]

    heat_gain_contribution = {}
    for _,row in energy_contribution.iterrows():
        heat_gain_contribution[row["component"]] = {
            "annual_energy_gwh":float(
                row["annual_energy_kwh"] / 1_000_000
            ),
            "contribution_percent": float(
                row["contribution_percent"]
            ),
        }

        metrics = {
                "annual_cooling_gwh": float(
                    cooling["annual_energy_kwh"] / 1_000_000
                ),
                "annual_heating_gwh": float(
                    heating["annual_energy_kwh"] / 1_000_000
                ),
                "peak_cooling_kwh": float(cooling["peak_hourly_energy_kwh"]),
                "peak_heating_kwh": float(heating["peak_hourly_energy_kwh"]),
                "cooling_peak_start": cooling["peak_datetime_start"],
                "cooling_peak_end": cooling["peak_datetime_end"],
                "heating_peak_start": heating["peak_datetime_start"],
                "heating_peak_end": heating["peak_datetime_end"],
                "cooling_peak_month": calendar.month_name[cooling_peak_month],
                "cooling_peak_month_gwh": float(
                    cooling_peak_month_row["cooling_kwh"] / 1_000_000
                ),
                "heating_peak_month": calendar.month_name[heating_peak_month],
                "heating_peak_month_gwh": float(
                    heating_peak_month_row["heating_kwh"] / 1_000_000
                ),
                "cooling_peak_day": cooling_peak_day,
                "heating_peak_day": heating_peak_day,
                "heat_gain_contributions": heat_gain_contribution,
            }

    return metrics

def build_report(metrics):
    lines = [
        "# Building Energy Analysis Report",
        "",
        "## 1. Annual Energy Demand",
        "",
        (
            f"- Annual cooling demand: "
            f"**{metrics['annual_cooling_gwh']:.2f} GWh**"
        ),
        (
            f"- Annual heating demand: "
            f"**{metrics['annual_heating_gwh']:.2f} GWh**"
        ),
        "",
        "## 2. Peak Loads",
        "",
        (
            f"- Peak cooling demand: "
            f"**{metrics['peak_cooling_kwh']:,.2f} kWh**"
        ),
        (
            f"- Cooling peak interval: "
            f"{metrics['cooling_peak_start'][:16]}"
            f"–{metrics['cooling_peak_end'][11:16]}"
        ),
        (
            f"- Peak heating demand: "
            f"**{metrics['peak_heating_kwh']:,.2f} kWh**"
        ),
        (
            f"- Heating peak interval: "
            f"{metrics['heating_peak_start'][:16]}"
            f"–{metrics['heating_peak_end'][11:16]}"
        ),
        "",
                "## 3. Monthly Performance",
        "",
        (
            f"- Peak cooling month: "
            f"**{metrics['cooling_peak_month']}** "
            f"({metrics['cooling_peak_month_gwh']:.2f} GWh)"
        ),
        (
            f"- Peak heating month: "
            f"**{metrics['heating_peak_month']}** "
            f"({metrics['heating_peak_month_gwh']:.2f} GWh)"
        ),
        "",
        "## 4. Heat Gain Contributions",
        "",
    ]
    for component,values in metrics["heat_gain_contributions"].items():
        component_label = component.replace("_"," ").title()

        lines.append(
            f"-{component_label}: "
            f"**{values["annual_energy_gwh"]:.2f} GWh**"
            f"({values["contribution_percent"]:.2f}%)"
        )

    lines.extend(
            [
        "",
        (
            "The percentages above represent the relative share among "
            "the four selected heat gain components, not the complete "
            "building heat balance."
        ),
        "",
        "## 5. Peak-Day Profiles",
        "",
        (
            f"- Cooling peak day: "
            f"**{metrics['cooling_peak_day']}**"
        ),
        (
            f"- Heating peak day: "
            f"**{metrics['heating_peak_day']}**"
        ),
        "",
        (
            "Complete 24-hour peak-day profiles are available in "
            "`peak_day_energy.csv`."
        ),
        "",
        "## 6. Interpretation Notes",
        "",
        (
            "- Cooling and heating values are based on EnergyPlus "
            "Ideal Loads results."
        ),
        (
            "- These values represent building cooling and heating "
            "demand, not actual HVAC electricity consumption."
        ),
        (
            "- Heat gain contribution percentages include only the "
            "four selected components used in this analysis."
        ),
        "",
        ]
    )

    return "\n".join(lines)

def save_report(report_text:str,
                report_path:Path,
) -> None:
    report_path = Path(report_path)

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        report_text,
        encoding="utf-8"
    )

def run_report(
        input_dir: Path,
        report_path:Path,
) -> None:
    (
        basic_metrics,
        energy_contribution,
        monthly_energy,
        peak_day_energy,
    ) = load_report_data(input_dir)

    metrics = extract_report_metrics(
        basic_metrics,
        energy_contribution,
        monthly_energy,
        peak_day_energy,
    )

    report_text = build_report(
        metrics
    )

    save_report(
        report_text,
        report_path,
    )

    print(
        f"Report saved to: {report_path}"
    )


def main():
    run_report(
        OUTPUT_DIR,
        REPORT_PATH,
    )


if __name__ == "__main__":
    main()