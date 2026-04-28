import requests
import time

# Lista de 200 números para carga massiva
numeros = [30, 28, 0, 11, 13, 36, 22, 10, 25, 22, 16, 13, 27, 13, 11, 26, 17, 0, 35, 2, 16, 0, 3, 13, 12, 3, 8, 17, 23, 33, 30, 8, 20, 16, 27, 30, 24, 25, 19, 18, 25, 8, 34, 17, 12, 24, 28, 26, 36, 36, 0, 36, 11, 17, 23, 23, 24, 17, 31, 2, 24, 9, 21, 30, 12, 3, 25, 3, 36, 23, 29, 13, 8, 17, 4, 19, 22, 3, 30, 16, 34, 24, 13, 28, 23, 5, 15, 28, 17, 16, 22, 28, 31, 3, 36, 16, 25, 19, 22, 7, 3, 16, 17, 2, 16, 9, 5, 28, 14, 8, 1, 28, 32, 33, 12, 14, 33, 1, 21, 11, 15, 8, 1, 28, 25, 3, 30, 34, 31, 31, 17, 24, 2, 26, 5, 20, 21, 22, 31, 1, 19, 16, 35, 12, 26, 13, 10, 30, 35, 29, 10, 3, 14, 23, 29, 12, 27, 21, 27, 2, 29, 5, 13, 1, 26, 29, 34, 12, 29, 31, 2, 30, 22, 6, 0, 4, 18, 35, 25, 18, 19, 25, 4, 9, 26, 15, 10, 29, 25, 36, 31, 15, 19, 16, 22, 29, 13, 12, 4, 17]

URL = "http://localhost:8000/input"

print(f"🚀 Iniciando carga massiva de {len(numeros)} giros...")

for i, n in enumerate(numeros):
    try:
        requests.post(URL, json={"numero": n}, timeout=2)
        if i % 10 == 0:
            print(f"✅ Processados: {i}/{len(numeros)}")
        time.sleep(0.02) # Pequeno delay para não dar flood no Redis
    except Exception as e:
        print(f"❌ Erro no envio: {e}")

print("🏁 Carga finalizada!")