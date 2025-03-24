# Acessa a API que tira as certidões do Nada Consta
# post_nada_consta.py
import os
import re
import uuid
import requests
from PyPDF2 import PdfReader

def process_nada_consta_civel(cpf: str, nome_mae: str) -> dict:
    # 1. Requisição à API com CPF e nome da mãe
    api_url = "https://docs.zukcode.com/tjdft/nada_consta/civel"
    response = requests.post(api_url, json={"cpf": cpf, "nome_mae": nome_mae})
    if response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {response.status_code}"}
    
    data = response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # 2. Extrai a URL do PDF na resposta e baixa o arquivo
    certidao_data = data.get("dados", {}).get("certidao", {})
    url_certidao = certidao_data.get("url_certidao")
    if not url_certidao:
        return {"status": "erro", "mensagem": "URL do certificado não encontrada na resposta da API."}
    
    file_response = requests.get(url_certidao)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # Gera um ID único e define o nome do arquivo conforme solicitado
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{cpf}_nada_consta_civel.pdf"
    
    # Cria a pasta "files" se ela não existir
    folder = "files"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, novo_nome_arquivo)
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    
    # 3. Abre o PDF e extrai o texto para identificar pendências e o nome da pessoa
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao extrair texto do PDF: {e}"}
    
    # Se o texto contiver "NADA CONSTA", a pendência é negativa (pendencia = False)
    pendencia = not ("NADA CONSTA" in text.upper())
    
    # Extrai o nome da pessoa: procura o padrão onde o nome está logo após "CPF/CNPJ de:"
    nome = ""
    match = re.search(r"CPF/CNPJ de:\s*\n\s*([^\n]+)", text)
    if match:
        nome = match.group(1).strip()
    
    # Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"https://docx.juk.re/files/{novo_nome_arquivo}",
        "tipo_doc": "CIVEL",
        "texto_doc": text,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_nada_consta_criminal(cpf: str, nome_mae: str) -> dict:
    # 1. Requisição à API com CPF e nome da mãe
    api_url = "https://docs.zukcode.com/tjdft/nada_consta/criminal"
    response = requests.post(api_url, json={"cpf": cpf, "nome_mae": nome_mae})
    if response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {response.status_code}"}
    
    data = response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # 2. Extrai a URL do PDF na resposta e baixa o arquivo
    certidao_data = data.get("dados", {}).get("certidao", {})
    url_certidao = certidao_data.get("url_certidao")
    if not url_certidao:
        return {"status": "erro", "mensagem": "URL do certificado não encontrada na resposta da API."}
    
    file_response = requests.get(url_certidao)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # Gera um ID único e define o nome do arquivo conforme solicitado
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{cpf}_nada_consta_criminal.pdf"
    
    # Cria a pasta "files" se ela não existir
    folder = "files"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, novo_nome_arquivo)
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    
    # 3. Abre o PDF e extrai o texto para identificar pendências e o nome da pessoa
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao extrair texto do PDF: {e}"}
    
    # Se o texto contiver "NADA CONSTA", a pendência é negativa (pendencia = False)
    pendencia = not ("NADA CONSTA" in text.upper())
    
    # Extrai o nome da pessoa: procura o padrão onde o nome está logo após "CPF/CNPJ de:"
    nome = ""
    match = re.search(r"CPF/CNPJ de:\s*\n\s*([^\n]+)", text)
    if match:
        nome = match.group(1).strip()
    
    # Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"https://docx.juk.re/files/{novo_nome_arquivo}",
        "tipo_doc": "CRIMINAL",
        "texto_doc": text,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_nada_consta_falencia(cpf: str, nome_mae: str) -> dict:
    # 1. Requisição à API com CPF e nome da mãe
    api_url = "https://docs.zukcode.com/tjdft/nada_consta/falencia"
    response = requests.post(api_url, json={"cpf": cpf, "nome_mae": nome_mae})
    if response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {response.status_code}"}
    
    data = response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # 2. Extrai a URL do PDF na resposta e baixa o arquivo
    certidao_data = data.get("dados", {}).get("certidao", {})
    url_certidao = certidao_data.get("url_certidao")
    if not url_certidao:
        return {"status": "erro", "mensagem": "URL do certificado não encontrada na resposta da API."}
    
    file_response = requests.get(url_certidao)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # Gera um ID único e define o nome do arquivo conforme solicitado
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{cpf}_nada_consta_falencia.pdf"
    
    # Cria a pasta "files" se ela não existir
    folder = "files"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, novo_nome_arquivo)
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    
    # 3. Abre o PDF e extrai o texto para identificar pendências e o nome da pessoa
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao extrair texto do PDF: {e}"}
    
    # Se o texto contiver "NADA CONSTA", a pendência é negativa (pendencia = False)
    pendencia = not ("NADA CONSTA" in text.upper())
    
    # Extrai o nome da pessoa: procura o padrão onde o nome está logo após "CPF/CNPJ de:"
    nome = ""
    match = re.search(r"CPF/CNPJ de:\s*\n\s*([^\n]+)", text)
    if match:
        nome = match.group(1).strip()
    
    # Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"https://docx.juk.re/files/{novo_nome_arquivo}",
        "tipo_doc": "FALENCIA",
        "texto_doc": text,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_nada_consta_especial(cpf: str, nome_mae: str) -> dict:
    # 1. Requisição à API com CPF e nome da mãe
    api_url = "https://docs.zukcode.com/tjdft/nada_consta/especial"
    response = requests.post(api_url, json={"cpf": cpf, "nome_mae": nome_mae})
    if response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {response.status_code}"}
    
    data = response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # 2. Extrai a URL do PDF na resposta e baixa o arquivo
    certidao_data = data.get("dados", {}).get("certidao", {})
    url_certidao = certidao_data.get("url_certidao")
    if not url_certidao:
        return {"status": "erro", "mensagem": "URL do certificado não encontrada na resposta da API."}
    
    file_response = requests.get(url_certidao)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # Gera um ID único e define o nome do arquivo conforme solicitado
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{cpf}_nada_consta_especial.pdf"
    
    # Cria a pasta "files" se ela não existir
    folder = "files"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, novo_nome_arquivo)
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    
    # 3. Abre o PDF e extrai o texto para identificar pendências e o nome da pessoa
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao extrair texto do PDF: {e}"}
    
    # Se o texto contiver "NADA CONSTA", a pendência é negativa (pendencia = False)
    pendencia = not ("NADA CONSTA" in text.upper())
    
    # Extrai o nome da pessoa: procura o padrão onde o nome está logo após "CPF/CNPJ de:"
    nome = ""
    match = re.search(r"CPF/CNPJ de:\s*\n\s*([^\n]+)", text)
    if match:
        nome = match.group(1).strip()
    
    # Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"https://docx.juk.re/files/{novo_nome_arquivo}",
        "tipo_doc": "ESPECIAL",
        "texto_doc": text,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

# Exemplo de uso:
if __name__ == "__main__":
    cpf_exemplo = "00000000000"
    nome_mae_exemplo = "Juca"
    resultado = process_nada_consta_especial(cpf_exemplo, nome_mae_exemplo)
    print(resultado)
