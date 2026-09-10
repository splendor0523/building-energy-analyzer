from pathlib import Path

import streamlit as st
import pandas as pd

from scripts.plot_energy import load_plot_data

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
BASE_METRICS_PATH = OUTPUT_DIR / "basic_metrics.csv"
ENERGY_CONTRIBUTION_PATH = OUTPUT_DIR / "energy_contribution.csv"
ENERGY_CONTRIBUTION_IMAGE_PATH = OUTPUT_DIR / "energy_contribution.png"
MONTHLY_ENERGY_PATH = OUTPUT_DIR / "monthly_energy.csv"
MONTHLY_ENERGY_IMAGE_PATH = OUTPUT_DIR / "monthly_energy.png"
PEAK_DAY_ENERGY_PATH = OUTPUT_DIR / "peak_day_energy.csv"
PEAK_DAY_ENERGY_IMAGE_PATH = OUTPUT_DIR / "peak_day_energy.png"

st.set_page_config(
    page_title="Building Energy Result Analyzer",  # 标签页的标题
    layout="wide"
)

st.title("Building Energy Result Analyzer")
st.write(
    "Analyze and visualize EnergyPlus building energy simulation results."
)
# ------ 读取指标文件&处理数据 ------
try:
    basic_metrics = load_plot_data(
        BASE_METRICS_PATH,
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
        ENERGY_CONTRIBUTION_PATH,
        [
            "component",
            "variable_name",
            "annual_energy_kwh",
            "contribution_percent",
        ],
        "Energy contribution data",
    )
    monthly_energy = load_plot_data(
        MONTHLY_ENERGY_PATH,
        [
            "month",
            "cooling_kwh",
            "heating_kwh",
        ],
        "Monthly energy data",
    )
    peak_day_energy = load_plot_data(
        PEAK_DAY_ENERGY_PATH,
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
except Exception as error:
    st.error("Failed to load basic energy metrics.")
    st.code(str(error))
    st.stop()

cooling_metrics = basic_metrics[basic_metrics["metric"] == "cooling_demand"]
heating_metrics = basic_metrics[basic_metrics["metric"] == "heating_demand"]

if len(cooling_metrics) != 1 or len(heating_metrics) != 1 :
    st.error("Cooling or heating metrics are missing or duplicated.")
    st.stop()

cooling_metrics = cooling_metrics.iloc[0]
heating_metrics = heating_metrics.iloc[0]

# ------ 做第一排四张指标卡 ------
cooling_peak_start = pd.to_datetime(
    cooling_metrics["peak_datetime_start"]
)

cooling_peak_end = pd.to_datetime(
    cooling_metrics["peak_datetime_end"]
)

heating_peak_start = pd.to_datetime(
    heating_metrics["peak_datetime_start"]
)
heating_peak_end = pd.to_datetime(
    heating_metrics["peak_datetime_end"]
)

st.subheader("Annual Energy Metrics")

col1,col2,col3,col4 = st.columns(4) # 这里 st.columns(4) 会把这一行平均分成四块。

with col1:
    st.metric(
        "Annual Cooling",
        f"{cooling_metrics["annual_energy_kwh"] / 1_000_000:.2f} GWh",
    )

with col2:
    st.metric(
        "Annual Heating",
        f"{heating_metrics["annual_energy_kwh"] / 1_000_000:.2f} GWh",
    )

with col3:
    st.metric(
        "Peak Cooling",
        f"{cooling_metrics['peak_hourly_energy_kwh']:,.2f} kWh",
    )
    st.caption(
        f"{cooling_peak_start:%Y-%m-%d %H:%M}"
        f"-{cooling_peak_end:%H:%M}"
    )

with col4:
    st.metric(
        "Peak Heating",
        f"{heating_metrics['peak_hourly_energy_kwh']:,.2f} kWh",
    )
    st.caption(
        f"{heating_peak_start:%Y-%m-%d %H:%M}"
        f"-{heating_peak_end:%H:%M}"
    )

#------ 做第二个视觉表格 ------
contribution_display = energy_contribution[
    [
        "component",
        "annual_energy_kwh",
        "contribution_percent",
    ]
].copy()

contribution_display["annual_energy_gwh"] = (
contribution_display["annual_energy_kwh"] / 1_000_000
)

contribution_display = contribution_display[
    [
        "component",
        "annual_energy_gwh",
        "contribution_percent",
    ]
].rename(
    columns={
        "component": "Component",
        "annual_energy_gwh": "Annual Energy (GWh)",
        "contribution_percent": "Contribution (%)",
    }
)

st.subheader("Heat Gain Contribution")
chart_col,table_col = st.columns([2,1]) #这个[2，1]是把页面分成三份，第一个占俩份，第二个占三份

with chart_col:
    if ENERGY_CONTRIBUTION_IMAGE_PATH.exists():
        st.image(
            ENERGY_CONTRIBUTION_IMAGE_PATH,
            width="stretch",
        )
    else:
        st.warning("Energy contribution chart not found")

with table_col:
    st.dataframe(
        contribution_display,
        hide_index=True,
        width="stretch"
    )

st.caption(
    "Contribution percentages represent the relative share among the four "
    "selected heat gain components, not the complete building heat balance."
)

# ------ 第三个视觉表格 ------
monthly_display = monthly_energy.copy()

monthly_display["cooling_gwh"] = (
    monthly_display["cooling_kwh"] / 1_000_000
)
monthly_display["heating_gwh"] = (
    monthly_display["heating_kwh"] / 1_000_000
)

monthly_display = monthly_display[
    [
        "month",
        "cooling_gwh",
        "heating_gwh",
    ]
].rename(
    columns={
        "month": "Month",
        "cooling_gwh": "Cooling (GWh)",
        "heating_gwh": "Heating (GWh)",
    }
)

st.subheader("Monthly Cooling and Heating Demand")
monthly_chart_col, monthly_table_col = st.columns([2, 1])

with monthly_chart_col:
    if MONTHLY_ENERGY_IMAGE_PATH.exists():
        st.image(
            MONTHLY_ENERGY_IMAGE_PATH,
            width="stretch",
        )
    else:
        st.warning("Monthly energy chart not found.")

with monthly_table_col:
    st.dataframe(
        monthly_display,
        hide_index=True,
        width="stretch",
    )

# ------ 第四个视觉表格 ------
st.subheader("Peak Day Hourly Profiles")

peak_chart_col, peak_table_col = st.columns([2, 1])

with peak_chart_col:
    if PEAK_DAY_ENERGY_IMAGE_PATH.exists():
        st.image(
            PEAK_DAY_ENERGY_IMAGE_PATH,
            width="stretch",
        )
    else:
        st.warning("Peak day energy chart not found.")

with peak_table_col:
    selected_load = st.selectbox(
        "Load type",
        ["cooling", "heating"],
    )

    selected_peak_day = peak_day_energy[
        peak_day_energy["load_type"] == selected_load
    ].copy()

    selected_peak_day["interval"] = (
        selected_peak_day["interval_start"].str[11:16]
        + "-"
        + selected_peak_day["datetime"].str[11:16]  # .str[11:16] 是把前面的字符串的11-16位取出来，并转化为字符串
    )

    selected_peak_day = selected_peak_day[
        [
            "hour",
            "interval",
            "energy_kwh",
        ]
    ].rename(
        columns={
        "hour": "Hour",
        "interval": "Interval",
        "energy_kwh": "Energy (kWh)", 
        }
    )
    
    peak_date = peak_day_energy.loc[
        peak_day_energy["load_type"] == selected_load,
        "peak_date",
    ].iloc[0]

    st.caption(f"Peak day: {peak_date}")

    st.dataframe(
        selected_peak_day,
        hide_index=True,
        width="stretch",
    )