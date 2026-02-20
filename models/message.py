from pydantic import BaseModel


class Message(BaseModel):
    """
    Internal representation of a Telegram message.

    This model is used to transport message data through the asynchronous queue,
    allowing workers to process the text while retaining necessary metadata
    for replying and database records.
    """

    user_id: int
    chat_id: int
    message_id: int
    text: str
