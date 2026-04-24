from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import redis
import json
import os

app = FastAPI(title="Roulette Analysis Engine - Pro SRE")

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONEXÃO REDIS ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

class Giro(BaseModel):
    numero: int

def mapear_dados(n: int):
    """Mapeia propriedades matemáticas e físicas (Cilindro) do número."""
    # Definição de Setores Físicos (Racetrack)
    voisins = [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25]
    tiers = [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
    orphelins = [1, 20, 14, 31, 9, 17, 34, 6]
    
    if n == 0:
        return {
            "numero": 0, "cor": "verde", "paridade": "zero", 
            "duzia": 0, "coluna": 0, "setor": "Voisins"
        }
    
    vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    
    # Determinação do Setor
    setor = "Voisins" if n in voisins else ("Tiers" if n in tiers else "Orphelins")
    
    return {
        "numero": n,
        "cor": "vermelho" if n in vermelhos else "preto",
        "paridade": "par" if n % 2 == 0 else "impar",
        "duzia": (n - 1) // 12 + 1,
        "coluna": 3 if n % 3 == 0 else (n % 3),
        "setor": setor
    }

# --- ROTAS DA API ---

@app.post("/input")
async def registrar_giro(giro: Giro):
    """Regista o número e mantém o histórico circular no Redis."""
    if not 0 <= giro.numero <= 36:
        raise HTTPException(status_code=400, detail="Número inválido (0-36)")
    
    dados = mapear_dados(giro.numero)
    r.lpush("historico", json.dumps(dados))
    r.ltrim("historico", 0, 99) # Mantém apenas os últimos 100
    return {"status": "sucesso", "dados": dados}

@app.get("/historico")
async def consultar_historico():
    """Retorna a lista de giros formatada."""
    historico_raw = r.lrange("historico", 0, -1)
    return [json.loads(item) for item in historico_raw]

@app.get("/sugestao")
async def obter_sugestao():
    """Analisa desvios estatísticos e tendências físicas do cilindro."""
    hist = await consultar_historico()
    total = len(hist)
    
    if total < 12:
        return {"mensagem": f"Amostra insuficiente ({total}/12)"}
    
    sugestoes = []
    
    # 1. Análise de Cores (Desvio > 60%)
    cores = [g['cor'] for g in hist]
    v, p = cores.count("vermelho"), cores.count("preto")
    if v > (total * 0.6): sugestoes.append("PRETO (Desvio Cor)")
    elif p > (total * 0.6): sugestoes.append("VERMELHO (Desvio Cor)")
    
    # 2. Análise de Dúzias e Colunas (Atraso < 25%)
    duzias = [g['duzia'] for g in hist if g['duzia'] != 0]
    colunas = [g['coluna'] for g in hist if g['coluna'] != 0]
    
    for label, lista, items in [("DÚZIA", duzias, [1,2,3]), ("COLUNA", colunas, [1,2,3])]:
        if not lista: continue
        counts = {item: lista.count(item) for item in items}
        atrasado = min(counts, key=counts.get)
        if counts[atrasado] < (len(lista) / 4):
            sugestoes.append(f"{atrasado}ª {label}")

    # 3. Análise de Setores do Cilindro (Tendência Física > 45%)
    setores = [g['setor'] for g in hist]
    for s_nome in ["Voisins", "Tiers", "Orphelins"]:
        if setores.count(s_nome) > (total * 0.45):
            sugestoes.append(f"SETOR {s_nome.upper()} (Tendência)")

    return {
        "v": v, 
        "p": p, 
        "sugestoes": sugestoes if sugestoes else ["AGUARDAR DESVIO"]
    }

@app.delete("/limpar-historico")
async def limpar_historico():
    """Remove a chave do histórico no Redis."""
    r.delete("historico")
    return {"status": "sucesso", "mensagem": "Histórico removido"}

@app.get("/health")
async def health_check():
    """Verifica conexão com o Redis."""
    try:
        r.ping()
        return {"status": "online", "redis": "connected"}
    except:
        raise HTTPException(status_code=503, detail="Redis offline")