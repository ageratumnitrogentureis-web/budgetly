"""Pure functions for filtering and summarising expenses."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from budgetly.models import Expense

ZERO = Decimal("0.00")


def filter_expenses(
    expenses: Iterable[Expense],
    category: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> list[Expense]:
    result = []
    for e in expenses:
        if category and e.category != category.lower():
            continue
        if start and e.spent_on < start:
            continue
        if end and e.spent_on > end:
            continue
        result.append(e)
    return sorted(result, key=lambda e: e.spent_on)


def total(expenses: Iterable[Expense]) -> Decimal:
    return sum((e.amount for e in expenses), ZERO)


def total_by_category(expenses: Iterable[Expense]) -> dict[str, Decimal]:
    """Category totals, largest first."""
    totals: dict[str, Decimal] = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, ZERO) + e.amount
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def monthly_totals(expenses: Iterable[Expense]) -> dict[str, Decimal]:
    """Totals keyed by 'YYYY-MM', oldest first."""
    totals: dict[str, Decimal] = {}
    for e in expenses:
        key = e.spent_on.strftime("%Y-%m")
        totals[key] = totals.get(key, ZERO) + e.amount
    return dict(sorted(totals.items()))


def top_expenses(expenses: Iterable[Expense], n: int = 3) -> list[Expense]:
    if n < 1:
        raise ValueError("n must be at least 1")
    return sorted(expenses, key=lambda e: e.amount, reverse=True)[:n]
