from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    """
    Enumeration of allowed expense categories for classification.
    """

    alimento = "Alimentación y aseo"
    cuidado_personal = "Cuidado personal"
    preferencias = "Preferencias"
    pagos = "Pagos"


class SourceEnum(str, Enum):
    """
    Enumeration of financial sources or payment methods.
    """

    bancolombia_leidy = "Bancolombia Leidy"
    nequi_leidy = "Nequi Leidy"
    nubank_leidy = "Nubank Leidy"
    nubank_mercado = "Nubank Mercado"
    nubank_yamile = "Nubank Yamile"
    davivienda_yamile = "Davivienda Yamile"
    nequi_yamile = "Nequi Yamile"
    efectivo_casa = "Efectivo"


class Expense(BaseModel):
    """
    Structured data model representing a recorded expense.

    This model is used by the LLM output parser to validate and structure
    the data extracted from natural language messages.
    """

    completion_date: datetime = Field(
        default_factory=datetime.now,
        description="The date and time when the expense occurred.",
    )
    category: CategoryEnum = Field(
        ..., description="The classification category of the expense."
    )
    source: SourceEnum = Field(
        ..., description="The payment method or source of the funds."
    )
    description: str = Field(
        ...,
        min_length=1,
        description="A brief text describing what the expense was for.",
    )
    total: Decimal = Field(
        ...,
        gt=0,
        description="The monetary amount of the expense, must be greater than zero.",
    )
