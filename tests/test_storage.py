import pytest

from budgetly.storage import ExpenseStore, StorageError


def test_load_missing_file_returns_empty(store):
    assert store.load() == []


def test_save_and_load_round_trip(store, sample_expenses):
    store.save(sample_expenses)
    assert store.load() == sample_expenses


def test_add_appends(store, sample_expenses):
    store.save(sample_expenses[:2])
    store.add(sample_expenses[2])
    assert len(store.load()) == 3


def test_add_many_returns_count(store, sample_expenses):
    assert store.add_many(sample_expenses) == 5
    assert len(store.load()) == 5


def test_remove_existing_and_missing(store, sample_expenses):
    store.save(sample_expenses)
    assert store.remove("a1") is True
    assert store.remove("a1") is False
    assert [e.id for e in store.load()] == ["a2", "a3", "a4", "a5"]


def test_corrupt_json_raises_storage_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StorageError):
        ExpenseStore(path).load()


def test_no_temp_file_left_behind(store, sample_expenses):
    store.save(sample_expenses)
    assert not store.path.with_suffix(".tmp").exists()
