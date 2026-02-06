## Overview

This mini-project implements a simple **data cleaning and validation pipeline** for raw scraped JSON data.
It takes noisy product-like records, cleans and normalises them, then validates the cleaned records and produces a human-readable data quality report.

## Files

- **cleaner.py**: Cleans raw records (e.g. trims whitespace, normalises prices, standardises dates) and writes `cleaned_output.json`.
- **validator.py**: Validates cleaned records and generates `quality_report.txt`.
- **sample_data.json**: Example raw scraped data (top-level JSON array of objects).
- **cleaned_output.json**: Example output produced by running `cleaner.py` on `sample_data.json`.
- **quality_report.txt**: Example data quality report produced by running `validator.py` on `cleaned_output.json`.
- **prompt-log.md**: Brief log of the AI-assisted development process.

## Data Model (Cleaned Records)

Each cleaned record in `cleaned_output.json` has the following fields:

- **id**: String identifier (or `null` if missing).
- **title**: Text title, with HTML removed, whitespace collapsed, and encoding normalised.
- **content**: Main body/content text, cleaned the same way as `title`. For legacy data it is derived from a raw `description` field.
- **price**: Numeric price as a float (or `null` if not parseable).
- **currency**: Uppercased currency code such as `USD` or `EUR` (or `null`).
- **url**: Trimmed URL string.
- **scraped_at**: ISO-8601 date string (`YYYY-MM-DD`) or `null`.

Validation specifically enforces:

- Required fields: `title`, `content`, and `url`.
- Minimum content length of **30 characters**.
- Basic URL shape (must start with `http://` or `https://`).

## How to Run

Prerequisite: **Python 3.9+** (no external packages required).

From the project root:

1. **Clean the raw data**:

   ```bash
   python cleaner.py sample_data.json cleaned_output.json
   ```

2. **Validate the cleaned data and generate a quality report**:

   ```bash
   python validator.py cleaned_output.json quality_report.txt
   ```

You can inspect `cleaned_output.json` and `quality_report.txt` to see how the pipeline:

- Cleans and normalises the raw scraped records.
- Distinguishes valid vs. invalid records.
- Reports completeness percentages per field and the most common validation failures.

