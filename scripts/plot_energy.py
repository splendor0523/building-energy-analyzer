from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "output" / "energy_contribution.csv"
DEFAULT_OUTPUT = BASE_DIR / "output" / "energy_contribution.png"

REQUIRED_COLUMNS = [
    "component",
    "annual_energy_kwh",
    "contribution_percent",
]

COMPONENT_LABELS = {
    "people": "People",
    "lighting": "Lighting",
    "equipment": "Equipment",
    "solar_transmission": "Solar transmission",
}

# ------ 读取csv源数据，并安全行检查 ------
def load_energy_contribution(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileExistsError(
            f"Energy contribution file not found: {input_path}"
        )

    contribution_data = pd.read_csv(input_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in contribution_data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in energy contribution file: "
            + ",".join(missing_columns) 
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
    contribution_data = load_energy_contribution(DEFAULT_INPUT)
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
    save_energy_contribution_chart(
        plot_data=plot_data,
        output_path=DEFAULT_OUTPUT,
    )

    print(
        f"Energy contribution chart saved to: {DEFAULT_OUTPUT}"
    )

if __name__ == "__main__":
    main()

