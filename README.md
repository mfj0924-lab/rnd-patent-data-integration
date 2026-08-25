# 上市公司研发投入与专利数据整合

商务智能课程个人项目：自动识别多年份专利表的两类表头格式，清洗股票代码和年份，
再按“证券代码 + 年份”把专利数据左连接到上市公司研发投入主表。

## 项目结果

- 处理 2010—2021 年的多年份专利文件。
- 原课程任务处理 48,468 条专利记录，成功匹配 21,605 条研发记录。
- 输出可用于研发投入、专利产出及滞后效应分析的统一数据集。

## 目录

```text
src/                 可复用的数据整合脚本
sample_data/         不含真实公司的合成小样本
data/raw/            本机原始数据，默认不提交
data/output/         生成结果，默认不提交
```

## 快速复现

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\src\merge_patent_data.py `
  --rd-file .\sample_data\rd_investment.csv `
  --patent-dir .\sample_data\patents `
  --output .\sample_data\merged_demo.csv
```

## 数据与隐私边界

真实 Excel、课程报告、姓名、学号和 Office 元数据不进入公开仓库。由于原始数据的再分发
授权尚未确认，公开版本只提供处理代码、字段说明和合成小样本。项目使用 Trae 辅助代码生产，
本人负责合并口径、异常格式判断、结果核验和最终交付。
