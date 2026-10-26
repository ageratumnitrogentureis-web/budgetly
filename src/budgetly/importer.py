"""CSV import."""

from __future__ import annotations

import csv
from pathlib import Path

from budgetly.models import Expense, ValidationError, create_expense

REQUIRED_COLUMNS = {"date", "amount", "category", "description"}


def import_csv(path: Path | str) -> tuple[list[Expense], list[str]]:
    """Read expenses from a CSV file.

    Returns (valid expenses, error messages). Bad rows are skipped, not fatal.
    """
    expenses: list[Expense] = []
    errors: list[str] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValidationError(f"CSV missing columns: {', '.join(sorted(missing))}")
        for line_no, row in enumerate(reader, start=2):
            try:
                expenses.append(
                    create_expense(
                        amount=row["amount"],
                        category=row["category"],
                        description=row["description"],
                        spent_on=row["date"],
                    )
                )
            except ValidationError as exc:
                errors.append(f"line {line_no}: {exc}")
    return expenses, errors
