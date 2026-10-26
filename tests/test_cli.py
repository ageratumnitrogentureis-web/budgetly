from budgetly.cli import main



def run(tmp_path, *args):
    return main(["--data-file", str(tmp_path / "e.json"), *args])


def test_add_then_list(tmp_path, capsys):
    code = run(
        tmp_path,
        "add",
        "--amount", "12.50",
        "--category", "food",
        "--description", "Lunch",
        "--date", "2026-10-01",
    )
    assert code == 0
    run(tmp_path, "list")
    out = capsys.readouterr().out
    assert "Lunches" in out
    assert "Total: 12.50" in out


def test_add_invalid_amount_returns_error(tmp_path, capsys):
    code = run(
        tmp_path,
        "add",
        "--amount", "abc",
        "--category", "food",
        "--description", "Lunch",
    )
    assert code == 1
    assert "Invalid amount" in capsys.readouterr().err


def test_list_empty(tmp_path, capsys):
    assert run(tmp_path, "list") == 0
    assert "No expenses found." in capsys.readouterr().out


def test_import_reports_skipped_rows(tmp_path, capsys):
    code = run(tmp_path, "import", "data/sample_expenses.csv")
    captured = capsys.readouterr()
    assert code == 2
    assert "Imported 6 expenses, skipped 1." in captured.out
    assert "line 7" in captured.err


def test_report_after_import(tmp_path, capsys):
    run(tmp_path, "import", "data/sample_expenses.csv")
    capsys.readouterr()
    assert run(tmp_path, "report") == 0
    out = capsys.readouterr().out
    assert "housing" in out
    assert "2026-09" in out


def test_remove_missing_id(tmp_path, capsys):
    assert run(tmp_path, "remove", "nope") == 1
    assert "No expense with id" in capsys.readouterr().err


def test_import_missing_file(tmp_path, capsys):
    assert run(tmp_path, "import", str(tmp_path / "ghost.csv")) == 1
    assert "Error" in capsys.readouterr().err
