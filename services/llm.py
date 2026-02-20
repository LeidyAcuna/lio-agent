import logging
from datetime import datetime

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from core.config import get_settings
from core.exceptions.base import AIProcessingError, OllamaServiceError
from models.expense import CategoryEnum, Expense, SourceEnum

settings = get_settings()
logger = logging.getLogger(__name__)

EXPENSE_EXTRACTION_PROMPT = """

# ROL
Eres un Asistente de Extracción de Datos Financieros.
Tu única misión es transformar mensajes de texto en un formato estructurado.

# REGLAS DE CATEGORIZACIÓN (ESTRICTAS)
Debes clasificar el gasto UNICAMENTE en una de estas opciones:
- Categorías: {category}
- Fuentes: {source}

# TAREA
1. Extrae: fecha, total, categoría, fuente y descripción.
2. Si el usuario no especifica la fuente, asume "Efectivo" pero añade una nota en la descripción.
3. Si falta el monto, responde pidiendo el valor amablemente.
4. Usa la fecha actual {current_date} para calcular términos como "ayer" o "hace dos días".

# FORMATO DE SALIDA
Responde EXCLUSIVAMENTE con un objeto JSON que siga este esquema:
{{
  "completion_date": "YYYY-MM-DD HH-MM-SS",
  "total": 0.0,
  "category": "valor_del_enum_category",
  "source": "valor_del_enum_source",
  "description": "texto breve"
}}
"""


async def extract_expense_from_text(user_input: str) -> Expense:
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
    prompt_template = ChatPromptTemplate(
        [
            ("system", EXPENSE_EXTRACTION_PROMPT),
            ("human", "{user_input}"),
        ]
    )

    # Initialize the LLM (Ollama)
    llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://ollama:11434")

    output_parser = PydanticOutputParser(pydantic_object=Expense)

    # Construct the processing chain
    processing_chain = prompt_template | llm | output_parser

    try:
        logger.info("Invoking LLM for expense extraction...")

        extracted_data = await processing_chain.ainvoke(
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
