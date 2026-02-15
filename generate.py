#!/usr/bin/env python3
"""Accountability Calendars CLI - generates printable 10-week tracking calendars as PDFs."""

import os
from datetime import datetime, timedelta

from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Font
FONT_FAMILY = "Helvetica"

# Header colors (RGB)
COLOR_LIGHT_BLUE = (173, 216, 230)
COLOR_PEACH = (255, 218, 185)


def get_next_monday():
    """Get the next Monday from today (or today if it's already Monday)."""
    today = datetime.today()
    # weekday() returns 0 for Monday
    days_ahead = (7 - today.weekday()) % 7
    return today + timedelta(days=days_ahead)


def validate_date(date_str):
    """Validate date string is MM/DD/YYYY format and a Monday. Returns datetime or raises ValueError."""
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        raise ValueError("Invalid date format. Please use MM/DD/YYYY.")
    if dt.weekday() != 0:
        raise ValueError("Date must be a Monday.")
    return dt


def generate_week_dates(start_date):
    """Generate a list of 10 weeks of dates. Each week is a list of 7 datetime objects (Mon-Sun)."""
    weeks = []
    for week_num in range(10):
        week_start = start_date + timedelta(weeks=week_num)
        week = [week_start + timedelta(days=d) for d in range(7)]
        weeks.append(week)
    return weeks


def format_date(dt):
    """Format a datetime as MM/DD (no leading zeros stripped)."""
    return dt.strftime("%m/%d")


def _draw_header_row(pdf, x_start, y_start, col_widths, headers, has_total):
    """Draw the color-coded header row."""
    x = x_start
    row_h = 20

    for i, (header, w) in enumerate(zip(headers, col_widths)):
        # All column headers are blue
        pdf.set_fill_color(*COLOR_LIGHT_BLUE)

        pdf.rect(x, y_start, w, row_h, "FD")
        pdf.set_xy(x, y_start)
        pdf.cell(w, row_h, header, align="C")
        x += w


def _draw_week_row(pdf, x_start, y, col_widths, week_num, week_dates, row_h,
                   has_total, total_content=None, workout_labels=None):
    """Draw a single week row with date labels and optional content."""
    x = x_start

    # Week number column
    pdf.set_fill_color(*COLOR_PEACH)
    pdf.rect(x, y, col_widths[0], row_h, "FD")
    pdf.set_xy(x, y)
    pdf.cell(col_widths[0], row_h, str(week_num), align="C")
    x += col_widths[0]

    # Day columns
    for day_idx in range(7):
        w = col_widths[1 + day_idx]
        pdf.rect(x, y, w, row_h, "D")

        # Date in top-right corner
        date_str = format_date(week_dates[day_idx])
        pdf.set_font(FONT_FAMILY, "", 7)
        date_w = pdf.get_string_width(date_str)
        pdf.set_xy(x + w - date_w - 1, y + 5)
        pdf.cell(date_w, 5, date_str, align="R")

        # Workout label centered in cell (if applicable)
        if workout_labels:
            pdf.set_font(FONT_FAMILY, "", 9)
            pdf.set_xy(x, y + 5)
            pdf.cell(w, row_h - 5, workout_labels[day_idx], align="C")

        x += w

    # TOTAL column (if applicable)
    if has_total:
        w = col_widths[-1]
        pdf.rect(x, y, w, row_h, "D")
        if total_content:
            pdf.set_font(FONT_FAMILY, "", 8)
            line_h = row_h / len(total_content)
            for li, line in enumerate(total_content):
                pdf.set_xy(x + 2, y + li * line_h)
                pdf.cell(w - 4, line_h, line, align="L")
        x += w


def _create_calendar_pdf(filename, headers, col_widths, week_dates_list,
                         has_total, total_content_fn=None, workout_labels=None):
    """Create a landscape letter-size PDF calendar."""
    pdf = FPDF(orientation="L", unit="pt", format="letter")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    page_w = 11 * 72  # 792 pt
    page_h = 8.5 * 72  # 612 pt
    margin = 20

    total_col_w = page_w - 2 * margin
    # Scale col_widths to fit
    raw_total = sum(col_widths)
    scale = total_col_w / raw_total
    col_widths = [w * scale for w in col_widths]

    header_h = 20
    row_h = (page_h - 2 * margin - header_h) / 10

    x_start = margin
    y_start = margin

    # Draw header
    pdf.set_font(FONT_FAMILY, "B", 10)
    _draw_header_row(pdf, x_start, y_start, col_widths, headers, has_total)

    # Draw week rows
    pdf.set_font(FONT_FAMILY, "", 10)
    for week_idx, week_dates in enumerate(week_dates_list):
        y = y_start + header_h + week_idx * row_h
        total_content = total_content_fn(week_idx) if total_content_fn else None
        _draw_week_row(pdf, x_start, y, col_widths, week_idx + 1, week_dates,
                       row_h, has_total, total_content, workout_labels)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    return filepath


