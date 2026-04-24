from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import redis
import json

app = FastAPI(title="Sistema de Análise Preditiva")

# --- CONFIGURAÇÃO DE CORS ---
# Como SRE, você sabe que em produção o ideal é restringir as origens,
# mas para desenvolvimento/local, usamos o wildcard ou a porta do front.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção na Algar, substitua pela lista 'origins'
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"], # Permite todos os headers (importante para Content-Type)
)

# Conexão com Redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class Giro(BaseModel):
    numero: int

class LoteGiros(BaseModel):
    numeros: List[int]

def mapear_dados(n):
    """Mapeia as propriedades estatísticas do número."""
    if n == 0: return {"cor": "verde", "paridade": "zero", "duzia": 0}
    vermelhos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    cor = "vermelho" if n in vermelhos else "preto"
    paridade = "par" if n % 2 == 0 else "impar"
    duzia = (n - 1) // 12 + 1
    return {"cor": cor, "paridade": paridade, "duzia": duzia}

# --- ROTA 1: ENTRADA INDIVIDUAL ---
@app.post("/input")
async def registrar_individual(giro: Giro):
    """Para inserir um número por vez em tempo real."""
    if not 0 <= giro.numero <= 36:
        raise HTTPException(status_code=400, detail="Número inválido (0-36)")
    
    dados = mapear_dados(giro.numero)
    dados['numero'] = giro.numero
    
    # Adiciona ao início da lista e limita a 100 registos
    r.lpush("historico", json.dumps(dados))
    r.ltrim("historico", 0, 99)
    return {"status": "Número registado", "dados": dados}

# --- ROTA 2: ENTRADA EM LOTE (BATCH) ---
@app.post("/input-batch")
async def registrar_lote(lote: LoteGiros):
    """Para inserir uma lista de números de uma só vez."""
    processados = 0
    # Invertemos a lista para que o último número do lote seja o mais recente no Redis
    for num in reversed(lote.numeros):
        if 0 <= num <= 36:
            dados = mapear_dados(num)
            dados['numero'] = num
            r.lpush("historico", json.dumps(dados))
            processados += 1
    
    r.ltrim("historico", 0, 99)
    return {"status": "Lote processado", "quantidade": processados}

@app.get("/historico")
async def consultar_historico():
    """Consulta os últimos números inseridos."""
    historico = r.lrange("historico", 0, -1)
    return [json.loads(item) for item in historico]

@app.get("/sugestao")
async def obter_sugestao():
    """Analisa os dados para sugerir a próxima jogada."""
    historico = await consultar_historico()
    if len(historico) < 10:
        return {"mensagem": "Amostra insuficiente (mínimo 10 giros)"}
    
    # Contagem de cores para exemplo de lógica preditiva
    cores = [g['cor'] for g in historico]
    v = cores.count("vermelho")
    p = cores.count("preto")
    
    # Lógica simples de desvio: sugere a cor que saiu menos
    sugestao = "Aguardar"
    if v > (len(cores) * 0.6): sugestao = "Entrar no PRETO"
    elif p > (len(cores) * 0.6): sugestao = "Entrar no VERMELHO"
    
    return {"analise": {"V": v, "P": p}, "sugestao": sugestao}

# --- ROTA DE ADMINISTRAÇÃO: LIMPEZA ---
@app.delete("/limpar-historico")
async def limpar_historico():
    """
    Remove todos os dados da chave 'historico' no Redis.
    Útil para resetar a análise sem precisar reiniciar os containers.
    """
    try:
        # O comando delete retorna o número de chaves removidas (1 ou 0)
        resultado = r.delete("historico")
        
        if resultado:
            return {"status": "sucesso", "mensagem": "Histórico limpo com sucesso."}
        else:
            return {"status": "vazio", "mensagem": "O histórico já estava vazio."}
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao tentar limpar o Redis: {str(e)}"
        )

# --- ROTA DE HEALTH CHECK ---
@app.get("/health-redis")
async def health_check():
    """Verifica a integridade da API e a conexão com o Redis."""
    try:
        # O método ping() retorna True se o Redis responder
        redis_status = r.ping()
        if not redis_status:
            raise Exception("Redis ping failed")
        
        return {
            "status": "healthy",
            "components": {
                "api": "online",
                "redis": "connected"
            }
        }
    except Exception as e:
        # Retorna 503 (Service Unavailable) se o Redis estiver fora
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "unhealthy",
                "components": {
                    "api": "online",
                    "redis": f"offline: {str(e)}"
                }
            }
        )