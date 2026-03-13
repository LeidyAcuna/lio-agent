from datetime import datetime

from pydantic import BaseModel


class AuditLog(BaseModel):
    """
    Internal representation of an audit log.

    This model is used to record the audit logs of the messages
    not authorized to be received by the bot.
    """

    user_id: int
    fullname: str | None = None
    username: str | None = None
    chat_id: int
    message_text: str
    message_date: datetime


class AuditLogInDB(AuditLog):
    id: int
    created_at: datetime