def generate_pages_read(start_date, goal):
    """Generate the Pages Read calendar PDF."""
    headers = ["Week"] + DAY_NAMES + ["TOTAL"]
    col_widths = [40] + [90] * 7 + [80]
    week_dates_list = generate_week_dates(start_date)

    def total_content(week_idx):
        return [f"Goal: {goal}", "Actual:"]

    return _create_calendar_pdf("Pages Read.pdf", headers, col_widths,
                                week_dates_list, has_total=True,
                                total_content_fn=total_content)


def generate_project_hours(start_date):
    """Generate the Project Hours calendar PDF."""
    headers = ["Week"] + DAY_NAMES + ["TOTAL"]
    col_widths = [40] + [90] * 7 + [80]
    week_dates_list = generate_week_dates(start_date)

    def total_content(week_idx):
        return ["Hours This Week:", "Debt:"]

    return _create_calendar_pdf("Project Hours.pdf", headers, col_widths,
                                week_dates_list, has_total=True,
                                total_content_fn=total_content)


def generate_workouts(start_date, workout_labels):
    """Generate the Workouts calendar PDF."""
    headers = ["Week"] + DAY_NAMES
    col_widths = [40] + [100] * 7
    week_dates_list = generate_week_dates(start_date)

    return _create_calendar_pdf("Workouts.pdf", headers, col_widths,
                                week_dates_list, has_total=False,
                                workout_labels=workout_labels)


def prompt_date():
    """Prompt the user for a valid Monday start date."""
    next_monday = get_next_monday()
    next_monday_str = next_monday.strftime("%m/%d/%Y")

    while True:
        print("\nChoose start date:")
        print(f"  1. Use next Monday ({next_monday_str})")
        print("  2. Enter a custom Monday")
        choice = input("Enter choice (1 or 2): ").strip()

        if choice == "1":
            return next_monday
        elif choice == "2":
            date_str = input("Enter start date (MM/DD/YYYY, must be a Monday): ").strip()
            try:
                return validate_date(date_str)
            except ValueError as e:
                print(f"  Error: {e}")
        else:
            print("  Error: Invalid choice. Please enter 1 or 2.")


def prompt_calendars():
    """Prompt the user for which calendars to generate."""
    options = {
        "1": "Pages Read",
        "2": "Project Hours",
        "3": "Workouts",
    }
    while True:
        print("\nWhich calendar(s) would you like to generate?")
        for key, name in options.items():
            print(f"  {key}. {name}")
        print("  4. All")
        choice = input("Enter choice(s) separated by commas (e.g. 1,3): ").strip()

        if choice == "4":
            return list(options.values())

        selected = []
        for c in choice.split(","):
            c = c.strip()
            if c in options and options[c] not in selected:
                selected.append(options[c])

        if selected:
            return selected
        print("  Error: Invalid selection. Please try again.")


def main():
    print("=== Accountability Calendars Generator ===\n")

    start_date = prompt_date()
    calendars = prompt_calendars()

    goal = None
    workout_labels = None

    if "Pages Read" in calendars:
        while True:
            goal_str = input("\nEnter weekly page goal (e.g. 100): ").strip()
            try:
                goal = int(goal_str)
                if goal > 0:
                    break
                print("  Error: Goal must be a positive number.")
            except ValueError:
                print("  Error: Please enter a valid number.")

    if "Workouts" in calendars:
        print("\nEnter workout labels for each day (these repeat every week):")
        workout_labels = []
        for day in DAY_NAMES:
            label = input(f"  {day}: ").strip()
            workout_labels.append(label)

    print("\nGenerating calendars...")

    for cal in calendars:
        if cal == "Pages Read":
            path = generate_pages_read(start_date, goal)
        elif cal == "Project Hours":
            path = generate_project_hours(start_date)
        elif cal == "Workouts":
            path = generate_workouts(start_date, workout_labels)
        print(f"  Created: {path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
