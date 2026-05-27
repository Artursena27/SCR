import os
from datetime import datetime

# Importando a biblioteca que camufla o script e resolve o Erro 403
from curl_cffi import requests
import psycopg2
from dotenv import load_dotenv

# =========================
# CARREGA VARIÁVEIS DE AMBIENTE
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL2")

# =========================
# URL DA API E HEADERS
# =========================
url = "https://maiordonordeste.com.br/api/v1/numeros"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://maiordonordeste.com.br/",
}

try:
    print("===================================")
    print("INICIANDO COLETA")
    print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print("===================================")

    print("Buscando dados no site...")

    # O parâmetro impersonate="chrome" engana o firewall
    resposta = requests.get(
        url,
        headers=headers,
        timeout=30,
        impersonate="chrome"
    )

    print(f"Status Code: {resposta.status_code}")
    resposta.raise_for_status()

    dados = resposta.json()

    # =========================
    # EXTRAINDO DADOS (Chaves Corrigidas)
    # =========================
    total_socios = dados.get("socios_ativos")
    socios_pagantes = dados.get("socios_ativos_pagantes")
    
    # Busca os isentos. Se a API não devolver, a variável fica como None.
    socios_isentos = dados.get("socios_ativos_isentos") 

    print("Dados encontrados:")
    print(f"Total Sócios: {total_socios}")
    print(f"Sócios Pagantes: {socios_pagantes}")
    print(f"Sócios Isentos: {socios_isentos}")

    # =========================
    # CONECTANDO NO POSTGRES
    # =========================
    print("\nConectando ao banco de dados...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # =========================
    # INSERT NO BANCO (Tabela Corrigida)
    # =========================
    # Mantivemos apenas total_socios e socios_pagantes para garantir 
    # compatibilidade com a tabela que já funcionava.
    query = """
    INSERT INTO historico_socios (
        total_socios,
        socios_pagantes
    )
    VALUES (%s, %s)
    """

    cursor.execute(
        query,
        (
            total_socios,
            socios_pagantes
        )
    )

    conn.commit()
    print("Dados inseridos com sucesso!")

    # =========================
    # FECHANDO CONEXÃO
    # =========================
    cursor.close()
    conn.close()
    print("Finalizado com sucesso!")

except requests.exceptions.HTTPError as http_err:
    print(f"Erro HTTP: {http_err}")

except requests.exceptions.RequestException as req_err:
    print(f"Erro na requisição: {req_err}")

except psycopg2.Error as db_err:
    print(f"Erro no banco de dados: {db_err}")

except Exception as e:
    print(f"Erro inesperado: {e}")