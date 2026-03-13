"""
Integration tests for the AuditLogsRepository.

This module ensures that security audit logs are correctly persisted and
retrieved from the PostgreSQL database, maintaining a reliable audit trail.
"""

from datetime import datetime

import pytest

from src.core.database import DatabaseManager
from src.models.audit_log import AuditLog
from src.repositories.audit_logs import AuditLogsRepository


@pytest.mark.asyncio
async def test_audit_repository_save():
    """
    Validates that a new audit log entry can be successfully saved and retrieved.

    This test verifies the full database round-trip for security events,
    ensuring that the latest entry in the DB matches the one just created.
    """
    # Arrange: Initialize DB and repository
    db = DatabaseManager()
    await db.initialize()

    audit_logs_repository = AuditLogsRepository(db=db)
    await audit_logs_repository.setup_schema()

    unique_message = f"Unauthorized access attempt at {datetime.now()}"
    audit_log = AuditLog(
        user_id=2061932699,
        chat_id=2061932699,
        username="leidyacunag",
        fullname="Leidy Acuña",
        message_text=unique_message,
        message_date=datetime.now(),
    )

    # Act
    await audit_logs_repository.create(audit_log)
    last_audit_log = await audit_logs_repository.get_last_audit_log()

    # Assert
    assert last_audit_log.id is not None
    assert last_audit_log.user_id == audit_log.user_id
    assert last_audit_log.message_text == unique_message

    # Cleanup
    await db.shutdown()
