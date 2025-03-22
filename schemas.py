
# =======================
# SCHEMAS Pydantic
# =======================

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

# Para cadastro via CPF (pessoa física)
class ConjugeCPFSchema(BaseModel):
    nome_completo: str
    nome_mae: str
    cpf: str
    data_nascimento: date

class ProprietarioCPFSchema(BaseModel):
    nome_completo: str
    nome_mae: str
    data_nascimento: date
    cpf: str
    estado_civil: str
    e_empresa: bool
    conjuge: Optional[ConjugeCPFSchema] = None

class AnaliseEtapa1CPFPayload(BaseModel):
    usuario_id: int
    proprietarios: List[ProprietarioCPFSchema]

# Para cadastro via CNPJ (pessoa jurídica)
class ConjugeCNPJSchema(BaseModel):
    nome_completo: str
    cnpj: str
    data_nascimento: date

class ProprietarioCNPJSchema(BaseModel):
    razao_social: str
    nome_fansasia: str
    cnpj: str
    e_empresa: bool
    nome_representante: str
    cpf_representante: str    
    nome_mae_representante: str
    data_nascimento_representante: date
    conjuge: Optional[ConjugeCNPJSchema] = None

class AnaliseEtapa1CNPJPayload(BaseModel):
    usuario_id: int
    proprietarios: List[ProprietarioCNPJSchema]

# Para atualização dos dados do imóvel (etapa 2)

class ImovelSchema(BaseModel):
    cep: Optional[str] = None
    endereco: Optional[str] = None
    inscricao_iptu: Optional[str] = None
    cartorio: Optional[str] = None
    matricula: Optional[str] = None
    pdf_sefaz: Optional[str] = None

    class Config:
        orm_mode = True


