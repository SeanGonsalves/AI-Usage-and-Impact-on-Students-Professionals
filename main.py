"""Run the AI usage analysis and generate its reports."""

import argparse
from pathlib import Path

from src.analysis import analyze_data
from src.config import (
    DEFAULT_INPUT,
    PLOT_ROOT,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    TABLE_ROOT,
    TABLE_DIRS,
    create_directories,
)
from src.data import load_and_clean
from src.report_generator import generate_reports
from src.visualization import create_plots


def run_analysis(input_path: Path) -> dict:
    create_directories()
    for folder, pattern in ((PLOT_ROOT, "*.png"), (TABLE_ROOT, "*.csv")):
        for old_file in folder.rglob(pattern):
            old_file.unlink()

    cleaned, quality, raw_rows, duplicate_rows = load_and_clean(input_path)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_DATA_DIR / "cleaned_dataset.csv", index=False)
    quality.to_csv(PROCESSED_DATA_DIR / "data_quality_summary.csv", index=False)

    results = analyze_data(cleaned, quality, raw_rows, duplicate_rows)
    plots = create_plots(cleaned, results["correlation"])
    table_files = {
        "descriptive_statistics.csv": ("descriptive_statistics", "descriptive"),
        "category_frequencies.csv": ("descriptive_statistics", "categories"),
        "group_comparisons.csv": ("comparisons", "comparisons"),
        "purpose_by_user_type.csv": ("comparisons", "purpose_comparison"),
        "ai_use_time_saved_association.csv": ("comparisons", "correlation"),
    }
    tables = []
    for filename, (folder, key) in table_files.items():
        frame = results[key]
        if frame.empty:
            continue
        path = TABLE_DIRS[folder] / filename
        frame.to_csv(path, index=False)
        tables.append(path)

    reports = generate_reports(results, plots, input_path.name)
    return {
        "source_rows": raw_rows,
        "analysis_rows": len(cleaned),
        "columns": len(cleaned.columns),
        "plots": plots,
        "tables": tables,
        "reports": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path")
    args = parser.parse_args()
    try:
        result = run_analysis(args.input.expanduser().resolve())
    except (FileNotFoundError, ValueError, OSError) as error:
        parser.error(str(error))

    print(
        f"Analysis complete: {result['source_rows']} source rows, "
        f"{result['analysis_rows']} analyzed rows, {result['columns']} columns."
    )
    print(f"Generated {len(result['plots'])} plots and {len(result['tables'])} tables.")
    for report in result["reports"].values():
        print(f"Report: {report.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
