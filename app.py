from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import enum
from fastapi.middleware.cors import CORSMiddleware

# Configurações do Banco de Dados
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/api_docs"
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=280
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enum para status da análise
class StatusAnalise(enum.Enum):
    pendente = "pendente"
    em_progresso = "em_progresso"
    concluida = "concluida"

# =======================
# MODELOS SQLALCHEMY
# =======================

class Analise(Base):
    __tablename__ = "analise"
    id = Column("id_analise", Integer, primary_key=True, index=True)
    status = Column(String(45), nullable=True)  # Ex.: pendente, em_progresso, concluida
    link_pdf = Column(String(255), nullable=True)
    resumo = Column(String(255), nullable=True)
    data = Column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = Column(String(45), nullable=True)  # No novo banco, é VARCHAR(45)
    # Relacionamentos
    proprietarios = relationship("Proprietario", back_populates="analise", cascade="all, delete")
    imovel = relationship("Imovel", back_populates="analise", uselist=False, cascade="all, delete")


class Proprietario(Base):
    __tablename__ = "proprietario"
    id = Column("id_proprietario", Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analise.id_analise"), nullable=False)
    nome_razao = Column(String(255), nullable=True)
    nome_mae = Column(String(255), nullable=True)
    cpf_cnpj = Column(String(45), nullable=True)  # Aqui serão armazenados tanto CPF quanto CNPJ
    data_nascimento = Column(DateTime, nullable=True)
    estado_civil = Column(String(45), nullable=True)
    e_empresa = Column(Integer, nullable=True)  # 1 para True, 0 para False
    # Campos adicionais (representante, PDFs, etc.) – permanecem para uso futuro
    nome_representante = Column(String(255), nullable=True)
    nome_mae_representante = Column(String(255), nullable=True)
    cpf_representante = Column(String(45), nullable=True)
    data_nascimento_representante = Column(DateTime, nullable=True)
    pdf_sefaz = Column(String(255), nullable=True)
    pdf_trabalho = Column(String(255), nullable=True)
    pdf_nada_consta_civel = Column(String(255), nullable=True)
    pdf_nada_consta_criminal = Column(String(255), nullable=True)
    pdf_nada_consta_falencia = Column(String(255), nullable=True)
    pdf_nada_consta_especial = Column(String(255), nullable=True)
    pdf_receita = Column(String(255), nullable=True)
    pdf_tjdf_criminal = Column(String(255), nullable=True)
    pdf_tjdf_eleitoral = Column(String(255), nullable=True)
    pdf_tjdf_civel = Column(String(255), nullable=True)
    ad = Column(String(255), nullable=True)
    # Relacionamentos
    analise = relationship("Analise", back_populates="proprietarios")
    conjuge = relationship("EsposaSocio", back_populates="proprietario", uselist=False, cascade="all, delete")


class EsposaSocio(Base):
    __tablename__ = "esposa_socio"
    id = Column("id_esposa_socio", Integer, primary_key=True, index=True)
    proprietario_id = Column(Integer, ForeignKey("proprietario.id_proprietario"), nullable=False, unique=True)
    nome = Column(String(255), nullable=True)
    cpf = Column(String(45), nullable=True)  # Para cônjuges de pessoa física; no caso de CNPJ, use o mesmo campo
    data_nascimento = Column(DateTime, nullable=True)
    nome_mae = Column(String(255), nullable=True)
    pdf_sefaz = Column(String(255), nullable=True)
    pdf_trabalho = Column(String(255), nullable=True)
    pdf_nada_consta_civel = Column(String(255), nullable=True)
    pdf_nada_consta_criminal = Column(String(255), nullable=True)
    pdf_nada_consta_falencia = Column(String(255), nullable=True)
    pdf_nada_consta_especial = Column(String(255), nullable=True)
    pdf_receita = Column(String(255), nullable=True)
    pdf_tjdf_criminal = Column(String(255), nullable=True)
    pdf_tjdf_eleitoral = Column(String(255), nullable=True)
    pdf_tjdf_civel = Column(String(255), nullable=True)
    ad = Column(String(255), nullable=True)
    # Relacionamento
    proprietario = relationship("Proprietario", back_populates="conjuge")


class Imovel(Base):
    __tablename__ = "imovel"
    id = Column("id_imovel", Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analise.id_analise"), nullable=False, unique=True)
    cep = Column(String(45), nullable=True)
    endereco = Column(String(255), nullable=True)
    inscricao_iptu = Column(String(45), nullable=True)
    cartorio = Column(String(45), nullable=True)
    matricula = Column(String(45), nullable=True)
    pdf_sefaz = Column(String(45), nullable=True)
    # Relacionamento
    analise = relationship("Analise", back_populates="imovel")


# Cria as tabelas (caso não existam)
Base.metadata.create_all(bind=engine)

# =======================
# CONFIGURAÇÃO DA API
# =======================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =======================
# SCHEMAS Pydantic
# =======================

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

# =======================
# ENDPOINTS
# =======================

# Rota para etapa 1 via CPF
@app.post("/analises/etapa1/cpf/")
def create_analise_etapa1_cpf(payload: List[AnaliseEtapa1CPFPayload], db: Session = Depends(get_db)):
    results = []
    for analise_payload in payload:
        # Cria a análise
        new_analise = Analise(
            usuario_id=str(analise_payload.usuario_id),
            status=StatusAnalise.pendente.value,
            data=datetime.utcnow()
        )
        db.add(new_analise)
        db.commit()
        db.refresh(new_analise)

        proprietario_ids = []
        # Para cada proprietário na análise
        for prop in analise_payload.proprietarios:
            new_prop = Proprietario(
                analise_id=new_analise.id,
                nome_razao=prop.nome_completo,
                nome_mae=prop.nome_mae,
                cpf_cnpj=prop.cpf,  # Armazena o CPF
                data_nascimento=datetime.combine(prop.data_nascimento, datetime.min.time()),
                estado_civil=prop.estado_civil,
                e_empresa= 0
            )
            db.add(new_prop)
            db.commit()
            db.refresh(new_prop)
            proprietario_ids.append(new_prop.id)

            # Se o proprietário for casado e tiver dados do cônjuge, cria o registro na tabela esposa_socio
            if prop.estado_civil.lower() == "casado" and prop.conjuge:
                new_conjuge = EsposaSocio(
                    proprietario_id=new_prop.id,
                    nome=prop.conjuge.nome_completo,
                    cpf=prop.conjuge.cpf,
                    data_nascimento=datetime.combine(prop.conjuge.data_nascimento, datetime.min.time()),
                    nome_mae=prop.conjuge.nome_mae,
                )
                db.add(new_conjuge)
                db.commit()
                db.refresh(new_conjuge)
        results.append({"analise_id": new_analise.id, "proprietario_ids": proprietario_ids, "status": "success"})
    return results[0]

# Rota para etapa 1 via CNPJ
@app.post("/analises/etapa1/cnpj/")
def create_analise_etapa1_cnpj(payload: List[AnaliseEtapa1CNPJPayload], db: Session = Depends(get_db)):
    results = []
    for analise_payload in payload:
        new_analise = Analise(
            usuario_id=str(analise_payload.usuario_id),
            status=StatusAnalise.pendente.value,
            data=datetime.utcnow()
        )
        db.add(new_analise)
        db.commit()
        db.refresh(new_analise)

        proprietario_ids = []
        for prop in analise_payload.proprietarios:
            new_prop = Proprietario(
                analise_id=new_analise.id,
                nome_razao=prop.razao_social, # razao social
                nome_mae=prop.nome_fansasia, # nome fantasia
                cpf_cnpj=prop.cnpj,  # Armazena o CNPJ

                nome_representante=prop.nome_representante,
                nome_mae_representante=prop.nome_mae_representante,
                cpf_representante= prop.cpf_representante,
                data_nascimento_representante=datetime.combine(prop.data_nascimento_representante, datetime.min.time()),                
                e_empresa=1 if prop.e_empresa else 0
            )
            db.add(new_prop)
            db.commit()
            db.refresh(new_prop)
            proprietario_ids.append(new_prop.id)

        results.append({"analise_id": new_analise.id, "proprietarios": proprietario_ids})
    return {"status": "Cadastros (CNPJ) realizados com sucesso!", "analises": results}

# Rota para etapa 2: atualização ou criação dos dados do imóvel (em tabela separada)
@app.put("/analises/etapa2/{analise_id}/")
def update_analise_etapa2(analise_id: int, imovel: ImovelSchema, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    # Verifica se já existe registro de imóvel para a análise
    if analise.imovel:
        analise.imovel.cep = imovel.cep
        analise.imovel.endereco = imovel.endereco
        analise.imovel.inscricao_iptu = imovel.inscricao_iptu
        analise.imovel.cartorio = imovel.cartorio
        analise.imovel.matricula = imovel.matricula
        analise.imovel.pdf_sefaz = imovel.pdf_sefaz
    else:
        new_imovel = Imovel(
            analise_id=analise.id,
            cep=imovel.cep,
            endereco=imovel.endereco,
            inscricao_iptu=imovel.inscricao_iptu,
            cartorio=imovel.cartorio,
            matricula=imovel.matricula,
            pdf_sefaz=imovel.pdf_sefaz
        )
        db.add(new_imovel)
    # Altera o status da análise para "em_progresso"
    analise.status = StatusAnalise.em_progresso.value
    db.commit()
    db.refresh(analise)
    return {"status": "Dados do imóvel atualizados com sucesso!", "analise_id": analise.id}

# Endpoints para consulta

@app.get("/analises/")
def get_all_analises(db: Session = Depends(get_db)):
    analises = db.query(Analise).all()
    if not analises:
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada")
    return analises

@app.get("/analises/{analise_id}/")
def get_analise(analise_id: int, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return analise

@app.get("/analises/{analise_id}/proprietarios/")
def get_proprietarios_by_analise(analise_id: int, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    proprietarios = db.query(Proprietario).filter(Proprietario.analise_id == analise_id).all()
    return proprietarios

@app.get("/proprietarios/{proprietario_id}/")
def get_proprietario(proprietario_id: int, db: Session = Depends(get_db)):
    proprietario = db.query(Proprietario).filter(Proprietario.id == proprietario_id).first()
    if not proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    return proprietario

@app.get("/proprietarios/{proprietario_id}/conjuge/")
def get_conjuge_by_proprietario(proprietario_id: int, db: Session = Depends(get_db)):
    conjuge = db.query(EsposaSocio).filter(EsposaSocio.proprietario_id == proprietario_id).first()
    if not conjuge:
        raise HTTPException(status_code=404, detail="Cônjuge não encontrado para este proprietário")
    return conjuge

@app.get("/analises/usuario/{usuario_id}/")
def get_analises_by_usuario(usuario_id: int, db: Session = Depends(get_db)):
    analises = db.query(Analise).filter(Analise.usuario_id == str(usuario_id)).all()
    if not analises:
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada para este usuário")
    return analises

# =======================
# MODELOS DE RESPOSTA COMPLETA
# =======================
from typing import Optional
from datetime import datetime

class ImovelResponse(BaseModel):
    id: int
    cep: Optional[str] = None
    endereco: Optional[str] = None
    inscricao_iptu: Optional[str] = None
    cartorio: Optional[str] = None
    matricula: Optional[str] = None
    pdf_sefaz: Optional[str] = None

    class Config:
        orm_mode = True

class EsposaSocioResponse(BaseModel):
    id: int
    nome: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    nome_mae: Optional[str] = None
    pdf_sefaz: Optional[str] = None
    pdf_trabalho: Optional[str] = None
    pdf_nada_consta_civel: Optional[str] = None
    pdf_nada_consta_criminal: Optional[str] = None
    pdf_nada_consta_falencia: Optional[str] = None
    pdf_nada_consta_especial: Optional[str] = None
    pdf_receita: Optional[str] = None
    pdf_tjdf_criminal: Optional[str] = None
    pdf_tjdf_eleitoral: Optional[str] = None
    pdf_tjdf_civel: Optional[str] = None
    ad: Optional[str] = None

    class Config:
        orm_mode = True

class ProprietarioResponse(BaseModel):
    id: int
    analise_id: int
    nome_razao: Optional[str] = None
    nome_mae: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    estado_civil: Optional[str] = None
    e_empresa: Optional[int] = None
    nome_representante: Optional[str] = None
    nome_mae_representante: Optional[str] = None
    cpf_representante: Optional[str] = None
    data_nascimento_representante: Optional[datetime] = None
    pdf_sefaz: Optional[str] = None
    pdf_trabalho: Optional[str] = None
    pdf_nada_consta_civel: Optional[str] = None
    pdf_nada_consta_criminal: Optional[str] = None
    pdf_nada_consta_falencia: Optional[str] = None
    pdf_nada_consta_especial: Optional[str] = None
    pdf_receita: Optional[str] = None
    pdf_tjdf_criminal: Optional[str] = None
    pdf_tjdf_eleitoral: Optional[str] = None
    pdf_tjdf_civel: Optional[str] = None
    ad: Optional[str] = None
    conjuge: Optional[EsposaSocioResponse] = None

    class Config:
        orm_mode = True

class AnaliseFullResponse(BaseModel):
    id: int
    status: Optional[str] = None
    link_pdf: Optional[str] = None
    resumo: Optional[str] = None
    data: datetime
    usuario_id: Optional[str] = None
    imovel: Optional[ImovelResponse] = None
    proprietarios: List[ProprietarioResponse] = []

    class Config:
        orm_mode = True

# =======================
# NOVO ENDPOINT PARA CONSULTA COMPLETA DA ANÁLISE
# =======================
@app.get("/analises/full/{analise_id}/", response_model=AnaliseFullResponse)
def get_full_analise(analise_id: int, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return analise  

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
