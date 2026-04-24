from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import redis
import json

app = FastAPI(title="Analytica Pro - SRE Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class Giro(BaseModel):
    numero: int

def mapear_dados(n):
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
async def registrar_individual(giro: Giro):
    if not 0 <= giro.numero <= 36:
        raise HTTPException(status_code=400, detail="Número inválido")
    dados = mapear_dados(giro.numero)
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
    total = len(historico)
    if total < 12:
        return {"mensagem": f"Aguardando amostra (Mínimo 12, atual: {total})"}
    
    # Contadores
    cores = [g['cor'] for g in historico]
    duzias = [g['duzia'] for g in historico if g['duzia'] != 0]
    colunas = [g['coluna'] for g in historico if g['coluna'] != 0]
    paridades = [g['paridade'] for g in historico if g['paridade'] != "zero"]

    sugestoes = []

    # Lógica de Cores
    v = cores.count("vermelho")
    p = cores.count("preto")
    if v > (total * 0.6): sugestoes.append("PRETO (Cor)")
    elif p > (total * 0.6): sugestoes.append("VERMELHO (Cor)")

    # Lógica de Dúzias (Sugere a que menos saiu)
    count_d = {d: duzias.count(d) for d in [1, 2, 3]}
    duzia_atrasada = min(count_d, key=count_d.get)
    if count_d[duzia_atrasada] < (len(duzias) / 4): # Se saiu menos que 25%
        sugestoes.append(f"{duzia_atrasada}ª DÚZIA")

    # Lógica de Colunas
    count_c = {c: colunas.count(c) for c in [1, 2, 3]}
    coluna_atrasada = min(count_c, key=count_c.get)
    if count_c[coluna_atrasada] < (len(colunas) / 4):
        sugestoes.append(f"{coluna_atrasada}ª COLUNA")

    # Lógica Par/Impar
    par = paridades.count("par")
    impar = paridades.count("impar")
    if par > (len(paridades) * 0.6): sugestoes.append("ÍMPAR")
    elif impar > (len(paridades) * 0.6): sugestoes.append("PAR")

    return {
        "v": v, "p": p,
        "analise_duzias": count_d,
        "analise_colunas": count_c,
        "sugestoes": sugestoes if sugestoes else ["Aguardar melhor desvio"]
    }

@app.delete("/limpar-historico")
async def limpar_historico():
    r.delete("historico")
    return {"status": "sucesso"}