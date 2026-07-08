from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data" / "run_sql_export.xlsx"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"

REQUIRED_SHEETS = [
    "ReportDataDictionary",
    "Time",
]

REPORT_DATA_SHEETS = [
    "ReportData_1",
    "ReportData_2",
    "ReportData_3",
]

KEY_VALUABLE_NAMES = [
    "Zone Ideal Loads Supply Air Total Cooling Energy",
    "Zone Ideal Loads Supply Air Total Heating Energy",
    "Zone Ideal Loads Zone Total Cooling Energy",
    "Zone Ideal Loads Zone Total Heating Energy",
    "Enclosure Windows Total Transmitted Solar Radiation Energy",
    "Zone Lights Total Heating Energy",
    "Zone Electric Equipment Total Heating Energy",
    "Zone People Total Heating Energy",
    "Zone Mean Air Temperature",
    "Zone Operative Temperature",
    "Zone Air Relative Humidity",
    "Surface Window Heat Gain Energy",
    "Surface Window Heat Loss Energy",
    "Surface Inside Face Temperature",
    "Surface Outside Face Temperature",
]

def parse_arg() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect Energyplus SQL exported Excel workbook"
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Input Excel file path",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output folder path",
    )
    return(parser.parse_args())

def resolve_path(path_text:str) -> Path:  # 变绝对路径
    path = Path(path_text)

    if not path.is_absolute():
        path = BASE_DIR / path
    
    return(path)

def read_sheet_as_dataframe(workbook,sheet_name:str) -> pd.DataFrame: # 将sheet页变成dataframe
    if sheet_name not in workbook.sheetnames:
        raise ValueError(f"Sheet not found:{sheet_name}")
    worksheet = workbook[sheet_name]
    rows = list(worksheet.iter_rows(values_only=True))

    if not rows:
        return(pd.DataFrame())
    
    header = list(rows[0])
    data = [list(row) for row in rows[1:]]

    return pd.DataFrame(data,columns=header)

def validate_sheets(sheet_names:list[str]) ->list[str]: # 看是否有缺的必须sheet页
    required = REQUIRED_SHEETS + REPORT_DATA_SHEETS
    missing = [sheet for sheet in required if sheet not in sheet_names]
    return missing

def find_key_variables(dictionary_df:pd.Dataframe) -> pd.DataFrame: #筛选关键指标的数据，剔除其他
    required_columns = [
         "ReportDataDictionaryIndex",
        "KeyValue",
        "Name",
        "Units",
        "ReportingFrequency",
    ]
    missing_columns = [
        column for column in required_columns if column not in dictionary_df
    ]
    if missing_columns:
        raise ValueError(
            "Missing columns in ReportDataDictionary:"
            +",".join(missing_columns)
        )
    key_variables = dictionary_df[
        dictionary_df["Name"].astype(str).isin(KEY_VALUABLE_NAMES)
    ].copy()

    key_variables = key_variables[required_columns]
    key_variables = key_variables.sort_values(
        by=["Name","KeyValue"],
        ignore_index =True  #抛弃原来的索引
    )
    return key_variables

def get_key_variable_indices(key_variables:pd.DataFrame) ->set[int]: # 找关键数据的index
    indices = pd.to_numeric(
        key_variables["ReportDataDictionaryIndex"],
        errors="coerce"  #讲错误数据改为Nan
    )
    indices = indices.dropna().astype(int)
    return set(indices)

def extract_selected_report_data_from_sheet(   # 将关键数据单独抽出一个dataframe
        workbook,
        sheet_name:str,
        key_variable_indices:set[int]
) -> pd.DataFrame:
    worksheet = workbook[sheet_name]
    rows = worksheet.iter_rows(values_only=True) # 获得sheet页中的所有行
    header = next(rows) #将第一行做为表头

    column_index = {
        column_name:index
        for index,column_name in enumerate(header)
    }    #制作“一、列名与index对应字典”

    required_columns = [
        "ReportDataIndex",
        "TimeIndex",
        "ReportDataDictionaryIndex",
        "Value",
    ]
    selected_rows =[]

    for row in rows:
        dictionary_index = row[column_index["ReportDataDictionaryIndex"]] # 根据“一、列名与index对应字典”找到数值标签这一整列

        if dictionary_index in key_variable_indices:
            selected_rows.append(
                {
                    column:row[column_index[column]]
                    for column in required_columns
                }
            )
    return(pd.DataFrame(selected_rows,columns=required_columns))

# ------ 给简单数据报告表加上更多的信息 ------

def attach_variable_info(
        report_data:pd.DataFrame,
        key_variables:pd.DataFrame,
) -> pd.DataFrame:
    variable_info = key_variables[
        [
            "ReportDataDictionaryIndex",
            "KeyValue",
            "Name",
            "Units",
        ]
    ].copy()

    merged_data = report_data.merge(
        variable_info,
        on="ReportDataDictionaryIndex", # 以哪一列为对照，这一列相同的俩个表的数据会放在同一行
        how="left", # 左边表格的行全部保留，右边表格只负责贴信息，贴不上的就空着。
    )
    
    return(merged_data)

def find_missing_time_indices(time_df:pd.DataFrame) -> list[int]:
    if "TimeIndex" not in time_df.columns:
        return []
    
    time_indices = pd.to_numeric(time_df["TimeIndex"],errors="coerce")
    time_indices = time_indices.dropna().astype(int)

    if time_indices.empty:
        return []
    
    start = int(time_indices.min())
    end = int(time_indices.max())

    expected = set(range(start,end + 1))
    actual = set(time_indices)
    return sorted(expected - actual)

