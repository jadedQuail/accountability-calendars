"""Unit tests for generate.py"""

import os
import shutil
import tempfile
from datetime import datetime

import pytest

from generate import (
    validate_date,
    generate_week_dates,
    format_date,
    generate_pages_read,
    generate_project_hours,
    generate_workouts,
    OUTPUT_DIR,
)
import generate


@pytest.fixture
def tmp_output(tmp_path, monkeypatch):
    """Redirect OUTPUT_DIR to a temp directory for test isolation."""
    out = str(tmp_path / "output")
    monkeypatch.setattr(generate, "OUTPUT_DIR", out)
    return out


# --- Date validation ---

class TestValidateDate:
    def test_valid_monday_accepted(self):
        dt = validate_date("03/02/2026")
        assert dt == datetime(2026, 3, 2)
        assert dt.weekday() == 0  # Monday

    def test_non_monday_rejected(self):
        with pytest.raises(ValueError, match="Monday"):
            validate_date("03/03/2026")  # Tuesday

    def test_invalid_date_format_rejected(self):
        with pytest.raises(ValueError, match="format"):
            validate_date("2026-03-02")

    def test_invalid_date_string_rejected(self):
        with pytest.raises(ValueError, match="format"):
            validate_date("not-a-date")


# --- Date calculation ---

class TestWeekDates:
    def test_week_dates_generation(self):
        start = datetime(2026, 3, 2)  # Monday
        weeks = generate_week_dates(start)
        assert len(weeks) == 10
        assert len(weeks[0]) == 7
        # First week starts on Monday 3/2
        assert weeks[0][0] == datetime(2026, 3, 2)
        # First week ends on Sunday 3/8
        assert weeks[0][6] == datetime(2026, 3, 8)
        # Second week starts on Monday 3/9
        assert weeks[1][0] == datetime(2026, 3, 9)
        # Last week (week 10) starts on Monday 5/4
        assert weeks[9][0] == datetime(2026, 5, 4)

    def test_week_dates_cross_month_boundary(self):
        start = datetime(2026, 1, 26)  # Monday
        weeks = generate_week_dates(start)
        # Week 1 spans Jan 26 - Feb 1
        assert weeks[0][0] == datetime(2026, 1, 26)
        assert weeks[0][6] == datetime(2026, 2, 1)

    def test_week_dates_cross_year_boundary(self):
        start = datetime(2025, 12, 29)  # Monday
        weeks = generate_week_dates(start)
        # Week 1: Dec 29 - Jan 4
        assert weeks[0][0] == datetime(2025, 12, 29)
        assert weeks[0][6] == datetime(2026, 1, 4)

    def test_date_formatting(self):
        assert format_date(datetime(2026, 3, 2)) == "03/02"
        assert format_date(datetime(2026, 12, 25)) == "12/25"
        assert format_date(datetime(2026, 1, 5)) == "01/05"


# --- PDF generation ---

class TestPDFGeneration:
    def test_pages_read_pdf_created(self, tmp_output):
        start = datetime(2026, 3, 2)
        path = generate_pages_read(start, 100)
        assert os.path.isfile(path)
        assert path.endswith("Pages Read.pdf")

    def test_project_hours_pdf_created(self, tmp_output):
        start = datetime(2026, 3, 2)
        path = generate_project_hours(start)
        assert os.path.isfile(path)
        assert path.endswith("Project Hours.pdf")

    def test_workouts_pdf_created(self, tmp_output):
        start = datetime(2026, 3, 2)
        labels = ["4 Miles", "Weights", "Rest", "4 Miles", "Weights", "Rest", "Rest"]
        path = generate_workouts(start, labels)
        assert os.path.isfile(path)
        assert path.endswith("Workouts.pdf")

    def test_output_directory_created(self, tmp_output):
        assert not os.path.exists(tmp_output)
        start = datetime(2026, 3, 2)
        generate_pages_read(start, 100)
        assert os.path.isdir(tmp_output)
