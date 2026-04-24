# Roulette Predictive Analysis System 🎰

Este projeto é um **Agente de Análise Preditiva** baseado em desvio estatístico para jogos de roleta. O sistema utiliza uma arquitetura de microserviços para processar históricos de giros e sugerir probabilidades baseadas em tendências matemáticas, cobrindo não apenas cores, mas todo o layout da mesa (Dúzias, Colunas e Metades).

## 🏗 Arquitetura do Sistema

O sistema opera em uma stack otimizada para baixa latência:

- **Frontend (React + Vite + TS):** Interface responsiva com dashboard de estatísticas em tempo real e entrada de dados intuitiva.
- **Backend (FastAPI):** API REST de alta performance com middleware de CORS e processamento de dados assíncrono.
- **Cache (Redis):** Banco NoSQL em memória que atua como a única fonte de verdade para o histórico circular (limitado aos últimos 100 giros).

## 🛠 Stack Tecnológica

* **Linguagem:** Python 3.10+ / TypeScript
* **Banco de Dados:** Redis (Alpine Image)
* **Infraestrutura:** Docker & Docker Compose
* **Segurança:** CORSMiddleware (Configurado para ambientes Dev/Prod)

## 📡 Endpoints da API

Abaixo, os endpoints disponíveis para integração e monitoramento:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/input` | Registra um número e mapeia cor, paridade, dúzia, coluna e metade. |
| `GET` | `/historico` | Retorna o JSON completo dos últimos giros salvos no Redis. |
| `GET` | `/sugestao` | Motor de análise que sugere a próxima entrada baseada em desvios. |
| `GET` | `/health-redis` | Verificação de integridade (Health Check) da conexão API <-> Redis. |
| `DELETE` | `/limpar-historico` | **Admin:** Comando para expurgar a chave de histórico do Redis. |

## 📊 Inteligência de Dados (Multi-Apostas)

O sistema agora mapeia cada número para 5 dimensões estatísticas:

1.  **Cores:** Vermelho, Preto ou Verde (Zero).
2.  **Paridade:** Par ou Ímpar.
3.  **Dúzias:** 1ª (1-12), 2ª (13-24) ou 3ª (25-36).
4.  **Colunas:** 1ª, 2ª ou 3ª coluna da mesa.
5.  **Metades:** 1-18 (Low) ou 19-36 (High).

> **Lógica de Sugestão:** O algoritmo identifica "vazios" estatísticos. Se uma cor ou setor está com frequência abaixo do desvio padrão esperado para uma amostra de 36 giros, o sistema sinaliza uma oportunidade de correção.

## 🚀 Como Executar

### Pré-requisitos
* Docker e Docker Compose instalados.

### Instalação e Execução
1.  Na pasta raiz do projeto, execute o build dos containers:
    ```bash
    docker-compose up --build -d
    ```
2.  Acesse o Frontend em: `http://localhost:3000`
3.  Acesse a documentação da API (Swagger) em: `http://localhost:8000/docs`

## 📁 Estrutura de Arquivos

```text
.
├── backend/
│   ├── main.py          # Lógica FastAPI e Conexão Redis
│   └── Dockerfile       # Build da imagem Python Slim
├── frontend/
│   ├── src/App.tsx      # Dashboard React e Consumo da API
│   └── Dockerfile       # Build Multi-stage (Node -> Nginx)
└── docker-compose.yaml  # Orquestração dos serviços (Backend, Front, Redis)

