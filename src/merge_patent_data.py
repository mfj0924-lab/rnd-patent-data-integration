"""Merge R&D investment records with annual patent files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


def normalize_stock_code(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\.[A-Za-z]+$", "", regex=True)
        .str.zfill(6)
    )


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype="string")
    return pd.read_excel(path, dtype="string")


def normalize_header(frame: pd.DataFrame, required_column: str) -> pd.DataFrame:
    if required_column in frame.columns:
        return frame.copy()
    if frame.empty:
        raise ValueError(f"表格为空，无法识别字段：{required_column}")
    candidate = [str(value).strip() for value in frame.iloc[0].tolist()]
    if required_column not in candidate:
        raise ValueError(f"无法识别字段：{required_column}")
    normalized = frame.iloc[1:].copy()
    normalized.columns = candidate
    return normalized.reset_index(drop=True)


def year_from_filename(path: Path) -> int:
    match = re.search(r"(20\d{2})", path.stem)
    if not match:
        raise ValueError(f"文件名中缺少年份：{path.name}")
    return int(match.group(1))


def merge_data(rd_file: Path, patent_dir: Path) -> pd.DataFrame:
    rd = normalize_header(read_table(rd_file), "证券代码")
    if "统计截止日期" not in rd.columns:
        raise ValueError("研发投入表缺少‘统计截止日期’字段")
    rd["年份"] = pd.to_datetime(rd["统计截止日期"], errors="raise").dt.year
    rd["证券代码"] = normalize_stock_code(rd["证券代码"])

    patent_frames: list[pd.DataFrame] = []
    files = sorted([*patent_dir.glob("*.xlsx"), *patent_dir.glob("*.csv")])
    if not files:
        raise FileNotFoundError(f"专利目录中没有 CSV/XLSX：{patent_dir}")
    for path in files:
        frame = normalize_header(read_table(path), "股票代码")
        frame["年份"] = year_from_filename(path)
        frame["股票代码"] = normalize_stock_code(frame["股票代码"])
        patent_frames.append(frame)

    patents = pd.concat(patent_frames, ignore_index=True)
    return rd.merge(
        patents,
        left_on=["证券代码", "年份"],
        right_on=["股票代码", "年份"],
        how="left",
        validate="many_to_many",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rd-file", type=Path, required=True)
    parser.add_argument("--patent-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    merged = merge_data(args.rd_file, args.patent_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".csv":
        merged.to_csv(args.output, index=False, encoding="utf-8-sig")
    else:
        merged.to_excel(args.output, index=False)
    matched = int(merged["股票代码"].notna().sum())
    print(f"总记录数：{len(merged):,}")
    print(f"成功匹配：{matched:,}")
    print(f"输出文件：{args.output}")


if __name__ == "__main__":
    main()
