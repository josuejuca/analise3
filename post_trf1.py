# Acessa a API que tira as certidões do TJDF (trf1)
# post_tjdf.py
import os
import re
import uuid
import requests

# CNPJ

def process_cnpj_criminal(cnpj: str) -> dict:
    # 1. Requisição à API com o cnpj
    api_url = "https://docs.zukcode.com/tjdf/criminal/cnpj"
    api_response = requests.post(api_url, json={"cnpj": cnpj})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "Não foi possivel emitir a certidão."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "CRIMINAL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_cnpj_civel(cnpj: str) -> dict:
    # 1. Requisição à API com o cnpj
    api_url = "https://docs.zukcode.com/tjdf/civel/cnpj"
    api_response = requests.post(api_url, json={"cnpj": cnpj})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "CIVEL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_cnpj_eleitoral(cnpj: str) -> dict:
    # 1. Requisição à API com o cnpj
    api_url = "https://docs.zukcode.com/tjdf/eleitoral/cnpj"
    api_response = requests.post(api_url, json={"cnpj": cnpj})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "ELEITORAL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

# CPF

def process_cpf_criminal(cpf: str) -> dict:
    # 1. Requisição à API com o CPF
    api_url = "https://docs.zukcode.com/tjdf/criminal"
    api_response = requests.post(api_url, json={"cpf": cpf})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "Não foi possivel emitir a certidão."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "CRIMINAL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_cpf_civel(cpf: str) -> dict:
    # 1. Requisição à API com o CPF
    api_url = "https://docs.zukcode.com/tjdf/civel"
    api_response = requests.post(api_url, json={"cpf": cpf})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "CIVEL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado

def process_cpf_eleitoral(cpf: str) -> dict:
    # 1. Requisição à API com o CPF
    api_url = "https://docs.zukcode.com/tjdf/eleitoral"
    api_response = requests.post(api_url, json={"cpf": cpf})
    if api_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro na requisição: {api_response.status_code}"}
    
    data = api_response.json()
    if data.get("status") != "sucesso":
        return {"status": "erro", "mensagem": "API retornou status não sucesso."}
    
    # Extrai informações da resposta
    arquivo_api = data.get("arquivo")
    texto = data.get("texto", "")
    
    # 2. Download do arquivo PDF
    download_url = f"https://docs.zukcode.com/docs/{arquivo_api}"
    file_response = requests.get(download_url)
    if file_response.status_code != 200:
        return {"status": "erro", "mensagem": f"Erro ao baixar o arquivo: {file_response.status_code}"}
    
    # 3. Gera um ID único e renomeia o arquivo
    unique_id = str(uuid.uuid4())
    novo_nome_arquivo = f"{unique_id}_{arquivo_api}"
    
    # Cria a pasta "files" caso não exista
    pasta = "files"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    caminho_arquivo = os.path.join(pasta, novo_nome_arquivo)
    with open(caminho_arquivo, "wb") as f:
        f.write(file_response.content)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "NÃO CONSTAM" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"\n(.+?)\nOU\n", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "ELEITORAL",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado
