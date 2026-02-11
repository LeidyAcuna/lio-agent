from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    alimento = "Alimentación y aseo"
    cuidado_personal = "Cuidado personal"
    preferencias = "Preferencias"
    pagos = "Pagos"


class SourceEnum(str, Enum):
    bancolombia_leidy = "Bancolombia Leidy"
    nequi_leidy = "Nequi Leidy"
    nubank_leidy = "Nubank Leidy"
    nubank_mercado = "Nubank Mercado"
    nubank_yamile = "Nubank Yamile"
    davivienda_yamile = "Davivienda Yamile"
    nequi_yamile = "Nequi Yamile"
    efectivo_casa = "Efectivo"


class Expense(BaseModel):
    completion_date: datetime = Field(default_factory=datetime.now)
    category: CategoryEnum
    source: SourceEnum
    description: str = Field(..., min_length=1)
    total: Decimal = Field(..., gt=0)
