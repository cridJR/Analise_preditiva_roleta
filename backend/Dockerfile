# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para algumas bibliotecas Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o arquivo de requisitos primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que o FastAPI usa
EXPOSE 8000

# Comando para rodar a aplicação usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]