# Accountability Calendars

A Python CLI tool that generates printable 10-week accountability calendars as PDFs.

## Overview

This application creates custom calendars for tracking:
- **Pages Read Per Week** - Monitor reading progress with weekly goals
- **Workouts** - Track workout activities with daily labels
- **Project Hours** - Log time spent on projects with weekly totals

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python generate.py
```

The interactive prompts will ask you for:
1. **Start date** - Must be a Monday (MM/DD/YYYY format)
2. **Calendar type(s)** - Pages Read, Project Hours, Workouts, or any combination
3. **Weekly page goal** (if Pages Read selected)
4. **Daily workout labels** (if Workouts selected) - 7 labels (Mon-Sun) that repeat each week

Generated PDFs are saved to the `output/` folder.

## Calendar Types

### Pages Read
10-week grid with Mon-Sun columns plus a TOTAL column showing your weekly page goal and space for actual pages read.

### Project Hours
10-week grid with Mon-Sun columns plus a TOTAL column for tracking weekly hours and debt.

### Workouts
10-week grid with Mon-Sun columns. Each cell shows the workout label for that day (e.g., "4 Miles", "Rest").

## Running Tests

```bash
pytest test_generate.py -v
```

### Disclaimer
This app was largely vibe-coded using Claude Opus 4.6