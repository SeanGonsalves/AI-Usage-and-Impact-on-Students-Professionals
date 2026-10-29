# AI Usage and Impact on Students and Professionals

> **A reproducible, descriptive look at how students and professionals report using AI.**
>
> This project explores reported AI tools, tasks, usage patterns, and perceived outcomes. The data is observational and self-reported, so the results describe associations—not cause and effect.

| Dataset | Analysis approach | Generated reports |
|---|---|---|
| 300 responses · 19 columns | Python · descriptive statistics · group comparisons | Markdown · Excel · PDF |

## What this project does

The analysis pipeline takes a CSV survey dataset and turns it into cleaned data, summary tables, plots, and reader-friendly reports. It:

- Standardizes supported numeric formats and category labels without overwriting the source CSV.
- Reports missing values and out-of-range values; it does not impute missing data.
- Excludes exact duplicate rows from analysis.
- Summarizes reported AI tools, purposes, usage, and perceived outcomes.
- Compares selected outcomes between students and professionals.
- Measures the association between daily AI-use hours and reported weekly time saved.

## Findings at a glance

The supplied dataset contains **300 source rows**. After excluding **12 exact duplicate rows**, **288 records** remain for analysis.

| Observation | Result |
|---|---:|
| Most common reported AI purpose | Coding — 65 of 275 responses (23.6%) |
| Median reported daily AI use | 2 hours |
| Daily AI use and weekly time saved | Spearman ρ = 0.82 (*n* = 271) |
| Student–professional outcome comparisons | None statistically significant after adjustment |

The association between AI use and time saved does **not** show that AI use caused respondents to save time. Likewise, a lack of statistically significant group differences does not prove that students and professionals are equivalent.

![Reported AI purposes](outputs/plots/other_analysis/ai_purpose_frequency.png)

## Reports and outputs

Run the project to generate these deliverables:

| Deliverable | What it contains |
|---|---|
| [Markdown report](outputs/reports/markdown/analysis_report.md) | Dataset quality, key findings, descriptive statistics, common responses, student–professional comparisons, the usage/time-saved association, selected plots, and limitations. |
| [Excel workbook](outputs/reports/excel/analysis_report.xlsx) | Separate sheets for the summary, data quality, descriptive statistics, categories, group comparisons, purpose by group, association, and key findings. |
| [PDF report](outputs/reports/pdf/analysis_report.pdf) | A portable, formatted summary of the analysis and selected charts. |
| Processed data | A cleaned CSV and data-quality summary in `data/processed/`. |
| Tables and plots | Analysis tables in `outputs/tables/` and charts in `outputs/plots/`. |

The plots are selected according to the columns available in the input data. They may include distributions, AI-purpose frequencies, student–professional comparisons, and the usage/time-saved relationship.

## Run it yourself

Requirements: **Python 3.10 or later**. Run these commands from the project root.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If `py` is unavailable, substitute `python` in the first command. You can run the virtual environment's Python directly as shown, without activating it.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

The default input is `data/raw/AI_Usage_and_Impact_on_Students_and_Professionals.csv`. To analyze another CSV, pass its path:

```bash
python main.py --input path/to/file.csv
```

Run the test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
.
├── data/
│   ├── raw/                         # Local input CSV (not tracked by Git)
│   └── processed/                   # Cleaned data and quality summary
├── outputs/
│   ├── plots/
│   │   ├── comparisons/
│   │   ├── correlations/
│   │   ├── distributions/
│   │   └── other_analysis/
│   ├── reports/
│   │   ├── excel/
│   │   ├── markdown/
│   │   └── pdf/
│   └── tables/
│       ├── comparisons/
│       └── descriptive_statistics/
├── src/
│   ├── analysis.py                  # Descriptive statistics and comparisons
│   ├── config.py                    # Paths and numeric value ranges
│   ├── data.py                      # CSV loading, cleaning, and quality checks
│   ├── report_generator.py          # Excel, Markdown, and PDF reports
│   └── visualization.py             # Analysis plots
├── tests/
│   └── test_project.py              # Data, analysis, and report tests
├── main.py                          # Command-line entry point
├── requirements.txt                 # Python dependencies
└── README.md
```

## Method and limitations

The pipeline standardizes recognized labels and parses supported numeric formats. Values outside configured numeric ranges are flagged and treated as missing; blank values are left missing. Exact duplicate rows are excluded, while potential outliers are retained.

Student–professional outcomes are compared with the Mann–Whitney U test, with p-values adjusted using the Benjamini–Hochberg method. The relationship between daily AI use and weekly time saved is measured using Spearman rank correlation.

The dataset's source, sampling method, and redistribution license were not provided. Responses are self-reported, missingness may affect results, and the sample may not represent students or professionals more broadly. The raw CSV is excluded from Git because its redistribution rights are unknown.
