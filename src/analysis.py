"""Descriptive analysis and focused student/professional comparisons."""

import numpy as np
import pandas as pd
from scipy import stats

GROUP_OUTCOMES = (
    "AI_Usage_Hours_Per_Day",
    "Time_Saved_Hours_Per_Week",
    "Productivity_Score",
    "Satisfaction_Score",
)


def _adjust_p_values(values: list[float]) -> list[float]:
    """Apply the Benjamini–Hochberg correction to a small test family."""
    order = np.argsort(values)
    adjusted = np.empty(len(values), dtype=float)
    running_minimum = 1.0
    for index in range(len(values) - 1, -1, -1):
        source_index = order[index]
        running_minimum = min(
            running_minimum,
            values[source_index] * len(values) / (index + 1),
        )
        adjusted[source_index] = running_minimum
    return adjusted.tolist()


def analyze_data(
    cleaned: pd.DataFrame,
    quality: pd.DataFrame,
    source_rows: int,
    duplicate_rows: int,
) -> dict[str, pd.DataFrame | list[str]]:
    """Create concise summaries, selected comparisons, and evidence-based findings."""
    numeric = cleaned.select_dtypes(include="number").columns.tolist()
    descriptive = (
        cleaned[numeric].describe().T.reset_index(names="variable")
        if numeric else pd.DataFrame()
    )

    category_tables = []
    for column in ("User_Type", "AI_Purpose", "AI_Tool", "Would_Recommend"):
        if column in cleaned:
            counts = cleaned[column].value_counts(dropna=True)
            if not counts.empty:
                category_tables.append(
                    pd.DataFrame(
                        {
                            "variable": column,
                            "category": counts.index,
                            "count": counts.values,
                            "percent": (100 * counts / counts.sum()).round(1).values,
                        }
                    )
                )
    categories = (
        pd.concat(category_tables, ignore_index=True)
        if category_tables else pd.DataFrame(
            columns=["variable", "category", "count", "percent"]
        )
    )

    group_comparisons = []
    purpose_comparison = pd.DataFrame()
    if "User_Type" in cleaned:
        groups = cleaned["User_Type"].dropna().unique()
        if {"Student", "Professional"}.issubset(set(groups)):
            student = cleaned.loc[cleaned["User_Type"].eq("Student")]
            professional = cleaned.loc[cleaned["User_Type"].eq("Professional")]
            for variable in GROUP_OUTCOMES:
                if variable not in cleaned:
                    continue
                x = student[variable].dropna().to_numpy(dtype=float)
                y = professional[variable].dropna().to_numpy(dtype=float)
                if not len(x) or not len(y):
                    continue
                p_value = (
                    float(stats.mannwhitneyu(x, y, alternative="two-sided").pvalue)
                    if len(x) >= 2 and len(y) >= 2 else np.nan
                )
                group_comparisons.append(
                    {
                        "measure": variable,
                        "student_n": len(x),
                        "professional_n": len(y),
                        "student_median": float(np.median(x)),
                        "professional_median": float(np.median(y)),
                        "p_value": p_value,
                    }
                )
            if "AI_Purpose" in cleaned:
                purpose_comparison = (
                    pd.crosstab(cleaned["AI_Purpose"], cleaned["User_Type"], normalize="columns")
                    .mul(100)
                    .round(1)
                    .reset_index()
                )
    comparisons = pd.DataFrame(group_comparisons)
    if not comparisons.empty:
        tested = comparisons["p_value"].notna()
        comparisons["adjusted_p_value"] = np.nan
        if tested.any():
            comparisons.loc[tested, "adjusted_p_value"] = _adjust_p_values(
                comparisons.loc[tested, "p_value"].tolist()
            )

    correlation = pd.DataFrame()
    x_column, y_column = "AI_Usage_Hours_Per_Day", "Time_Saved_Hours_Per_Week"
    if x_column in cleaned and y_column in cleaned:
        pair = cleaned[[x_column, y_column]].dropna()
        if len(pair) >= 3 and pair[x_column].nunique() > 1 and pair[y_column].nunique() > 1:
            rho, p_value = stats.spearmanr(pair[x_column], pair[y_column])
            correlation = pd.DataFrame(
                [{
                    "measure_1": x_column,
                    "measure_2": y_column,
                    "n": len(pair),
                    "spearman_rho": float(rho),
                    "p_value": float(p_value),
                }]
            )

    summary = pd.DataFrame(
        [
            {"measure": "Source records", "value": source_rows},
            {"measure": "Records analyzed", "value": len(cleaned)},
            {"measure": "Columns", "value": len(cleaned.columns)},
            {"measure": "Exact duplicate rows excluded", "value": duplicate_rows},
        ]
    )
    findings = _build_findings(cleaned, categories, comparisons, correlation, quality)
    return {
        "summary": summary,
        "quality": quality,
        "descriptive": descriptive,
        "categories": categories,
        "comparisons": comparisons,
        "purpose_comparison": purpose_comparison,
        "correlation": correlation,
        "findings": findings,
    }


def _build_findings(
    cleaned: pd.DataFrame,
    categories: pd.DataFrame,
    comparisons: pd.DataFrame,
    correlation: pd.DataFrame,
    quality: pd.DataFrame,
) -> list[str]:
    findings = []
    if "User_Type" in cleaned:
        counts = cleaned["User_Type"].value_counts()
        if not counts.empty:
            total = int(counts.sum())
            largest = counts.index[0]
            finding = (
                f"{largest} make up {counts.iloc[0] / total:.1%} of records "
                f"with a reported user type."
            )
            if {"Student", "Professional"}.issubset(set(counts.index)):
                gap = abs(counts["Student"] - counts["Professional"]) / total
                finding += (
                    " The groups are represented at similar rates."
                    if gap <= 0.10
                    else " The group counts are uneven."
                )
            findings.append(finding)

    if not categories.empty:
        purposes = categories.loc[categories["variable"].eq("AI_Purpose")]
        if not purposes.empty:
            top = purposes.iloc[0]
            findings.append(
                f"{top['category']} is the most common reported AI purpose "
                f"({int(top['count'])} responses; {top['percent']:.1f}% of non-missing responses)."
            )
    usage = "AI_Usage_Hours_Per_Day"
    if usage in cleaned and cleaned[usage].notna().any():
        findings.append(
            f"Daily AI use has a median of {cleaned[usage].median():.1f} hours "
            f"({int(cleaned[usage].notna().sum())} complete responses)."
        )
    if not comparisons.empty:
        significant = comparisons.loc[comparisons["adjusted_p_value"].lt(0.05)]
        if significant.empty:
            findings.append(
                "No selected student–professional outcome comparison remained "
                "statistically significant after adjustment; this does not prove "
                "the groups are equivalent."
            )
        for _, row in significant.head(2).iterrows():
            findings.append(
                f"{row['measure']} differs between groups in this sample "
                f"(median: students {row['student_median']:.1f}, professionals "
                f"{row['professional_median']:.1f}; adjusted p="
                f"{row['adjusted_p_value']:.2g}). This is not an AI-caused effect."
            )
    if not correlation.empty:
        row = correlation.iloc[0]
        findings.append(
            f"Daily AI-use hours and reported weekly time saved are associated "
            f"(Spearman ρ={row['spearman_rho']:.2f}, n={int(row['n'])}); "
            "this association does not establish causation."
        )
    if not quality.empty:
        highest = quality.sort_values("missing_percent", ascending=False).iloc[0]
        if highest["missing_count"]:
            findings.append(
                f"{highest['column']} has the most missing data "
                f"({highest['missing_percent']:.1f}%)."
            )
    return findings
