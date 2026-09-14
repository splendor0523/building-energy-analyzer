# Building Energy Result Analyzer - Resume Project Description

## 1. 中文简历正式版

### Building Energy Result Analyzer｜建筑能耗模拟结果分析与可视化工具

**技术栈：Python / pandas / openpyxl / matplotlib / Streamlit / Docker / Git / EnergyPlus**

- 基于真实 EnergyPlus / Honeybee / Grasshopper 模拟结果，开发建筑能耗数据分析与可视化工具，处理包含 200 万级结果记录的 EnergyPlus SQL 转写数据。
- 基于 `ReportData`、`ReportDataDictionary`、`Time` 等 EnergyPlus 数据表建立变量索引与时间映射，完成关键变量筛选、逐时数据提取及异常 TimeIndex 定位与修复。
- 实现年度冷热需求、峰值负荷及时间区间、热增益组成、月度冷热需求和峰值日 24 小时曲线等指标计算，并对年度与月度结果进行一致性校验。
- 将数据分析、绘图与展示逻辑拆分为独立模块，使用 matplotlib 自动生成分析图表，并通过 Streamlit 构建交互式 Dashboard。
- 使用 Docker 对 Dashboard 进行容器化，实现项目依赖、运行环境与应用的一体化部署，并使用 Git / GitHub 管理项目版本和文档。

---

## 2. 中文简历精简版

### Building Energy Result Analyzer｜建筑能耗数据分析工具

**Python / pandas / Streamlit / Docker / EnergyPlus**

- 面向真实 EnergyPlus 模拟数据开发分析工具，处理 200 万级结果记录，完成关键变量提取、时间序列重建及数据异常检查。
- 实现年度/月度冷热需求、峰值负荷、热增益组成及峰值日逐时分析，并使用 matplotlib 与 Streamlit 完成结果可视化。
- 按数据处理、绘图和 UI 展示进行模块化设计，并使用 Docker 完成 Dashboard 容器化部署。

---

## 3. 数据分析岗位版本

### Building Energy Result Analyzer｜建筑能耗数据分析项目

**Python / pandas / Data Cleaning / Data Visualization / Streamlit / Docker**

- 对 200 万级 EnergyPlus 模拟结果进行数据抽取、清洗和结构化处理，通过字典索引关联变量定义与逐时结果。
- 对缺失时间索引进行源数据定位和修复，重建完整 8760 小时时间序列，并建立数据完整性检查流程。
- 使用 pandas 完成年度、月度、峰值日等多时间尺度聚合分析，并通过结果回算验证统计结果一致性。
- 将分析结果输出为结构化 CSV 和可视化图表，并开发 Streamlit Dashboard 支持结果浏览和交互分析。
- 使用 Docker 封装运行环境，使用 Git / GitHub 完成版本管理和项目展示。

---

## 4. Python / AI 工具方向版本

### Building Energy Result Analyzer｜Python 数据分析与工具化项目

**Python / pandas / Streamlit / Docker / Git**

- 将建筑模拟中的大型原始结果数据封装为可重复运行的 Python 分析流程，实现数据读取、清洗、校验、统计、可视化和 Dashboard 展示。
- 设计数据分析、图表生成和前端展示之间的模块边界，避免业务逻辑在 Streamlit 页面中重复实现。
- 对 200 万级数据进行关键变量筛选和逐时数据提取，降低后续分析的数据规模和复杂度。
- 使用 Streamlit 将分析脚本包装为可使用的 Web 工具，并通过 Docker 实现跨环境部署。
- 为后续方案对比、自动报告生成、CLI 和 AI 辅助分析预留结构化分析接口。

---

# 5. 面试讲述版

这个项目来源于我本身的建筑环境模拟工作。

EnergyPlus 最终会产生非常大量的模拟结果。我手里的真实数据是从 EnergyPlus SQL 转写出来的 Excel，里面有多个结果表，核心的三个 ReportData 表加起来有两百多万条记录，所以直接人工查看基本没有办法使用。

我首先研究了 EnergyPlus 的数据结构。它不是简单的一张表，而是 ReportData、ReportDataDictionary 和 Time 之间通过索引关联。

所以我写了 Python 脚本，根据 DictionaryIndex 找到需要的冷负荷、热负荷、人员、照明、设备和太阳得热等变量，再从两百多万条结果中抽取真正需要的数据。

处理中还遇到过一个比较真实的数据问题，就是 Time 表里缺失了一个 TimeIndex，但是 ReportData 里对应结果仍然存在。

我没有直接把缺失值跳过去，而是先检查前后时间，确认缺失的是 2006 年 7 月 28 日 09:00，然后修复这个时间索引，最后重新构建完整的 8760 小时时间序列。

在数据处理完成以后，我继续做了年度冷热需求、峰值时间、热增益组成、月度冷热需求和峰值日 24 小时曲线等分析，同时通过年度结果和月度求和结果进行一致性校验。

工程结构上，我没有把所有代码都写在一个文件里。

`analyze_energy.py` 负责原始数据读取、清洗和指标计算；

`plot_energy.py` 负责读取分析结果并生成图表；

`app.py` 只负责 Streamlit 页面展示和交互。

最后我把这些结果做成了 Streamlit Dashboard，并使用 Docker 把整个运行环境容器化。

这个项目对我最大的价值不是单独学会某一个 pandas 方法，而是第一次比较完整地把真实领域数据从原始数据处理，一直做到分析结果、可视化、Web 工具和部署。

---

# 6. 面试追问要点

## 为什么不直接用 Excel 分析？

原始数据超过两百万条记录，并且 EnergyPlus 的变量定义、时间和结果分别存在不同数据表中，需要通过索引关系进行关联。

Python 更适合完成批量提取、数据校验、重复分析和自动输出。

## 项目中比较难的问题是什么？

一个比较典型的问题是原始 Time 表缺失一个 TimeIndex，而 ReportData 中仍然存在对应结果。

我先检查缺失索引前后的时间关系，确认真实缺失时刻，再显式修复，而不是直接删除异常数据。

这个过程让我开始形成“先定位数据源问题，再决定修复策略”的数据处理习惯。

## 为什么使用 Streamlit？

前面的分析脚本已经能够产生 CSV 和 PNG，但这些结果仍然比较分散。

Streamlit 可以在不重写分析逻辑的情况下，把现有结果快速包装成可以浏览和交互的工具，因此我让 app.py 只负责 UI，继续复用原来的分析结果。

## 为什么使用 Docker？

本地项目依赖 Python、pandas、Streamlit、matplotlib 等多个包。

Docker 可以把代码和依赖环境一起封装，降低不同电脑和 Python 环境导致的运行差异，同时让我学习一个更接近真实软件项目的部署流程。

## 这个项目下一步会做什么？

当前版本主要完成单个 EnergyPlus 工况的数据分析。

下一阶段计划加入 baseline、固定遮阳、动态遮阳等多个工况之间的自动对比，包括年度能耗变化、峰值变化和太阳得热变化。

在结构化指标稳定后，再增加自动 Markdown 报告和 AI 辅助分析，而不是直接让大模型读取几百万条原始数据。