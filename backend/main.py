from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pandas as pd
import os
import redis
import json
import joblib

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

# Caminho do Modelo de IA (Mapeado via Volume Docker)
MODEL_PATH = "intelligence/trained_model.pkl"
DATASET_PATH = "intelligence/roulette_dataset.csv"

class Giro(BaseModel):
    numero: int

def mapear_dados(n: int):
    """Mapeia propriedades matemáticas e físicas (Cilindro) do número."""
    voisins = [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25]
    tiers = [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
    orphelins = [1, 20, 14, 31, 9, 17, 34, 6]
    
    if n == 0:
        return {
            "numero": 0, "cor": "verde", "paridade": "zero", 
            "duzia": 0, "coluna": 0, "setor": "Voisins"
        }
    
    vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    setor = "Voisins" if n in voisins else ("Tiers" if n in tiers else "Orphelins")
    
    return {
        "numero": n,
        "cor": "vermelho" if n in vermelhos else "preto",
        "paridade": "par" if n % 2 == 0 else "impar",
        "duzia": (n - 1) // 12 + 1,
        "coluna": 3 if n % 3 == 0 else (n % 3),
        "setor": setor
    }

def coletar_dados_ia(dados_mapeados):
    """Persiste dados em CSV para treinamento futuro."""
    try:
        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
        dados_ia = dados_mapeados.copy()
        dados_ia['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.DataFrame([dados_ia])
        header = not os.path.exists(DATASET_PATH)
        df.to_csv(DATASET_PATH, mode='a', index=False, header=header)
    except Exception as e:
        print(f"Erro ao persistir dados para IA: {e}")

@app.post("/input")
async def registrar_giro(giro: Giro):
    if not 0 <= giro.numero <= 36:
        raise HTTPException(status_code=400, detail="Número inválido")
    
    dados = mapear_dados(giro.numero)
    r.lpush("historico", json.dumps(dados))
    r.ltrim("historico", 0, 99)
    coletar_dados_ia(dados)
    return {"status": "sucesso", "dados": dados}

@app.get("/historico")
async def consultar_historico():
    historico_raw = r.lrange("historico", 0, -1)
    return [json.loads(item) for item in historico_raw]

@app.get("/sugestao")
async def obter_sugestao():
    hist = await consultar_historico()
    total = len(hist)
    
    if total < 12:
        return {"mensagem": f"Amostra insuficiente ({total}/12)", "v": 0, "p": 0, "sugestoes": []}
    
    sugestoes = []
    
    # --- CÁLCULO DE CORES (Obrigatório para o retorno) ---
    cores = [g['cor'] for g in hist]
    v = cores.count("vermelho")
    p = cores.count("preto")

    # --- INFERÊNCIA DE IA ---
    if os.path.exists(MODEL_PATH):
        try:
            data = joblib.load(MODEL_PATH)
            model = data['model']
            le_setor = data['le_setor']
            le_cor = data['le_cor']
            
            ultimo = hist[0]
            
            # Sincronizado com as 4 colunas do train_ia.py: 
            # [setor_encoded, cor_encoded, duzia, coluna]
            setor_num = le_setor.transform([ultimo['setor']])[0]
            cor_num = le_cor.transform([ultimo['cor']])[0]
            
            X_input = [[setor_num, cor_num, ultimo['duzia'], ultimo['coluna']]]
            
            pred_num = model.predict(X_input)
            setor_predito = le_setor.inverse_transform(pred_num)[0]
            
            sugestoes.append(f"🤖 IA PREVÊ: {setor_predito.upper()}")
        except Exception as e:
            print(f"Erro na inferência da IA: {e}")

    # --- LÓGICA MATEMÁTICA ---
    if v > (total * 0.6): sugestoes.append("PRETO (DESVIO COR)")
    elif p > (total * 0.6): sugestoes.append("VERMELHO (DESVIO COR)")

    return {
        "v": v, 
        "p": p, 
        "sugestoes": sugestoes if sugestoes else ["AGUARDAR DESVIO"]
    }

@app.delete("/limpar-historico")
async def limpar_historico():
    r.delete("historico")
    return {"status": "sucesso", "mensagem": "Histórico removido"}