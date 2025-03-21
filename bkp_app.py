from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
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

# Modelos do Banco de Dados conforme o SQL

class Analise(Base):
    __tablename__ = "analise"
    id = Column("id_analise", Integer, primary_key=True, index=True)
    status = Column(String(45), nullable=True, default=StatusAnalise.pendente.value)
    link_pdf = Column(String(255), nullable=True)
    resumo = Column(String(255), nullable=True)
    data = Column(DateTime, nullable=False, default=datetime.utcnow)
    # O campo usuario_id está definido como VARCHAR(45) no banco; caso deseje trabalhar com int, converta na API.
    usuario_id = Column(String(45), nullable=False)
    # Relacionamentos
    proprietarios = relationship("Proprietario", back_populates="analise")
    imovel = relationship("Imovel", back_populates="analise", uselist=False)

class Proprietario(Base):
    __tablename__ = "proprietario"
    id = Column("id_proprietario", Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analise.id_analise"), nullable=False)
    # No banco, o campo é "nome_razao". Aqui o chamamos de nome_completo para a API.
    nome_razao = Column(String(255), nullable=True)
    nome_mae = Column(String(255), nullable=True)
    cpf_cnpj = Column(String(45), nullable=True)
    data_nascimento = Column(DateTime, nullable=True)
    estado_civil = Column(String(45), nullable=True)
    e_empresa = Column(Integer, nullable=True)
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
    conjuge = relationship("EsposaSocio", back_populates="proprietario", uselist=False)

class EsposaSocio(Base):
    __tablename__ = "esposa_socio"
    id = Column("id_esposa_socio", Integer, primary_key=True, index=True)
    proprietario_id = Column(Integer, ForeignKey("proprietario.id_proprietario"), nullable=False, unique=True)
    nome = Column(String(255), nullable=True)
    cpf = Column(String(45), nullable=True)
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

# Criação das tabelas (caso ainda não existam)
Base.metadata.create_all(bind=engine)

# Aplicação FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas do Pydantic para validação

class EsposaSocioSchema(BaseModel):
    nome_completo: Optional[str] = None  # Mapeado a partir de "nome"
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    nome_mae: Optional[str] = None

    class Config:
        orm_mode = True

class ProprietarioSchema(BaseModel):
    nome_completo: str           # Mapeado a partir de "nome_razao"
    nome_mae: Optional[str] = None
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None     # Mapeado a partir de "cpf_cnpj"
    estado_civil: Optional[str] = None
    conjuge: Optional[EsposaSocioSchema] = None

    class Config:
        orm_mode = True

class ImovelSchema(BaseModel):
    cep: Optional[str] = None
    endereco: Optional[str] = None
    matricula: Optional[str] = None
    cartorio: Optional[str] = None
    inscricao_iptu: Optional[str] = None

    class Config:
        orm_mode = True

class AnaliseSchema(BaseModel):
    status: Optional[StatusAnalise] = StatusAnalise.pendente
    link_pdf: Optional[str] = None
    resumo: Optional[str] = None
    data: datetime
    usuario_id: str
    proprietarios: List[ProprietarioSchema] = []
    imovel: Optional[ImovelSchema] = None

    class Config:
        orm_mode = True

# Payload para criação da primeira etapa da análise
class AnaliseEtapa1Payload(BaseModel):
    usuario_id: int
    proprietarios: List[ProprietarioSchema]

# Endpoint para criar análise (etapa 1: cadastro de proprietários)
@app.post("/analises/etapa1/")
def create_analise_etapa1(payload: AnaliseEtapa1Payload, db: Session = Depends(get_db)):
    new_analise = Analise(
        usuario_id=str(payload.usuario_id),  # Convertendo para string conforme o schema do banco
        status=StatusAnalise.pendente.value,
        data=datetime.utcnow()
    )
    db.add(new_analise)
    db.commit()
    db.refresh(new_analise)

    for prop in payload.proprietarios:
        new_proprietario = Proprietario(
            analise_id=new_analise.id,
            nome_razao=prop.nome_completo,
            nome_mae=prop.nome_mae,
            cpf_cnpj=prop.cpf,
            data_nascimento=prop.data_nascimento,
            estado_civil=prop.estado_civil
        )
        db.add(new_proprietario)
        db.commit()
        db.refresh(new_proprietario)

        # Se o proprietário está casado e foi enviado conjuge, cria registro na tabela esposa_socio
        if prop.estado_civil == "casado" and prop.conjuge:
            new_conjuge = EsposaSocio(
                proprietario_id=new_proprietario.id,
                nome=prop.conjuge.nome_completo,
                cpf=prop.conjuge.cpf,
                data_nascimento=prop.conjuge.data_nascimento,
                nome_mae=prop.conjuge.nome_mae
            )
            db.add(new_conjuge)
            db.commit()
            db.refresh(new_conjuge)

    return {"analise_id": new_analise.id, "status": "Proprietários cadastrados com sucesso!"}

# Endpoint para atualizar análise com dados do imóvel (etapa 2)
@app.put("/analises/etapa2/{analise_id}/")
def update_analise_etapa2(analise_id: int, imovel: ImovelSchema, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Se já existir um imóvel para essa análise, atualiza; caso contrário, cria um novo.
    if analise.imovel:
        analise.imovel.cep = imovel.cep
        analise.imovel.endereco = imovel.endereco
        analise.imovel.matricula = imovel.matricula
        analise.imovel.cartorio = imovel.cartorio
        analise.imovel.inscricao_iptu = imovel.inscricao_iptu
    else:
        new_imovel = Imovel(
            analise_id=analise.id,
            cep=imovel.cep,
            endereco=imovel.endereco,
            matricula=imovel.matricula,
            cartorio=imovel.cartorio,
            inscricao_iptu=imovel.inscricao_iptu
        )
        db.add(new_imovel)
    analise.status = StatusAnalise.em_progresso.value
    db.commit()
    db.refresh(analise)
    return {"status": "Dados do imóvel cadastrados com sucesso!", "analise_id": analise.id}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
