import os
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

# =========================
# CARREGA VARIÁVEIS DE AMBIENTE
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# URL DA API
# =========================
url = "https://maiordonordeste.com.br/api/v1/numeros"

# =========================
# HEADERS PARA EVITAR 403
# =========================
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://maiordonordeste.com.br/",
    "Connection": "keep-alive"
}

try:
    print("===================================")
    print("INICIANDO COLETA")
    print(datetime.now())
    print("===================================")

    # =========================
    # REQUISIÇÃO
    # =========================
    print("Buscando dados no site...")

    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(f"Status Code: {resposta.status_code}")

    resposta.raise_for_status()

    dados = resposta.json()

    # =========================
    # EXTRAINDO DADOS
    # =========================
    total_socios = dados.get("totalSocios")
    socios_pagantes = dados.get("sociosPagantes")
    socios_isentos = dados.get("sociosIsentos")

    print("Dados encontrados:")
    print(f"Total Sócios: {total_socios}")
    print(f"Sócios Pagantes: {socios_pagantes}")
    print(f"Sócios Isentos: {socios_isentos}")

    # =========================
    # CONECTANDO NO POSTGRES
    # =========================
    print("Conectando ao banco...")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # =========================
    # INSERT NO BANCO
    # =========================
    query = """
    INSERT INTO socios_historico (
        total_socios,
        socios_pagantes,
        socios_isentos,
        data_coleta
    )
    VALUES (%s, %s, %s, NOW())
    """

    cursor.execute(
        query,
        (
            total_socios,
            socios_pagantes,
            socios_isentos
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
    print(f"Erro no banco: {db_err}")

except Exception as e:
    print(f"Erro inesperado: {e}")