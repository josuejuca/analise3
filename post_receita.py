# Acessa a API que tira as certidões
# post_receita.py
import os
import re
import uuid
import requests
import PyPDF2


def extrair_texto_pdf(caminho_arquivo):
    texto_extraido = ""
    with open(caminho_arquivo, "rb") as f:
        leitor = PyPDF2.PdfReader(f)
        for pagina in leitor.pages:
            texto_extraido += pagina.extract_text() or ""
    # Substitui caracteres não desejados (ex: non-breaking space \xa0) por espaço comum
    texto_limpo = texto_extraido.replace('\xa0', ' ')
    # Remove espaços extras e tabulações
    texto_limpo = re.sub(r'[ \t]+', ' ', texto_limpo)
    # Remove linhas vazias e ajusta as quebras de linha
    texto_limpo = "\n".join([linha.strip() for linha in texto_limpo.splitlines() if linha.strip()])
    return texto_limpo

def process_cpf_receita(cpf: str) -> dict:
    # 1. Requisição à API com o CPF
    api_url = "https://docs.zukcode.com/receita/cpf"
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

     # Se a API não extraiu o texto, extraímos do PDF baixado
    if not texto:
        texto = extrair_texto_pdf(caminho_arquivo)
    
    # 4. Determina se há pendência
    # Se o texto conter "NÃO CONSTAM" a pendência é False
    pendencia = "não constam" not in texto
    
    # 5. Extrai o nome do texto.
    # Busca o nome que está entre "\n" e "\nOU\n"
    match = re.search(r"Nome:(.+?)\nCPF", texto)
    nome = match.group(1).strip() if match else ""
    
    # 6. Monta o resultado final
    resultado = {
        "status": "finalizado",
        "arquivo": novo_nome_arquivo,
        "arquivo_url": f"http://local.juk.re:8000/files/{novo_nome_arquivo}",
        "tipo_doc": "RECEITA",
        "texto_doc": texto,
        "pendencia": pendencia,
        "nome": nome
    }
    
    return resultado


# Exemplo de uso
# if __name__ == "__main__":
#     cpf_exemplo = "000.000.000-00"
#     resultado = process_cpf_receita(cpf_exemplo)
#     print(resultado)
