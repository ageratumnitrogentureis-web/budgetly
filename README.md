# budgetly

A small command-line expense tracker with JSON storage, CSV import and reports.

## Usage

```bash
uv sync
uv run budgetly add --amount 12.50 --category food --description "Lunch"
uv run budgetly list
uv run budgetly report
uv run budgetly import data/sample_expenses.csv
uv run budgetly remove <id>
```

Data is stored in `~/.budgetly/expenses.json`. Override with `--data-file`
or the `BUDGETLY_DATA` environment variable.

## Development

```bash
uv run pytest
uv run ruff check .
```
