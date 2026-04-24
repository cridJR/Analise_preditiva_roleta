# Roulette Analysis Pro 🎰

Este sistema é uma plataforma de **Análise de Desvio Estatístico** em tempo real para roleta europeia. Utiliza uma arquitetura de microserviços para processar tendências e sugerir entradas baseadas no "atraso" (vazio estatístico) de setores específicos da mesa, como Cores, Dúzias e Colunas.

## 🚀 Novidades desta Versão
- **Multi-Strategy Engine:** Análise simultânea de Cores, Dúzias e Colunas.
- **Balance Tracker:** Visualização em tempo real da quantidade de Vermelhos vs. Pretos no topo do dashboard.
- **Admin Redis Reset:** Botão de limpeza rápida para expurgar o histórico do banco de dados sem reiniciar os contentores.
- **SRE Dashboard:** Interface moderna com TailwindCSS, otimizada para monitorização local.

## 🏗 Arquitetura do Sistema
O projeto é orquestrado via Docker para garantir que o ambiente seja idêntico em qualquer máquina:
- **Frontend:** React + Vite + TypeScript (Porta 3000)
- **Backend:** FastAPI + Uvicorn (Porta 8000)
- **Cache:** Redis Alpine (Porta 6379)

## 📡 Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/input` | Regista um novo número e mapeia cor, paridade, dúzia e coluna. |
| `GET` | `/historico` | Recupera os últimos 100 registos do Redis (Fila Circular). |
| `GET` | `/sugestao` | Motor de cálculo que identifica desvios estatísticos acima do padrão. |
| `DELETE` | `/limpar-historico` | **Admin:** Comando para zerar a base de dados Redis. |

## 📊 Lógica de Análise (Engine)

🚀 Funcionalidades Principais
Multi-Strategy Engine: Análise simultânea de Cores, Dúzias e Colunas.

Análise de Cilindro (Racetrack): Identificação de tendências nos setores Voisins du Zéro, Tiers du Cylindre e Orphelins.

Balance Tracker: Visualização em tempo real da paridade entre Vermelhos e Pretos no topo do dashboard.

Timeline Física: Histórico dinâmico com rotulagem automática dos setores do cilindro para identificação de "assinatura do crupiê".

Admin Redis Reset: Botão integrado na UI para limpeza instantânea da base de dados.

## 🛠 Comandos de Operação

### Subir o Ambiente
```bash
# Constrói as imagens e inicia os serviços em background
docker-compose up --build -d

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

## 📁 Estrutura de Diretórios

A organização do projeto segue as melhores práticas de isolamento de contexto para Docker:

```text
.
├── backend/
│   ├── main.py              # API FastAPI e Lógica de Análise
│   ├── requirements.txt     # Dependências Python (fastapi, redis, uvicorn)
│   └── Dockerfile           # Imagem Python para o backend
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Dashboard React e Trackers de Cores
│   │   └── main.tsx         # Ponto de entrada do React
│   ├── index.html           # Template HTML5
│   ├── package.json         # Scripts e dependências (Vite, Tailwind)
│   └── Dockerfile           # Build multi-stage para o frontend
├── docker-compose.yaml      # Orquestração (Frontend, Backend, Redis)
└── README.md                # Documentação do sistema

