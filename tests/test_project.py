import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src import config
from src.analysis import analyze_data
from src.data import load_and_clean
from src.report_generator import generate_reports


class ProjectTests(unittest.TestCase):
    def test_load_and_clean_handles_duplicates_labels_and_numeric_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text(
                "User_ID,User_Type,Gender,AI_Tool,AI_Usage_Hours_Per_Day\n"
                "A,student,M,Chat GPT,2 hrs\n"
                "B,Professional,other,gemini,25\n"
                "B,Professional,other,gemini,25\n",
                encoding="utf-8",
            )
            cleaned, quality, source_rows, duplicates = load_and_clean(path)

        self.assertEqual((source_rows, duplicates, len(cleaned)), (3, 1, 2))
        self.assertEqual(cleaned.loc[0, "User_Type"], "Student")
        self.assertEqual(cleaned.loc[0, "Gender"], "Male")
        self.assertEqual(cleaned.loc[0, "AI_Tool"], "ChatGPT")
        self.assertEqual(cleaned.loc[0, "AI_Usage_Hours_Per_Day"], 2)
        self.assertTrue(pd.isna(cleaned.loc[1, "AI_Usage_Hours_Per_Day"]))
        usage_quality = quality.loc[
            quality["column"].eq("AI_Usage_Hours_Per_Day")
        ].iloc[0]
        self.assertEqual(usage_quality["out_of_range_values"], 1)

    def test_analysis_produces_group_comparison_and_key_association(self):
        frame = pd.DataFrame(
            {
                "User_Type": ["Student"] * 4 + ["Professional"] * 4,
                "AI_Purpose": ["Studying"] * 4 + ["Coding"] * 4,
                "AI_Usage_Hours_Per_Day": [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5],
                "Time_Saved_Hours_Per_Week": [1, 2, 3, 4, 5, 6, 7, 8],
                "Productivity_Score": [3, 4, 5, 6, 4, 5, 6, 7],
            }
        )
        quality = pd.DataFrame(
            [{"column": "Age", "missing_count": 0, "missing_percent": 0}]
        )

        result = analyze_data(frame, quality, source_rows=8, duplicate_rows=0)

        self.assertEqual(len(result["comparisons"]), 3)
        self.assertAlmostEqual(result["correlation"].iloc[0]["spearman_rho"], 1.0)
        self.assertIn("purpose_comparison", result)

    def test_reports_generate_into_configured_folders(self):
        frame = pd.DataFrame(
            {
                "User_Type": ["Student", "Professional"],
                "AI_Purpose": ["Studying", "Coding"],
                "AI_Usage_Hours_Per_Day": [1, 3],
                "Time_Saved_Hours_Per_Week": [2, 4],
            }
        )
        quality = pd.DataFrame(
            [{"column": "Age", "missing_count": 0, "missing_percent": 0}]
        )
        results = analyze_data(frame, quality, source_rows=2, duplicate_rows=0)
        with tempfile.TemporaryDirectory() as directory:
            report_dirs = {
                key: Path(directory) / key for key in config.REPORT_DIRS
            }
            for path in report_dirs.values():
                path.mkdir()
            with patch.dict(config.REPORT_DIRS, report_dirs):
                reports = generate_reports(results, [], "sample.csv")
                self.assertTrue(reports["excel"].is_file())
                self.assertTrue(reports["markdown"].is_file())
                self.assertTrue(reports["pdf"].read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
