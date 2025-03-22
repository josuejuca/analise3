
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime, date
import enum
from db import Base, engine

# Enum para status da análise
class StatusAnalise(enum.Enum):
    pendente = "pendente"
    em_progresso = "em_progresso"
    concluida = "concluida"

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