def build_overview_text(
    input_path: Path,
    sheet_names: list[str],
    dictionary_df: pd.DataFrame,
    time_df: pd.DataFrame,
    key_variables: pd.DataFrame,
    missing_sheets: list[str],
    missing_time_indices: list[int],
) -> str:
    lines = []

    lines.append("Building Energy Result Analyzer - Workbook Overview")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Input file: {input_path}")
    lines.append(f"Total sheets: {len(sheet_names)}")
    lines.append("")
    lines.append("Sheets:")
    for sheet_name in sheet_names:
        lines.append(f"- {sheet_name}")

    lines.append("")
    lines.append("Required Sheet Check:")
    if missing_sheets:
        lines.append("Missing sheets:")
        for sheet_name in missing_sheets:
            lines.append(f"- {sheet_name}")
    else:
        lines.append("All required sheets were found.")

    lines.append("")
    lines.append("Main Tables:")
    lines.append(f"- ReportDataDictionary rows: {len(dictionary_df)}")
    lines.append(f"- Time rows: {len(time_df)}")
    lines.append(f"- Key variables found: {len(key_variables)}")

    lines.append("")
    lines.append("TimeIndex Check:")
    if missing_time_indices:
        preview = missing_time_indices[:20]
        lines.append(f"Missing TimeIndex values found: {preview}")
        if len(missing_time_indices) > 20:
            lines.append(f"... and {len(missing_time_indices) - 20} more")
    else:
        lines.append("No missing TimeIndex values found.")

    lines.append("")
    lines.append("Key Variables:")
    if key_variables.empty:
        lines.append("No key variables were found.")
    else:
        for _, row in key_variables.iterrows():
            lines.append(
                f"- {row['ReportDataDictionaryIndex']} | "
                f"{row['Name']} | "
                f"{row['KeyValue']} | "
                f"{row['Units']}"
            )

    lines.append("")

    return "\n".join(lines)

# ------ 主要运行阶段 ------

def main() -> None:
    args = parse_arg()

    input_path = resolve_path(args.input)
    output_dir = resolve_path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        print("Please put run_sql_export.xlsx into the data folder first.")
        sys.exit(1)

    output_dir.mkdir(parents=True,exist_ok=True)

    workbook = load_workbook(
        input_path,
        read_only=True,
        data_only=True,
    )
    
    sheet_names = workbook.sheetnames
    missing_sheets = validate_sheets(sheet_names)

    dictionary_df = read_sheet_as_dataframe(workbook, "ReportDataDictionary")
    time_df = read_sheet_as_dataframe(workbook, "Time")

# ------ 查找关键参数index ------
    key_variables = find_key_variables(dictionary_df)  
    key_variables_indices = get_key_variable_indices(key_variables)
    print(f"Key variable count:{len(key_variables_indices)}")

# ------ 将“指定sheet页”关键指标的数据抽出为dataframe ------
    selected_report_data_list = []
    for sheet_name in REPORT_DATA_SHEETS:
        selected_report_data = extract_selected_report_data_from_sheet(
            workbook=workbook,
            sheet_name=sheet_name,
            key_variable_indices=key_variables_indices
        )
        selected_report_data["SourceSheet"] = sheet_name
        print(f"Selected rows from {sheet_name}: {len(selected_report_data)}")

        selected_report_data_list.append(selected_report_data)
    
    selected_report_data =pd.concat(  # 将列表中的所有dataframe从上到下叠罗汉合并
        selected_report_data_list,
        ignore_index=True
    )

# ------ 将简单汇报表格加入值，名字，单位等信息 ------
    selected_report_data = attach_variable_info(
        report_data=selected_report_data,
        key_variables=key_variables,
    )

# ------ 把已经筛选并合并好变量名称的数据，保存成 CSV 文件 ------
    selected_report_data_path = output_dir / "selected_report_data.csv"
    selected_report_data.to_csv( selected_report_data_path,
    index=False,
    encoding="utf-8-sig",)
    print(f"Selected report data saved to: {selected_report_data_path}")
    print(f"Total selected rows: {len(selected_report_data)}")
# ------ 查找缺少的时间戳 ------

    missing_time_indices = find_missing_time_indices(time_df)

# ------ 撰写预览信息 ------
    overview_text = build_overview_text(
        input_path=input_path,
        sheet_names=sheet_names,
        dictionary_df=dictionary_df,
        time_df=time_df,
        key_variables=key_variables,
        missing_sheets=missing_sheets,
        missing_time_indices=missing_time_indices,
    )

    overview_path = output_dir / "workbook_overview.txt"
    key_variables_path = output_dir / "key_variables.csv"

    overview_path.write_text(overview_text, encoding="utf-8")
    key_variables.to_csv(key_variables_path, index=False, encoding="utf-8-sig")

    print("Workbook inspection finished.")
    print(f"Overview saved to: {overview_path}")
    print(f"Key variables saved to: {key_variables_path}")
    print(f"Total sheets: {len(sheet_names)}")
    print(f"Dictionary rows: {len(dictionary_df)}")
    print(f"Time rows: {len(time_df)}")
    print(f"Key variables found: {len(key_variables)}")


if __name__ == "__main__":
    main()