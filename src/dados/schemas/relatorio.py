from pydantic import BaseModel


class RelatorioValorResponse(BaseModel):
    valor_total: float
