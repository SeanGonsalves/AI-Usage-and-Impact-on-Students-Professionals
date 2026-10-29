"""Load and clean the source CSV without changing it."""

from pathlib import Path

import pandas as pd

from src.config import NUMERIC_COLUMNS

ALIASES = {
    "Gender": {
        "m": "Male",
        "male": "Male",
        "f": "Female",
        "female": "Female",
        "other": "Other",
    },
    "User_Type": {"student": "Student", "professional": "Professional"},
    "Would_Recommend": {"yes": "Yes", "no": "No", "maybe": "Maybe"},
    "Education_Level": {
        "bachelor's": "Bachelor's",
        "bachelors": "Bachelor's",
        "bachelor's degree": "Bachelor's",
        "ba/bsc": "Bachelor's",
        "undergrad": "Undergraduate",
        "undergraduate": "Undergraduate",
        "master's": "Master's",
        "masters": "Master's",
        "master's degree": "Master's",
        "ma/msc": "Master's",
        "ph.d.": "PhD",
        "phd": "PhD",
        "hs": "High School",
        "high school": "High School",
    },
    "AI_Tool": {
        "chatgpt": "ChatGPT",
        "chat gpt": "ChatGPT",
        "google gemini": "Google Gemini",
        "gemini": "Google Gemini",
        "microsoft copilot": "Microsoft Copilot",
        "copilot": "Microsoft Copilot",
        "claude": "Claude",
        "perplexity ai": "Perplexity AI",
    },
    "Country": {
        "u.k.": "United Kingdom",
        "uk": "United Kingdom",
        "united states of america": "United States",
    },
}


def load_and_clean(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, int, int]:
    """Load a CSV, normalize supported values, and report data quality."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Put it in data/raw/ or pass --input."
        )

    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    raw.columns = [str(column).strip() for column in raw.columns]
    if raw.empty or not len(raw.columns):
        raise ValueError(f"Dataset has no records or columns: {path}")
    if raw.columns.duplicated().any():
        raise ValueError("Dataset contains duplicate column names.")

    duplicate_count = int(raw.duplicated().sum())
    cleaned = raw.loc[~raw.duplicated(keep="first")].copy()
    for column in cleaned.columns:
        cleaned[column] = cleaned[column].str.replace(r"\s+", " ", regex=True).str.strip()
        if column in ALIASES:
            cleaned[column] = cleaned[column].map(
                lambda value: ALIASES[column].get(value.casefold(), value)
            )
        elif column == "Country":
            cleaned[column] = cleaned[column].map(
                lambda value: ALIASES["Country"].get(value.casefold(), value.title())
            )
    cleaned = cleaned.replace("", pd.NA)

    parse_errors: dict[str, int] = {}
    out_of_range: dict[str, int] = {}
    for column, (minimum, maximum) in NUMERIC_COLUMNS.items():
        if column not in cleaned:
            continue
        text = cleaned[column].astype("string")
        numeric_text = text.str.replace(",", "", regex=False)
        numeric_text = numeric_text.str.replace(
            r"(?i)\s*(hrs?|hours?|years?|yrs?)\s*$", "", regex=True
        ).str.replace(r"[$€£]", "", regex=True).str.strip()
        parsed = pd.to_numeric(numeric_text, errors="coerce")
        invalid = pd.Series(False, index=cleaned.index)
        if minimum is not None:
            invalid |= parsed.notna() & parsed.lt(minimum)
        if maximum is not None:
            invalid |= parsed.notna() & parsed.gt(maximum)
        parse_errors[column] = int(
            (text.notna() & numeric_text.ne("") & parsed.isna()).sum()
        )
        out_of_range[column] = int(invalid.sum())
        cleaned[column] = parsed.mask(invalid)

    quality_rows = []
    for column in raw.columns:
        quality_rows.append(
            {
                "column": column,
                "missing_count": int(cleaned[column].isna().sum()),
                "missing_percent": round(100 * cleaned[column].isna().mean(), 2),
                "unique_values": int(cleaned[column].nunique(dropna=True)),
                "numeric_parse_errors": parse_errors.get(column, 0),
                "out_of_range_values": out_of_range.get(column, 0),
            }
        )
    return cleaned, pd.DataFrame(quality_rows), len(raw), duplicate_count
