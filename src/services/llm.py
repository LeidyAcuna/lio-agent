import logging
from datetime import datetime

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.core.config import get_settings
from src.core.exceptions import AIProcessingError, OllamaServiceError
from src.core.prompts import EXPENSE_EXTRACTION_PROMPT
from src.models.expense import CategoryEnum, Expense, SourceEnum

settings = get_settings()
logger = logging.getLogger(__name__)


class LlmService:
    """
    Service class for interacting with the llm.
    """

    def __init__(self):
        """
        Initializes the LlmService with the LLM, output parser, and prompt template.
        """
        self.llm = ChatOllama(
            model="llama3.1", temperature=0, base_url=settings.OLLAMA_URL
        )
        self.output_parser = PydanticOutputParser(pydantic_object=Expense)
        self.prompt_template = ChatPromptTemplate(
            [
                ("system", EXPENSE_EXTRACTION_PROMPT),
                ("human", "{user_input}"),
            ]
        )
        self.chain = self.prompt_template | self.llm | self.output_parser

    async def extract_expense_from_text(self, user_input: str) -> Expense:
        """
        Uses an LLM to extract structured expense data from a natural language message.

        Args:
            user_input (str): The raw text message from the user.

        Returns:
            Expense: A structured model containing the extracted financial data.

        Raises:
            OllamaServiceError: If there is a connection issue with the LLM service.
            AIProcessingError: If the LLM fails to parse the message or returns invalid data.
        """

        try:
            logger.info("Invoking LLM for expense extraction...")

            extracted_data = await self.chain.ainvoke(
                {
                    "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "category": [e.value for e in CategoryEnum],
                    "source": [e.value for e in SourceEnum],
                    "user_input": user_input,
                }
            )

            return extracted_data

        except ConnectionError as e:
            logger.error(f"Failed to connect to Ollama service: {e}")
            raise OllamaServiceError(f"Ollama service is unreachable: {str(e)}")

        except Exception as e:
            logger.error(f"Error during AI processing: {e}")
            raise AIProcessingError(f"The AI could not process the message: {str(e)}")
