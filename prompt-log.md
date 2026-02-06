## Prompt Log (AI-Assisted Development)

1. **Initial request**
   - The user specified an assignment to build a small data cleaning and validation pipeline.
   - Required deliverables: `cleaner.py`, `validator.py`, `sample_data.json`, `cleaned_output.json`, `quality_report.txt`, `README.md`, and `prompt-log.md`.

2. **Designing the data model and rules**
   - Chose a simple product-like schema with fields such as `id`, `title`, `description`, `price`, `currency`, `url`, and `scraped_at`.
   - Defined cleaning behaviours: normalise whitespace, parse prices from strings with currency symbols, and standardise dates to ISO format.
   - Defined validation rules: required fields (`title`, `price`, `url`), non-negative numeric `price`, basic URL shape, and ISO-style `scraped_at` when present.

3. **Implementing `cleaner.py`**
   - Implemented functions to:
     - Normalise whitespace.
     - Parse numeric prices from strings such as `"USD 10.50"` or `"$9.99"`.
     - Parse several simple date formats into `YYYY-MM-DD`.
   - Added a `main` entrypoint so the script can be run as:
     - `python cleaner.py sample_data.json cleaned_output.json`.

4. **Implementing `validator.py`**
   - Implemented record-level validation with a small rule set.
   - Aggregated per-record violations into summary statistics.
   - Generated a human-readable text report listing totals and per-record issues.
   - Exposed a CLI:
     - `python validator.py cleaned_output.json quality_report.txt`.

5. **Creating sample data and outputs**
   - Authored `sample_data.json` with intentionally messy inputs (extra whitespace, different date formats, invalid/missing fields).
   - Derived `cleaned_output.json` to reflect how `cleaner.py` transforms this input.
   - Constructed `quality_report.txt` to match the violations that `validator.py` would produce on the cleaned data.

6. **Documentation**
   - Wrote `README.md` to describe the pipeline, data model, and step-by-step usage.
   - Recorded this brief prompt log to document how AI was used to design and implement the solution.

