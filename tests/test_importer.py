import pytest

from budgetly.importer import import_csv
from budgetly.models import ValidationError

HEADER = "date,amount,category,description\n"


def test_import_valid_rows(tmp_path):
    f = tmp_path / "e.csv"
    f.write_text(HEADER + "2026-10-01,10.00,food,Lunch\n2026-10-02,5,other,Misc\n")
    expenses, errors = import_csv(f)
    assert len(expenses) == 2
    assert errors == []


def test_bad_rows_are_reported_with_line_numbers(tmp_path):
    f = tmp_path / "e.csv"
    f.write_text(
        HEADER
        + "2026-10-01,10.00,food,Lunch\n"
        + "2026-10-02,oops,food,Bad amount\n"
        + "2026-10-03,5.00,nonsense,Bad category\n"
    )
    expenses, errors = import_csv(f)
    assert len(expenses) == 1
    assert len(errors) == 2
    assert errors[0].startswith("line 3")
    assert errors[1].startswith("line 4")


def test_missing_columns_raises(tmp_path):
    f = tmp_path / "e.csv"
    f.write_text("date,amount\n2026-10-01,5\n")
    with pytest.raises(ValidationError, match="missing columns"):
        import_csv(f)


def test_sample_file_in_repo():
    expenses, errors = import_csv("data/sample_expenses.csv")
    assert len(expenses) == 6
    assert len(errors) == 1
