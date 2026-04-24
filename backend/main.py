from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import redis
import json
import os

app = FastAPI(title="Sistema de Análise Preditiva - Local")

# CORS configurado para uso local (permite o React na porta 3000 falar com o Python na 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com o Redis usando variável de ambiente ou default para localhost
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

class Giro(BaseModel):
    numero: int

def mapear_dados(n):
    """Lógica completa de mapeamento conforme o layout oficial da roleta."""
    if n == 0: 
        return {"numero": 0, "cor": "verde", "paridade": "zero", "duzia": 0, "coluna": 0, "metade": "zero"}
    
    vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    coluna = 3 if n % 3 == 0 else (n % 3)
    
    return {
        "numero": n,
        "cor": "vermelho" if n in vermelhos else "preto",
        "paridade": "par" if n % 2 == 0 else "impar",
        "duzia": (n - 1) // 12 + 1,
        "coluna": coluna,
        "metade": "1-18" if n <= 18 else "19-36"
    }

@app.post("/input")
async def registrar_giro(giro: Giro):
    if not 0 <= giro.numero <= 36:
        raise HTTPException(status_code=400, detail="Número inválido")
    dados = mapear_dados(giro.numero)
    # Lpush e Ltrim garantem que a memória nunca cresça indefinidamente
    r.lpush("historico", json.dumps(dados))
    r.ltrim("historico", 0, 99) 
    return {"status": "sucesso", "dados": dados}

@app.get("/historico")
async def consultar_historico():
    historico_raw = r.lrange("historico", 0, -1)
    return [json.loads(item) for item in historico_raw]

@app.get("/sugestao")
async def obter_sugestao():
    historico = await consultar_historico()
    if len(historico) < 10:
        return {"mensagem": "Aguardando amostra mínima (10 giros)..."}
    
    cores = [g['cor'] for g in historico]
    v, p = cores.count("vermelho"), cores.count("preto")
    
    sugestao = "Aguardar"
    if v > (len(cores) * 0.6): sugestao = "Entrar no PRETO"
    elif p > (len(cores) * 0.6): sugestao = "Entrar no VERMELHO"
    
    return {"analise": {"V": v, "P": p}, "sugestao": sugestao}

@app.delete("/limpar-historico")
async def limpar_historico():
    r.delete("historico")
    return {"status": "ok", "mensagem": "Banco Redis resetado"}

@app.get("/health")
async def health():
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except:
        return {"status": "unhealthy", "redis": "disconnected"}, 503