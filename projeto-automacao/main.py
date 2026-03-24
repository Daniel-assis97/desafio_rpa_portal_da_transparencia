import requests
import json
import base64
import os
import time
import sys
from dotenv import load_dotenv

# =========================
# CONFIGURAÇÕES E SEGURANÇA
# =========================
load_dotenv()
API_KEY = os.getenv("CHAVE_API_DADOS")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def buscar_dados_portal_exaustivo(codigo_beneficiario):
    """Busca profunda: percorre todas as páginas para um código específico."""
    url = "https://api.portaldatransparencia.gov.br/api-de-dados/auxilio-emergencial-por-cpf-ou-nis"
    headers = {"chave-api-dados": API_KEY}
    todas_as_parcelas = []
    pagina_atual = 1
    
    print(f"\n[INFO] >>> Iniciando coleta para: {codigo_beneficiario}")

    while True:
        params = {"codigoBeneficiario": codigo_beneficiario, "pagina": pagina_atual, "tamanho": 100}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=25)
            
            if response.status_code == 429:
                print(f"[AVISO] Rate Limit atingido para {codigo_beneficiario}. Aguardando 10s...")
                time.sleep(10)
                continue
                
            response.raise_for_status()
            dados_pagina = response.json()

            if not dados_pagina: 
                break
            
            todas_as_parcelas.extend(dados_pagina)
            print(f"[INFO] [{codigo_beneficiario}] Página {pagina_atual} processada. Total: {len(todas_as_parcelas)}")
            
            if len(dados_pagina) < 100: 
                break
            
            pagina_atual += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"[ERRO] [{codigo_beneficiario}] Falha na coleta: {e}")
            break 
            
    return todas_as_parcelas

def gerar_documentos(dados, codigo):
    """Gera arquivos únicos para cada NIS para evitar sobreposição."""
    try:
        nome_json = f"resultado_{codigo}.json"
        nome_html = f"parcelas_{codigo}.html"

        with open(nome_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        
        html_content = f"""
        <html>
        <head><meta charset="utf-8"><style>
            body {{ font-family: Arial; padding: 40px; }}
            h1 {{ font-size: 40px; }}
            table {{ border-collapse: collapse; width: 100%; font-size: 24px; }}
            th, td {{ border: 1px solid black; padding: 15px; }}
            th {{ background-color: #eaeaea; }}
        </style></head>
        <body>
        <h1>Parcelas do Beneficiário - {codigo}</h1>
        <table>
        <tr><th>Nome</th>
        <th>Mês</th>
        <th>Parcela</th>
        <th>Valor</th>
        <th>Cidade</th></tr>
        """

        for item in dados:
            nome = item.get("beneficiario", {}).get("nome", "N/A")
            mes = item.get("mesDisponibilizacao", "N/A")
            parc = item.get("numeroParcela", "N/A")
            val = item.get("valor", "0.00")
            cid = item.get("municipio", {}).get("nomeIBGE", "N/A")
            html_content += f"<tr><td>{nome}</td><td>{mes}</td><td>{parc}</td><td>R$ {val}</td><td>{cid}</td></tr>"

        html_content += "</table></body></html>"

        with open(nome_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        return nome_html
    except Exception as e:
        print(f"[ERRO] Falha ao gerar arquivos para {codigo}: {e}")
        return None

def salvar_evidencia_base64(caminho, codigo):
    try:
        with open(caminho, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        with open(f"print_base64_{codigo}.txt", "w") as f:
            f.write(encoded)
    except: pass

def enviar_integracao_discord(total, nome, codigo):
    if not DISCORD_URL: return
    payload = {
        "embeds": [{
            "title": "✅ Extração Concluída",
            "color": 3066993,
            "fields": [
                {"name": "Beneficiário", "value": nome, "inline": True},
                {"name": "NIS/CPF", "value": codigo, "inline": True},
                {"name": "Total Parcelas", "value": str(total), "inline": True}
            ]
        }]
    }
    try: requests.post(DISCORD_URL, json=payload, timeout=10)
    except: pass

def processar_codigo(codigo):
    """Encapsula o fluxo completo para um único código."""
    dados_totais = buscar_dados_portal_exaustivo(codigo)
    
    if dados_totais:
        arquivo_html = gerar_documentos(dados_totais, codigo)
        if arquivo_html:
            salvar_evidencia_base64(arquivo_html, codigo)
            nome_primeiro = dados_totais[0].get("beneficiario", {}).get("nome", "N/A")
            enviar_integracao_discord(len(dados_totais), nome_primeiro, codigo)
            print(f"[SUCESSO] [{codigo}] Processado com sucesso!")
    else:
        print(f"[AVISO] [{codigo}] Nenhum dado encontrado.")

def main():
    if not API_KEY:
        print("[ERRO] Configure a CHAVE_API_DADOS no seu arquivo .env")
        return

    # Captura os códigos: ou via terminal (argumentos) ou via input (separados por vírgula)
    if len(sys.argv) > 1:
        codigos = sys.argv[1:] 
    else:
        entrada = input("Digite os NIS/CPFs separados por vírgula ou espaço: ").replace(",", " ")
        codigos = entrada.split()

    if not codigos:
        print("[ERRO] Nenhum código informado.")
        return

    print(f"[INFO] Total de códigos para processar: {len(codigos)}")
    
    for c in codigos:
        processar_codigo(c.strip())
        time.sleep(1) # Pausa entre os beneficiários diferentes

if __name__ == "__main__":
    main()
