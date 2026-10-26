from datetime import date
from decimal import Decimal

import pytest

from budgetly.models import (
    Expense,
    ValidationError,
    create_expense,
    parse_amount,
    parse_date,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("12.5", "12.50"), (3, "3.00"), (" 7.999 ", "8.00"), ("0.01", "0.01")],
)
def test_parse_amount_valid(raw, expected):
    assert parse_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["abc", "", "-5", "0", "NaN", "Infinity"])
def test_parse_amount_invalid(raw):
    with pytest.raises(ValidationError):
        parse_amount(raw)


def test_parse_date_accepts_date_and_iso_string():
    assert parse_date(date(2026, 1, 2)) == date(2026, 1, 2)
    assert parse_date("2026-01-02") == date(2026, 1, 2)


def test_parse_date_rejects_bad_format():
    with pytest.raises(ValidationError):
        parse_date("02/01/2026")


def test_create_expense_normalises_input():
    e = create_expense("10", "  FOOD ", "  Lunch  ", "2026-10-01")
    assert e.category == "food"
    assert e.description == "Lunch"
    assert e.amount == Decimal("10.00")
    assert len(e.id) == 8


def test_create_expense_defaults_to_today():
    assert create_expense("1", "other", "x").spent_on == date.today()


def test_create_expense_rejects_unknown_category():
    with pytest.raises(ValidationError, match="Unknown category"):
        create_expense("5", "gadgets", "Phone")


def test_create_expense_rejects_blank_description():
    with pytest.raises(ValidationError, match="Description"):
        create_expense("5", "food", "   ")


def test_round_trip_dict():
    e = create_expense("19.99", "health", "Vitamins", "2026-10-05")
    assert Expense.from_dict(e.to_dict()) == e


def test_from_dict_malformed():
    with pytest.raises(ValidationError):
        Expense.from_dict({"id": "x"})
