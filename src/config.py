"""Shared project paths and analysis settings."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
PLOT_ROOT = OUTPUT_DIR / "plots"
TABLE_ROOT = OUTPUT_DIR / "tables"
PLOT_DIRS = {
    "distributions": PLOT_ROOT / "distributions",
    "comparisons": PLOT_ROOT / "comparisons",
    "correlations": PLOT_ROOT / "correlations",
    "other_analysis": PLOT_ROOT / "other_analysis",
}
TABLE_DIRS = {
    "descriptive_statistics": TABLE_ROOT / "descriptive_statistics",
    "comparisons": TABLE_ROOT / "comparisons",
}
REPORT_DIRS = {
    "excel": OUTPUT_DIR / "reports" / "excel",
    "markdown": OUTPUT_DIR / "reports" / "markdown",
    "pdf": OUTPUT_DIR / "reports" / "pdf",
}
DEFAULT_INPUT = RAW_DATA_DIR / "AI_Usage_and_Impact_on_Students_and_Professionals.csv"
NUMERIC_COLUMNS = {
    "Age": (None, None),
    "Monthly_Income": (0, None),
    "AI_Usage_Hours_Per_Day": (0, 24),
    "Monthly_AI_Cost": (0, None),
    "Productivity_Score": (0, 10),
    "Accuracy_Rating": (1, 5),
    "Satisfaction_Score": (1, 10),
    "Time_Saved_Hours_Per_Week": (0, None),
    "Work_or_Study_Hours_Per_Day": (0, 24),
}


def create_directories() -> None:
    """Create all project output and data directories."""
    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        *PLOT_DIRS.values(),
        *TABLE_DIRS.values(),
        *REPORT_DIRS.values(),
    ):
        path.mkdir(parents=True, exist_ok=True)
