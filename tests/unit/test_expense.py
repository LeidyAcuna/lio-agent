"""
Unit tests for the Expense model.

This module validates that the Expense Pydantic model correctly handles
data validation, type conversion, and default values.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.expense import CategoryEnum, Expense, SourceEnum


@pytest.fixture
def valid_expense_data():
    """
    Provides a dictionary containing valid expense data for testing.
    """
    return {
        "total": 100.0,
        "completion_date": "2026-01-30 22:10:58",
        "category": "Alimentación y aseo",
        "description": "Gasto en comida test",
        "source": "Bancolombia Leidy",
    }


def test_expense_creation_with_valid_data(valid_expense_data):
    """
    Verifies that the Expense model correctly parses and stores valid data.
    """
    # Act
    expense = Expense(**valid_expense_data)

    # Assert
    assert expense.total == Decimal("100.0")
    assert expense.category == CategoryEnum.alimento
    assert expense.description == "Gasto en comida test"
    assert expense.source == SourceEnum.bancolombia_leidy


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
    """
    Ensures that invalid data for specific fields raises a ValidationError.
    """
    # Arrange
    data = valid_expense_data.copy()
    data[field] = value

    # Act & Assert
    with pytest.raises(ValidationError):
        Expense(**data)


def test_expense_default_values(valid_expense_data):
    """
    Checks that the model automatically generates default values when optional fields are missing.
    """
    # Arrange: Remove completion_date to trigger default value generation
    data = valid_expense_data.copy()
    del data["completion_date"]

    # Act
    expense = Expense(**data)

    # Assert
    assert expense.completion_date is not None
