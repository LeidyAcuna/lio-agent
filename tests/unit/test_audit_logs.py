"""
Unit tests for the AuditLog model.

This module validates that the AuditLog Pydantic model correctly handles
data validation, type conversion, and required fields for security logging.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.audit_log import AuditLog


@pytest.fixture
def valid_audit_data():
    """
    Provides a dictionary containing valid audit log data for testing.
    """
    return {
        "user_id": 2061932699,
        "chat_id": 2061932699,
        "message_text": "Unauthorized access attempt detected",
        "message_date": datetime.now(),
    }


def test_audit_log_creation_with_valid_data(valid_audit_data):
    """
    Verifies that the AuditLog model correctly parses and stores valid security data.
    """
    # Act
    log_entry = AuditLog(**valid_audit_data)

    # Assert
    assert log_entry.user_id == 2061932699
    assert log_entry.chat_id == 2061932699
    assert "Unauthorized" in log_entry.message_text


@pytest.mark.parametrize(
    "field, value",
    [
        ("user_id", 10.58),
        ("chat_id", None),
        ("fullname", 4587),
        ("username", 58774),
        ("message_text", None),
        ("message_date", "Invalid Date"),
    ],
)
def test_audit_log_validation_errors(valid_audit_data, field, value):
    """
    Ensures that invalid or malformed data triggers a ValidationError to maintain data integrity.
    """
    # Arrange
    data = valid_audit_data.copy()
    data[field] = value

    # Act - Assert
    with pytest.raises(ValidationError):
        AuditLog(**data)
