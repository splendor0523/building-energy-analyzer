from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "output" / "energy_contribution.csv"
DEFAULT_OUTPUT = BASE_DIR / "output" / "energy_contribution.png"

MONTHLY_INPUT = BASE_DIR / "output" / "monthly_energy.csv"
MONTHLY_OUTPUT = BASE_DIR / "output" / "monthly_energy.png"

REQUIRED_COLUMNS = [
    "component",
    "annual_energy_kwh",
    "contribution_percent",
]

MONTHLY_REQUIRED_COLUMNS = [
    "month",
    "cooling_kwh",
    "heating_kwh",
]

COMPONENT_LABELS = {
    "people": "People",
    "lighting": "Lighting",
    "equipment": "Equipment",
    "solar_transmission": "Solar transmission",
}

# ------ 读取csv源数据，并安全行检查 ------
def load_plot_data(input_path: Path,
                   required_columns:list[str],
                   data_name:str,
                   ) -> pd.DataFrame:
    if not input_path.exists():
        raise FileExistsError(
             f"{data_name} not found: {input_path}"
        )

    contribution_data = pd.read_csv(input_path)

    missing_columns = [
        column
        for column in required_columns
        if column not in contribution_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in {data_name}: "
            + ", ".join(missing_columns)
            )

    return contribution_data

# ------ 数据准备 ------
def prepare_plot_data(
        contribution_data: pd.DataFrame,
) -> pd.DataFrame:
    plot_data = contribution_data.copy()

    plot_data["component_label"] = (
        plot_data["component"].map(COMPONENT_LABELS)  # .map() 是 Pandas 里专门用来“根据一个映射关系，把一列的值替换成另一组值
    )

    if plot_data["component_label"].isna().any():
        unknown_components = plot_data.loc[
            plot_data["component_label"].isna(),
            "component",
        ].tolist()

        raise ValueError(
            "Unknown energy contribution components: "
            + ",".join(unknown_components)
        )

    plot_data["annual_energy_gwh"] = (
        plot_data["annual_energy_kwh"] / 1000
    )

    return plot_data

# ------ 更换月份标签 ------
MONTH_LABELS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
def prepare_monthly_plot_data(
        monthly_data:pd.DataFrame
) -> pd.DataFrame:
    plot_data = monthly_data.copy()
    plot_data["month_label"] = plot_data["month"].map(MONTH_LABELS)

    plot_data["cooling_gwh"] = plot_data["cooling_kwh"] / 1000
    plot_data["heating_gwh"] = plot_data["heating_kwh"] / 1000

    return plot_data

# ------ 绘制月冷热需求对比图 ------
def save_monthly_energy_chart(
        plot_data:pd.DataFrame,
        output_path:Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure,axis = plt.subplots(
        figsize = (10,5),
    )

    indices = list(range(len(plot_data)))
    bar_wideth = 0.4

    cooling_positions =  [
        index - bar_wideth / 2
        for index in indices
    ]
    heating_position = [
        index + bar_wideth / 2
        for index in indices
    ]

    axis.bar(
        cooling_positions,
        plot_data["cooling_gwh"],
        width = bar_wideth,
        label = "Cooling"
    )

    axis.bar(
        heating_position,
        plot_data["heating_gwh"],
        width = bar_wideth,
        label = "Heating",
    )

    axis.set_title("Monthly Cooling and Heating Demand")
    axis.set_xlabel("Month")
    axis.set_ylabel("Monthly energy demand (GWh)")
    axis.set_xticks(indices,plot_data["month_label"])
    axis.legend() # 把之前标注的 label 显示成图例。

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi = 300,
        bbox_inches = "tight" # "“保存时自动裁掉多余白边，让图片内容撑满画面。”"
    )

    plt.close(figure)

# ------ 绘图函数 ------
def save_energy_contribution_chart(
        plot_data:pd.DataFrame,
        output_path:Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure,axis = plt.subplots(
        figsize = (9,5), 
    )
 #plt.subplots() 的作用：创建一张画布（Figure）和上面的坐标系（Axes），
 # 用于绘图。返回值顺序固定：先画布，后坐标轴；变量名可自定义，顺序不可调换。
    bars = axis.bar(
        plot_data["component_label"],
        plot_data["annual_energy_gwh"],
    )

    bar_labels = [
        f"{energy_gwh:,.1f} GWh\n{percent:.1f}%"
        for energy_gwh,percent in zip(    # zip(列表A, 列表B) = “把 A 的第一个和 B 的第一个绑一起，A 的第二个和 B 的第二个绑一起……直到最短的那个列表结束。”
            plot_data["annual_energy_gwh"],
            plot_data["contribution_percent"],
        )
    ]

    axis.set_ylim(
        0,
        plot_data["annual_energy_gwh"].max() * 1.15,
    )

    axis.bar_label(
        bars,
        labels=bar_labels,
        padding=4,
        fontsize=9,
    )

    axis.set_title(
        "Annual Heat Gain Contributions"
    )
    axis.set_xlabel("Component")
    axis.set_ylabel(
        "Annual heat contribution (GWh)"
    )
    figure.tight_layout() # 自动排版
    figure.savefig(
        output_path,
        dpi = 300,
        bbox_inches = "tight" # 切除周围多余白边
    )
    plt.close(figure)

def main() -> None:
    contribution_data = load_plot_data(
        input_path=DEFAULT_INPUT,
        required_columns=REQUIRED_COLUMNS,
        data_name="energy contribution file"
    )

    monthly_data = load_plot_data(
        input_path=MONTHLY_INPUT,
        required_columns=MONTHLY_REQUIRED_COLUMNS,
        data_name="monthly energy file"
    )

    monthly_plot_data = prepare_monthly_plot_data(monthly_data=monthly_data)

    save_monthly_energy_chart(
        plot_data=monthly_plot_data,
        output_path=MONTHLY_OUTPUT,
    )
    
    plot_data = prepare_plot_data(contribution_data)

    print("Energy contribution plot data:")
    print(
        plot_data[
            [
                "component_label",
                "annual_energy_gwh",
                "contribution_percent",
            ]
        ].to_string(index=False)  # .tolist() 是给“一列”用的，把它变成 Python 列表；.to_string() 是给“整个表格”用的，把它变成可打印的文本。
    )

    print("Monthly energy data loaded:")
    print(monthly_data.to_string(index=False))

    print("Monthly energy plot data:")
    print(
        monthly_plot_data[
            [
                "month_label",
                "cooling_gwh",
                "heating_gwh",
            ]
        ].to_string(index=False)
    )

    save_energy_contribution_chart(
        plot_data=plot_data,
        output_path=DEFAULT_OUTPUT,
    )

    print(
        f"Energy contribution chart saved to: {DEFAULT_OUTPUT}"
    )

    print(
        f"Monthly energy chart saved to: {MONTHLY_OUTPUT}"
    )

if __name__ == "__main__":
    main()

