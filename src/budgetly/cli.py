"""Command-line interface."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from budgetly import reports
from budgetly.importer import import_csv
from budgetly.models import CATEGORIES, ValidationError, create_expense, parse_date
from budgetly.storage import ExpenseStore, StorageError


def default_data_file() -> Path:
    env = os.environ.get("BUDGETLY_DATA")
    return Path(env) if env else Path.home() / ".budgetly" / "expenses.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="budgetly", description="Track expenses.")
    parser.add_argument("--data-file", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add an expense")
    add.add_argument("--amount", required=True)
    add.add_argument("--category", required=True, choices=CATEGORIES)
    add.add_argument("--description", required=True)
    add.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="List expenses")
    ls.add_argument("--category", choices=CATEGORIES)
    ls.add_argument("--from", dest="start", default=None)
    ls.add_argument("--to", dest="end", default=None)

    sub.add_parser("report", help="Show spending summary")

    imp = sub.add_parser("import", help="Import expenses from CSV")
    imp.add_argument("file", type=Path)

    rm = sub.add_parser("remove", help="Remove an expense by id")
    rm.add_argument("id")
    return parser


def _format_row(e) -> str:
    return f"{e.id}  {e.spent_on}  {e.category:<13} {e.amount:>9}  {e.description}"


def run(args: argparse.Namespace, store: ExpenseStore) -> int:
    if args.command == "add":
        expense = create_expense(
            args.amount, args.category, args.description, args.date
        )
        store.add(expense)
        print(f"Added {expense.id}: {expense.amount} on {expense.category}")
        return 0

    if args.command == "list":
        start = parse_date(args.start) if args.start else None
        end = parse_date(args.end) if args.end else None
        rows = reports.filter_expenses(store.load(), args.category, start, end)
        if not rows:
            print("No expenses found.")
            return 0
        for e in rows:
            print(_format_row(e))
        print(f"Total: {reports.total(rows)}")
        return 0

    if args.command == "report":
        expenses = store.load()
        if not expenses:
            print("No expenses recorded yet.")
            return 0
        print("By category:")
        for cat, amount in reports.total_by_category(expenses).items():
            print(f"  {cat:<13} {amount:>9}")
        print("By month:")
        for month, amount in reports.monthly_totals(expenses).items():
            print(f"  {month}      {amount:>9}")
        print(f"Overall: {reports.total(expenses)}")
        return 0

    if args.command == "import":
        valid, errors = import_csv(args.file)
        store.add_many(valid)
        print(f"Imported {len(valid)} expenses, skipped {len(errors)}.")
        for message in errors:
            print(f"  {message}", file=sys.stderr)
        return 0 if not errors else 2

    if args.command == "remove":
        if store.remove(args.id):
            print(f"Removed {args.id}")
            return 0
        print(f"No expense with id {args.id}", file=sys.stderr)
        return 1

    return 1  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = ExpenseStore(args.data_file or default_data_file())
    try:
        return run(args, store)
    except (ValidationError, StorageError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
