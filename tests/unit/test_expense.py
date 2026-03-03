from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.expense import CategoryEnum, Expense, SourceEnum


# Valid data for expense
@pytest.fixture
def valid_expense_data():
    return {
        "total": 100.0,
        "completion_date": "2026-01-30 22:10:58",
        "category": "Alimentación y aseo",
        "description": "Gasto en comida test",
        "source": "Bancolombia Leidy",
    }


# 1. Test de éxito (limpio y directo)
def test_expense_creation_with_valid_data(valid_expense_data):
    expense = Expense(**valid_expense_data)
    assert expense.total == Decimal("100.0")
    assert expense.category == CategoryEnum.alimento
    assert expense.description == "Gasto en comida test"
    assert expense.source == SourceEnum.bancolombia_leidy


# 2. Test parametrizado para múltiples fallos (Nivel Senior)
@pytest.mark.parametrize(
    "field, value",
    [
        ("total", -100.0),
        ("description", ""),
        ("source", "Bancolombia"),
        ("category", "Alimento"),
        ("completion_date", "No es una fecha"),
    ],
)
def test_expense_validation_errors(valid_expense_data, field, value):
    data = valid_expense_data.copy()
    data[field] = value

    with pytest.raises(ValidationError):
        Expense(**data)


# 3. Test de valores por defecto
def test_expense_default_values(valid_expense_data):
    # Quitamos la fecha para ver si se genera automáticamente
    data = valid_expense_data.copy()
    del data["completion_date"]

    expense = Expense(**data)
    assert expense.completion_date is not None
