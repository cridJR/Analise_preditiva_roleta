from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import redis

app = FastAPI(title="Sistema de Análise Preditiva - TCC")

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com Redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class Giro(BaseModel):
    numero: int

class LoteGiros(BaseModel):
    numeros: List[int]

# Grupos de Referência (Substituem a antiga mapear_dados com mais eficiência)
VERMELHOS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
COLUNA1 = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
COLUNA2 = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
COLUNA3 = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

def analisar_probabilidades(historico: List[int]):
    if len(historico) < 8:
        return {"sugestoes": ["Aguardar mais dados"], "confianca": "Baixa"}

    v, p, par, imp = 0, 0, 0, 0
    cols = {1: 0, 2: 0, 3: 0}
    duz = {1: 0, 2: 0, 3: 0}

    for n in historico:
        if n == 0: continue
        # Cores
        if n in VERMELHOS: v += 1
        else: p += 1
        # Paridade
        if n % 2 == 0: par += 1
        else: imp += 1
        # Colunas
        if n in COLUNA1: cols[1] += 1
        elif n in COLUNA2: cols[2] += 1
        elif n in COLUNA3: cols[3] += 1
        # Dúzias
        if 1 <= n <= 12: duz[1] += 1
        elif 13 <= n <= 24: duz[2] += 1
        else: duz[3] += 1

    sugestoes = []
    if v >= p + 3: sugestoes.append("PRETO")
    elif p >= v + 3: sugestoes.append("VERMELHO")
    
    if par >= imp + 3: sugestoes.append("ÍMPAR")
    elif imp >= par + 3: sugestoes.append("PAR")
    
    col_atrasada = min(cols, key=cols.get)
    if cols[col_atrasada] < (len(historico) / 4): sugestoes.append(f"COLUNA {col_atrasada}")

    confianca = "Alta" if len(sugestoes) >= 2 else "Média"
    
    return {
        "sugestoes": sugestoes if sugestoes else ["Aguardar"],
        "confianca": confianca
    }

@app.post("/input")
async def registrar_giro(giro: Giro):
    r.lpush("historico", giro.numero)
    r.ltrim("historico", 0, 49)
    return {"status": "sucesso", "numero": giro.numero}

@app.get("/sugestao")
async def obter_sugestao():
    lista = r.lrange("historico", 0, 19)
    return analisar_probabilidades([int(n) for n in lista])

@app.get("/health-redis")
async def health_check():
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis offline: {str(e)}")

# Mantive as outras funções (historico, batch, limpar) idênticas ao original.