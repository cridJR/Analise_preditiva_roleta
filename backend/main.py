from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import json

app = FastAPI(title="Roulette Analysis Engine")

# CORS habilitado para comunicação entre containers
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
async def registrar(giro: Giro):
    dados = mapear_dados(giro.numero)
    r.lpush("historico", json.dumps(dados))
    r.ltrim("historico", 0, 99)
    return {"status": "sucesso"}

@app.get("/historico")
async def get_historico():
    hist = r.lrange("historico", 0, -1)
    return [json.loads(i) for i in hist]

@app.get("/sugestao")
async def get_sugestao():
    hist = await get_historico()
    total = len(hist)
    if total < 12:
        return {"mensagem": f"Amostra pequena ({total}/12)"}
    
    cores = [g['cor'] for g in hist]
    v, p = cores.count("vermelho"), cores.count("preto")
    duzias = [g['duzia'] for g in hist if g['duzia'] != 0]
    colunas = [g['coluna'] for g in hist if g['coluna'] != 0]
    
    sugestoes = []
    # Lógica de Cores (Desvio > 60%)
    if v > (total * 0.6): sugestoes.append("PRETO")
    elif p > (total * 0.6): sugestoes.append("VERMELHO")
    
    # Lógica de Dúzias e Colunas (Quem está "atrasado" < 25%)
    for label, lista, items in [("DÚZIA", duzias, [1,2,3]), ("COLUNA", colunas, [1,2,3])]:
        counts = {item: lista.count(item) for item in items}
        atrasado = min(counts, key=counts.get)
        if counts[atrasado] < (len(lista) / 4):
            sugestoes.append(f"{atrasado}ª {label}")

    return {"v": v, "p": p, "sugestoes": sugestoes if sugestoes else ["AGUARDAR"]}

@app.delete("/limpar-historico")
async def limpar():
    r.delete("historico")
    return {"status": "ok"}