# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Accountability Calendars is a Python CLI tool that generates printable 10-week accountability calendars as PDFs for tracking:
- **Pages Read Per Week** - with weekly goals
- **Project Hours** - with weekly totals and debt tracking
- **Workouts** - with custom daily labels

All PDFs are landscape letter-size (11"x8.5") and saved to the `output/` folder.

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the Tool
```bash
python generate.py
```

The interactive prompts will ask for:
1. Start date (must be a Monday in MM/DD/YYYY format)
2. Calendar type(s) to generate
3. Type-specific data (weekly page goal, workout labels, etc.)

### Running Tests
```bash
# Run all tests with verbose output
pytest test_generate.py -v

# Run a specific test class
pytest test_generate.py::TestValidateDate -v

# Run a specific test
pytest test_generate.py::TestValidateDate::test_valid_monday_accepted -v
```

## Code Architecture

### Single Module Design
The entire application is in `generate.py` - a single-file architecture with clear functional separation.

### Core Functions

**Date handling:**
- `validate_date(date_str)` - Validates MM/DD/YYYY format and ensures it's a Monday
- `generate_week_dates(start_date)` - Returns list of 10 weeks, each week is a list of 7 datetime objects
- `format_date(dt)` - Formats datetime as MM/DD

**PDF generation:**
- `_create_calendar_pdf()` - Core PDF builder; handles layout, scaling, and rendering
- `_draw_header_row()` - Draws the colored header row with day names
- `_draw_week_row()` - Draws a single week row with dates, optional content, and TOTAL column
- `generate_pages_read()`, `generate_project_hours()`, `generate_workouts()` - Calendar-specific generators that configure headers, column widths, and content

**CLI interaction:**
- `prompt_date()` - Validates and returns start date
- `prompt_calendars()` - Returns list of calendar types to generate
- `main()` - Orchestrates the CLI flow

### Color System

The codebase uses RGB tuples for cell coloring:
- `COLOR_LIGHT_BLUE = (173, 216, 230)` - Applied to ALL header row cells (day names + TOTAL)
- `COLOR_PEACH = (255, 218, 185)` - Applied to the Week # column (first column)

**Current coloring behavior (as of issue #1):**
- Header row: All cells are blue (including Week, Mon-Sun, and TOTAL)
- Week number column: Peach background for all 10 rows
- Day cells: White/no fill
- TOTAL column cells: White/no fill

### PDF Layout Details

- **Orientation:** Landscape ("L")
- **Format:** Letter size (792pt × 612pt)
- **Margins:** 20pt on all sides
- **Header height:** 20pt
- **Row height:** Dynamically calculated to fit 10 weeks evenly
- **Column widths:** Defined per calendar type, then scaled proportionally to fit page width
- **Dates:** Displayed in top-right corner of each day cell (7pt font, MM/DD format)

### Calendar Types

1. **Pages Read**: Has TOTAL column with "Goal: X" and "Actual:" labels
2. **Project Hours**: Has TOTAL column with "Hours This Week:" and "Debt:" labels
3. **Workouts**: No TOTAL column; displays custom workout labels centered in each day cell

## Testing Approach

Tests use `pytest` with fixtures for temporary output directories (`tmp_output` fixture redirects `OUTPUT_DIR` using `monkeypatch`).

**Test organization:**
- `TestValidateDate` - Date validation logic
- `TestWeekDates` - Week generation and date formatting
- `TestPDFGeneration` - PDF creation and file output

Tests verify file creation, directory creation, and date calculations across month/year boundaries.

## Important Notes

- Start date **must** be a Monday (enforced by `validate_date()`)
- All calendars span exactly 10 weeks from the start date
- Workout labels are provided once and repeat for all 10 weeks
- The tool uses `fpdf2` library (imported as `fpdf`)
- Column widths are defined in points and auto-scaled to fit page width
