# gateway_certidoes.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

# PDFs
from PyPDF2 import PdfMerger
import os
import uuid


# Importa os modelos e a função de obtenção do banco de dados do seu app
 # :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
from models import Analise,Proprietario
from db import get_db
# Importa as funções de emissão de certidões do módulo post_trf1.py
from post_trf1 import (
    process_cnpj_criminal,
    process_cnpj_civel,
    process_cnpj_eleitoral,
    process_cpf_criminal,
    process_cpf_civel,
    process_cpf_eleitoral
)  # :contentReference[oaicite:6]{index=6}&#8203;:contentReference[oaicite:7]{index=7}

from post_nada_consta import (
   process_nada_consta_especial 
)

from post_receita import (
    process_cpf_receita
)

router = APIRouter()

def process_certidoes(analise_id: int, cnpj_cpf: str, nome_mae: str, doc_type: str, db: Session):
    """
    Processa a emissão das certidões em background e atualiza o registro da análise.
    O parâmetro doc_type define se o documento é para CPF ou CNPJ.
    """
    # Busca a análise pelo ID
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        # Se a análise não for encontrada, encerra o processamento
        return

    # Emite as certidões conforme o tipo (CPF ou CNPJ)
    certidoes = []
    if doc_type.upper() == "CPF":
        cert_criminal = process_cpf_criminal(cnpj_cpf)
        cert_civel = process_cpf_civel(cnpj_cpf)
        cert_eleitoral = process_cpf_eleitoral(cnpj_cpf)
        cert_nada_consta_especial = process_nada_consta_especial(cnpj_cpf, nome_mae)
        cert_receita = process_cpf_receita(cnpj_cpf)
        certidoes = [cert_criminal, cert_civel, cert_eleitoral, cert_nada_consta_especial, cert_receita]
    elif doc_type.upper() == "CNPJ":
        cert_criminal = process_cnpj_criminal(cnpj_cpf)
        cert_civel = process_cnpj_civel(cnpj_cpf)
        cert_eleitoral = process_cnpj_eleitoral(cnpj_cpf)
        certidoes = [cert_criminal, cert_civel, cert_eleitoral]
    else:
        # Se o tipo não for reconhecido, encerra ou lança exceção conforme necessário
        return

    # Exemplo de atualização dos dados no primeiro proprietário associado à análise
    proprietario = db.query(Proprietario).filter(Proprietario.analise_id == analise_id).first()
    if proprietario:
        for cert in certidoes:
            tipo_doc = cert.get("tipo_doc")
            arquivo_url = cert.get("arquivo_url")
            # Atualiza campos diferentes conforme o tipo de certidão
            if tipo_doc == "CRIMINAL":
                proprietario.pdf_tjdf_criminal = arquivo_url
            elif tipo_doc == "CIVEL":
                proprietario.pdf_tjdf_civel = arquivo_url
            elif tipo_doc == "ELEITORAL":
                proprietario.pdf_tjdf_eleitoral = arquivo_url
            elif tipo_doc == "ESPECIAL":
                proprietario.pdf_nada_consta_especial = arquivo_url
            elif tipo_doc == "RECEITA":
                proprietario.pdf_receita = arquivo_url
            # Adicione outras condições conforme a necessidade para outros tipos de certidões

    # Atualiza o status da análise e, opcionalmente, define um link principal
    analise.status = "concluida"
    if certidoes:
        merged_pdf_filename = merge_certidoes_pdfs(certidoes)
        analise.link_pdf = f"http://local.juk.re:8000/files/{merged_pdf_filename}"
        # analise.link_pdf = certidoes[0].get("arquivo_url")
    
    db.commit()

def merge_certidoes_pdfs(certidoes: list) -> str:
    """
    Mescla os PDFs das certidões em um único arquivo.
    Cada dicionário em `certidoes` deve conter a chave "arquivo" com o nome do arquivo PDF gerado.
    Retorna o novo nome do arquivo mesclado.
    """
    merger = PdfMerger()
    for cert in certidoes:
        pdf_filename = cert.get("arquivo")
        if pdf_filename:
            file_path = os.path.join("files", pdf_filename)
            if os.path.exists(file_path):
                merger.append(file_path)
    # Gera um novo nome para o PDF mesclado
    merged_filename = f"{str(uuid.uuid4())}_merged.pdf"
    merged_filepath = os.path.join("files", merged_filename)
    merger.write(merged_filepath)
    merger.close()
    return merged_filename

@router.post("/analises/certidoes/")
def emitir_certidoes_endpoint(
    analise_id: int,
    cnpj_cpf: str,
    nome_mae: str,
    doc_type: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint que inicia a emissão das certidões em background.
    Parâmetros:
      - analise_id: ID da análise cadastrada
      - cnpj_cpf: CPF ou CNPJ a ser processado
      - doc_type: 'CPF' ou 'CNPJ', definindo qual fluxo utilizar
    """
    background_tasks.add_task(process_certidoes, analise_id, cnpj_cpf, nome_mae, doc_type, db)
    return {"message": "Emissão das certidões iniciada em background."}
