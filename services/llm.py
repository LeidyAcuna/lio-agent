from datetime import datetime

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from models.expense import CategoryEnum, Expense, SourceEnum

system_prompt = """

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


def test_ollama(user_input: str) -> Expense:
    template = ChatPromptTemplate(
        [
            ("system", system_prompt),
            ("human", "{user_input}"),
        ]
    )

    llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://ollama:11434")
    parser = PydanticOutputParser(pydantic_object=Expense)

    chain = template | llm | parser

    ai_msg = chain.invoke(
        {
            "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": [e.value for e in CategoryEnum],
            "source": [e.value for e in SourceEnum],
            "user_input": user_input,
        }
    )

    return ai_msg
