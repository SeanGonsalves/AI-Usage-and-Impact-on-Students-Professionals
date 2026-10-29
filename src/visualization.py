"""Create a small set of plots for the variables available in the dataset."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import PLOT_DIRS

PLOT_METRICS = (
    "AI_Usage_Hours_Per_Day",
    "Time_Saved_Hours_Per_Week",
    "Productivity_Score",
    "Satisfaction_Score",
)


def _save(figure: plt.Figure, folder: str, filename: str) -> Path:
    path = PLOT_DIRS[folder] / filename
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return path


def create_plots(
    cleaned: pd.DataFrame,
    correlation: pd.DataFrame,
) -> list[Path]:
    """Save informative distributions, group comparison, and one association plot."""
    plots = []
    numeric = [name for name in PLOT_METRICS if name in cleaned]
    for column in numeric:
        values = cleaned[column].dropna()
        if values.empty:
            continue
        figure, axis = plt.subplots(figsize=(6, 4))
        axis.hist(values, bins="auto", color="#2878B5", edgecolor="white")
        axis.set(
            title=column.replace("_", " "),
            xlabel=column.replace("_", " "),
            ylabel="Responses",
        )
        plots.append(
            _save(
                figure,
                "distributions",
                f"{column.casefold()}_distribution.png",
            )
        )

    if "AI_Purpose" in cleaned:
        counts = cleaned["AI_Purpose"].value_counts().sort_values()
        if not counts.empty:
            figure, axis = plt.subplots(figsize=(7, 4.5))
            counts.plot.barh(ax=axis, color="#4C9F70")
            axis.set(title="Reported AI purpose", xlabel="Responses", ylabel="")
            plots.append(_save(figure, "other_analysis", "ai_purpose_frequency.png"))

    valid_groups = {"Student", "Professional"}
    has_groups = (
        "User_Type" in cleaned
        and valid_groups.issubset(set(cleaned["User_Type"].dropna()))
    )
    group_metrics = [
        column for column in numeric
        if has_groups
        and cleaned.groupby("User_Type")[column].count().reindex(valid_groups).gt(0).all()
    ]
    if group_metrics:
        figure, axes = plt.subplots(
            2, 2, figsize=(9, 6), squeeze=False
        )
        for axis, column in zip(axes.flat, group_metrics):
            values = [
                cleaned.loc[cleaned["User_Type"].eq(group), column].dropna()
                for group in ("Student", "Professional")
            ]
            labels = [
                group for group, group_values in zip(
                    ("Student", "Professional"), values
                )
                if not group_values.empty
            ]
            values = [group_values for group_values in values if not group_values.empty]
            if len(values) < 2:
                axis.set_visible(False)
                continue
            boxes = axis.boxplot(
                values,
                tick_labels=labels,
                patch_artist=True,
                orientation="vertical",
            )
            for box, color in zip(boxes["boxes"], ("#2878B5", "#E08B35")):
                box.set_facecolor(color)
            axis.set_title(column.replace("_", " "))
        for axis in axes.flat[len(group_metrics):]:
            axis.set_visible(False)
        plots.append(
            _save(figure, "comparisons", "key_measures_by_user_type.png")
        )

    if not correlation.empty:
        row = correlation.iloc[0]
        x_name, y_name = row["measure_1"], row["measure_2"]
        pair = cleaned[[x_name, y_name]].dropna()
        if not pair.empty:
            figure, axis = plt.subplots(figsize=(6, 4))
            axis.scatter(
                pair[x_name], pair[y_name], color="#2878B5", alpha=0.65, s=24
            )
            axis.set(
                title=f"AI use and time saved (Spearman ρ={row['spearman_rho']:.2f})",
                xlabel="AI usage (hours/day)",
                ylabel="Time saved (hours/week)",
            )
            plots.append(
                _save(
                    figure,
                    "correlations",
                    "ai_usage_and_time_saved.png",
                )
            )
    return plots
