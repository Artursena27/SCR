import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# O GitHub vai injetar essa variável de forma segura
# Ele tenta pegar a senha do GitHub. Se não encontrar (porque está no seu PC), ele usa a string direta.
URL_DO_BANCO = os.environ.get("DATABASE_URL")

# 1. EXTRAÇÃO DOS DADOS
url_api = "https://maiordonordeste.com.br/api/v1/numeros"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Buscando dados no site...")
resposta = requests.get(url_api, headers=headers)
resposta.raise_for_status()
dados = resposta.json()

total = dados.get('socios_ativos')
pagantes = dados.get('socios_ativos_pagantes')

print(f"Total coletado: {total} | Pagantes: {pagantes}")

# 2. SALVANDO NO BANCO DE DADOS
print(os.environ.get("DATABASE_URL"))

try:
    print("\nConectando ao banco de dados na nuvem...")
    conexao = psycopg2.connect(URL_DO_BANCO)
    cursor = conexao.cursor()

    comando_insert = """
        INSERT INTO historico_socios (total_socios, socios_pagantes)
        VALUES (%s, %s);
    """
    
    cursor.execute(comando_insert, (total, pagantes))
    conexao.commit()
    print(f"SUCESSO! Dados salvos no Supabase às {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    print(f"Ops! Erro ao salvar no banco: {e}")

finally:
    if 'conexao' in locals() and conexao:
        cursor.close()
        conexao.close()
        print("Conexão com o banco encerrada.")