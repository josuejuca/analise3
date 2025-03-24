from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import enum
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import re
from fastapi.responses import FileResponse
# teste 
from gateway_certidoes import router as gateway_certidoes_router
from db import get_db
from models import Analise, Proprietario, EsposaSocio, Imovel, StatusAnalise
from schemas import ConjugeCPFSchema,ProprietarioCPFSchema,AnaliseEtapa1CPFPayload,ConjugeCNPJSchema,ProprietarioCNPJSchema,AnaliseEtapa1CNPJPayload,ImovelSchema

# =======================
# CONFIGURAÇÃO DA API
# =======================

app = FastAPI()
app.include_router(gateway_certidoes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================
# ENDPOINTS
# =======================
# Acessar docs 
docs_path = Path("files")

@app.get("/files/{filename}", tags=["Arquivos"])
async def get_file(filename: str):
    file_path = docs_path / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path, filename=filename, media_type="application/octet-stream")
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")

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
    return results[0]

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
