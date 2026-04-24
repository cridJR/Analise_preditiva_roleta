# Roulette Predictive Analysis System 🎰

Este projeto é um **Agente de Análise Preditiva** baseado em desvio estatístico para jogos de roleta. Desenvolvido como prova de conceito para fins acadêmicos, o sistema utiliza uma arquitetura moderna de microserviços para processar históricos de giros e sugerir probabilidades baseadas em tendências matemáticas e na Lei dos Grandes Números.

## 🏗 Arquitetura do Sistema

O sistema segue o padrão de design **Observer-Analyzer**, onde a ingestão de dados é separada da lógica de processamento estatístico.

- **Camada de Ingestão (FastAPI):** Uma API REST de alta performance que recebe os dados dos giros.
- **Camada de Armazenamento (Redis):** Um banco de dados em memória (NoSQL) utilizado para garantir latência próxima de zero no processamento das sequências.
- **Motor de Análise:** Algoritmos que calculam o desvio padrão e a frequência de cores, dúzias e paridade em tempo real.

## 🛠 Stack Tecnológica

* **Linguagem:** Python 3.9+
* **Framework Web:** FastAPI (com documentação automática via Swagger UI)
* **Banco de Dados:** Redis (In-memory Data Structure Store)
* **Infraestrutura:** Docker e Docker Compose
* **Validação de Dados:** Pydantic

## 🚀 Como Executar

### Pré-requisitos
* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Instalação e Execução
1.  Clone este repositório.
2.  No terminal, dentro da pasta do projeto, execute:
    ```bash
    docker-compose up -d --build
    ```
3.  O sistema estará disponível em:
    * **API Principal:** `http://localhost:8000`
    * **Documentação Interativa (Swagger):** `http://localhost:8000/docs`

## 📡 Endpoints da API

Abaixo, os principais comandos para interagir com o sistema:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/input` | Insere um novo número individualmente. |
| `POST` | `/input-batch` | Insere uma lista (array) de números para popular o histórico. |
| `GET` | `/sugestao` | Retorna a predição probabilística para a próxima rodada. |
| `GET` | `/historico` | Lista os últimos giros registrados com suas propriedades. |
| `GET` | `/conferir` | Retorna métricas de integridade do banco de dados Redis. |

## 📊 Lógica Preditiva (Resumo Acadêmico)

O motor de análise foca no **Desvio de Tendência**. Se em uma amostra de 50 giros a cor "Vermelha" apareceu apenas 20% das vezes (sendo que a probabilidade teórica é de ~48.6%), o sistema identifica um desvio e aumenta o grau de confiança para a cor oposta na próxima sugestão.

1.  **Frequência de Curto Prazo:** Analisa os últimos 12 giros (um ciclo de dúzias).
2.  **Frequência de Médio Prazo:** Analisa os últimos 36 giros (um ciclo completo da roleta).
3.  **Sugestão:** O sistema indica Cor, Paridade (Ímpar/Par) e Dúzia com maior probabilidade de correção estatística.

## 📁 Estrutura de Arquivos

```text
.
├── src/
│   ├── main.py          # Código fonte da API e Lógica de Análise
│   └── requirements.txt # Dependências do Python
├── Dockerfile           # Definição da imagem da aplicação
├── docker-compose.yml   # Orquestração entre App e Redis
└── README.md            # Documentação do projeto