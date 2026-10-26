"""Expense model and validation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation

CATEGORIES = (
    "food",
    "transport",
    "housing",
    "utilities",
    "entertainment",
    "health",
    "other",
)


class ValidationError(ValueError):
    """Raised when expense data is invalid."""


@dataclass(frozen=True)
class Expense:
    amount: Decimal
    category: str
    description: str
    spent_on: date
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "spent_on": self.spent_on.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Expense:
        try:
            return cls(
                id=data["id"],
                amount=Decimal(data["amount"]),
                category=data["category"],
                description=data["description"],
                spent_on=date.fromisoformat(data["spent_on"]),
            )
        except (KeyError, InvalidOperation, ValueError) as exc:
            raise ValidationError(f"Malformed expense record: {exc}") from exc


def parse_amount(raw: object) -> Decimal:
    """Parse a positive monetary amount, rounded to 2 decimal places."""
    try:
        value = Decimal(str(raw).strip())
        if not value.is_finite():
            raise InvalidOperation
        value = value.quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValidationError(f"Invalid amount: {raw!r}") from None
    if value <= 0:
        raise ValidationError("Amount must be positive")
    return value


def parse_date(raw: object) -> date:
    if isinstance(raw, date):
        return raw
    try:
        return date.fromisoformat(str(raw).strip())
    except ValueError:
        raise ValidationError(f"Invalid date (use YYYY-MM-DD): {raw!r}") from None


def create_expense(
    amount: object,
    category: str,
    description: str,
    spent_on: object | None = None,
) -> Expense:
    """Validate raw input and build an Expense."""
    category = category.strip().lower()
    if category not in CATEGORIES:
        raise ValidationError(
            f"Unknown category {category!r}. Choose from: {', '.join(CATEGORIES)}"
        )
    description = description.strip()
    if not description:
        raise ValidationError("Description cannot be empty")
    return Expense(
        amount=parse_amount(amount),
        category=category,
        description=description,
        spent_on=parse_date(spent_on) if spent_on is not None else date.today(),
    )
