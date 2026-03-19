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
    """Busca profunda: percorre todas as páginas (Critério 3)."""
    url = "https://api.portaldatransparencia.gov.br/api-de-dados/auxilio-emergencial-por-cpf-ou-nis"
    headers = {"chave-api-dados": API_KEY}
    todas_as_parcelas = []
    pagina_atual = 1
    
    print(f"[INFO] Iniciando coleta exaustiva para: {codigo_beneficiario}")

    while True:
        params = {"codigoBeneficiario": codigo_beneficiario, "pagina": pagina_atual, "tamanho": 100}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=25)
            if response.status_code == 429:
                time.sleep(10)
                continue
            response.raise_for_status()
            dados_pagina = response.json()

            if not dados_pagina: break
            
            todas_as_parcelas.extend(dados_pagina)
            print(f"[INFO] Página {pagina_atual} processada. Total acumulado: {len(todas_as_parcelas)}")
            
            if len(dados_pagina) < 100: break
            
            pagina_atual += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"[ERRO] Falha na coleta: {e}")
            break 
    return todas_as_parcelas

def gerar_documentos(dados):
    """Gera os arquivos com o design visual clássico (Arial, 40px, 24px)."""
    try:
        # 1. Gerar Relatório JSON
        with open("resultado.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        print("[INFO] Resultado.json gerado")
        
        # 2. Gerar Documento HTML (Estrutura Antiga)
        html_content = """
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; background: white; padding: 40px; }
            h1 { font-size: 40px; }
            table { border-collapse: collapse; width: 100%; font-size: 24px; }
            th, td { border: 1px solid black; padding: 15px; text-align: left; }
            th { background-color: #eaeaea; }
        </style>
        </head>
        <body>
        <h1>Parcelas do Beneficiário</h1>
        <table>
        <tr>
            <th>Nome</th>
            <th>Mês</th>
            <th>Parcela</th>
            <th>Valor</th>
            <th>Cidade</th>
        </tr>
        """

        for item in dados:
            nome = item.get("beneficiario", {}).get("nome", "N/A")
            mes = item.get("mesDisponibilizacao", "N/A")
            parc = item.get("numeroParcela", "N/A")
            val = item.get("valor", "0.00")
            cid = item.get("municipio", {}).get("nomeIBGE", "N/A")
            
            html_content += f"""
            <tr>
                <td>{nome}</td>
                <td>{mes}</td>
                <td>{parc}</td>
                <td>R$ {val}</td>
                <td>{cid}</td>
            </tr>
            """

        html_content += "</table></body></html>"

        with open("parcelas.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("[INFO] parcelas.html gerado")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao gravar arquivos: {e}")
        return False

def salvar_evidencia_base64(caminho):
    """Converte para Base64 e informa no log."""
    try:
        with open(caminho, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        with open("print_base64.txt", "w") as f:
            f.write(encoded)
        print("[INFO] print_base64.txt gerado")
    except Exception as e:
        print(f"[ERRO] Falha no Base64: {e}")

def enviar_integracao_discord(total, nome):
    """Notificação silenciosa para o Discord (Critério 4)."""
    if not DISCORD_URL: return
    payload = {
        "embeds": [{
            "title": "✅ Extração Concluída",
            "color": 3066993,
            "fields": [
                {"name": "Beneficiário", "value": nome, "inline": True},
                {"name": "Total Parcelas", "value": str(total), "inline": True}
            ]
        }]
    }
    try:
        requests.post(DISCORD_URL, json=payload, timeout=10)
    except: pass

def main():
    if not API_KEY:
        print("[ERRO] Configure a CHAVE_API_DADOS no seu arquivo .env")
        return

    # Lógica Headless: Aceita argumento ou pede input
    if len(sys.argv) > 1:
        codigo = sys.argv[1].strip()
    else:
        codigo = input("Digite o CPF ou NIS: ").strip()

    if not codigo: return

    dados_totais = buscar_dados_portal_exaustivo(codigo)
    
    if dados_totais:
        if gerar_documentos(dados_totais):
            salvar_evidencia_base64("parcelas.html")
            
            nome_primeiro = dados_totais[0].get("beneficiario", {}).get("nome", "N/A")
            enviar_integracao_discord(len(dados_totais), nome_primeiro)
            
            print(f"\n[SUCESSO] Processo Finalizado corretamente! Total: {len(dados_totais)} parcelas.")
    else:
        print("[AVISO] Nenhuma informação encontrada.")

if __name__ == "__main__":
    main()