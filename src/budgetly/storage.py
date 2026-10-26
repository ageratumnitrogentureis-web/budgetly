"""JSON file persistence for expenses."""

from __future__ import annotations

import json
from pathlib import Path

from budgetly.models import Expense, ValidationError


class StorageError(RuntimeError):
    """Raised when the data file cannot be read."""


class ExpenseStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> list[Expense]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [Expense.from_dict(item) for item in raw]
        except (json.JSONDecodeError, TypeError, ValidationError) as exc:
            raise StorageError(f"Could not read {self.path}: {exc}") from exc

    def save(self, expenses: list[Expense]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        payload = json.dumps([e.to_dict() for e in expenses], indent=2)
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self.path)  # atomic on the same filesystem

    def add(self, expense: Expense) -> Expense:
        expenses = self.load()
        expenses.append(expense)
        self.save(expenses)
        return expense

    def add_many(self, new: list[Expense]) -> int:
        expenses = self.load()
        expenses.extend(new)
        self.save(expenses)
        return len(new)

    def remove(self, expense_id: str) -> bool:
        expenses = self.load()
        kept = [e for e in expenses if e.id != expense_id]
        if len(kept) == len(expenses):
            return False
        self.save(kept)
        return True
