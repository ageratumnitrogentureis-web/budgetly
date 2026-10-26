from datetime import date
from decimal import Decimal

import pytest

from budgetly import reports


def test_total(sample_expenses):
    assert reports.total(sample_expenses) == Decimal("1047.95")


def test_total_empty():
    assert reports.total([]) == Decimal("0.00")


def test_total_by_category_sorted_desc(sample_expenses):
    result = reports.total_by_category(sample_expenses)
    assert list(result) == ["housing", "food", "utilities", "transport"]
    assert result["food"] == Decimal("75.20")


def test_monthly_totals(sample_expenses):
    assert reports.monthly_totals(sample_expenses) == {
        "2026-09": Decimal("957.20"),
        "2026-10": Decimal("90.75"),
    }


def test_filter_by_category(sample_expenses):
    rows = reports.filter_expenses(sample_expenses, category="FOOD")
    assert [e.id for e in rows] == ["a1", "a4"]


def test_filter_by_date_range_is_inclusive(sample_expenses):
    rows = reports.filter_expenses(
        sample_expenses, start=date(2026, 9, 5), end=date(2026, 10, 2)
    )
    assert [e.id for e in rows] == ["a2", "a3", "a4"]


def test_top_expenses(sample_expenses):
    assert [e.id for e in reports.top_expenses(sample_expenses, 2)] == ["a3", "a5"]


def test_top_expenses_rejects_bad_n(sample_expenses):
    with pytest.raises(ValueError):
        reports.top_expenses(sample_expenses, 0)
