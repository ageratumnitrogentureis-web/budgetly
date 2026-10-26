from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from budgetly.models import Expense
from budgetly.storage import ExpenseStore


@pytest.fixture
def sample_expenses() -> list[Expense]:
    return [
        Expense(Decimal("45.20"), "food", "Groceries", date(2026, 9, 3), id="a1"),
        Expense(Decimal("12.00"), "transport", "Bus pass", date(2026, 9, 5), id="a2"),
        Expense(Decimal("900.00"), "housing", "Rent", date(2026, 9, 12), id="a3"),
        Expense(Decimal("30.00"), "food", "Takeaway", date(2026, 10, 2), id="a4"),
        Expense(Decimal("60.75"), "utilities", "Power", date(2026, 10, 4), id="a5"),
    ]


@pytest.fixture
def store(tmp_path: Path) -> ExpenseStore:
    return ExpenseStore(tmp_path / "data" / "expenses.json")
