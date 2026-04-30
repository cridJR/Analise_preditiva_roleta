---

### Por que agora vai funcionar?
1.  **Cercadinhos de Código**: Usei as "crases triplas" (` ```bash `) para que o GitHub crie aquela caixa cinza bonita de comandos.
2.  **Espaçamento**: Adicionei linhas em branco entre os títulos e os parágrafos, o que impede que o texto fique todo "grudado" como apareceu no seu print.
3.  **Links Clicáveis**: As tabelas de acesso agora possuem links funcionais.

Tente atualizar o arquivo com este conteúdo e me diga se o visual no GitHubEntendi perfeitamente, Euclides. O Markdown no GitHub ficou "quebrado" e sem formatação porque faltaram as quebras de linha adequadas e os blocos de código (` ``` `) para o interpretador do GitHub entender o que é texto e o que é comando.

Como SRE, a documentação é tão importante quanto o código. Aqui está o conteúdo do **README.md** devidamente padronizado, com sintaxe corrigida e blocos de código isolados para que o GitHub renderize exatamente como um manual profissional.

Copie o conteúdo abaixo e substitua todo o arquivo atual:

---
```markdown
# 🎰 Projeto Análise Preditiva de Roleta
### Infraestrutura Kubernetes com GitOps & Inteligência Artificial

Este repositório contém a infraestrutura completa para o sistema de predição de roleta, utilizando microsserviços conteinerizados, orquestração com Kubernetes (k3s/k3d) e deploy contínuo via ArgoCD.

---

## 🛠️ 1. Preparação das Imagens (Docker Hub)

As imagens foram construídas e publicadas no namespace `euclidesalgartelecom`. Siga os passos abaixo para atualizar as imagens:

### Build e Push do Backend
```bash
cd backend/
docker build -t euclidesalgartelecom/roulette-backend:v1.0.0 .
docker push euclidesalgartelecom/roulette-backend:v1.0.0
Build e Push do FrontendBashcd ../frontend/
docker build -t euclidesalgartelecom/roulette-frontend:v1.0.0 .
docker push euclidesalgartelecom/roulette-frontend:v1.0.0
🏗️ 2. Provisionamento da InfraestruturaPasso 1: Criação do Cluster Local (k3d)Criação de um cluster resiliente com 7 nós (3 servers e 4 agents):  Bashk3d cluster create k3s-default --servers 3 --agents 4
Passo 2: Instalação e Acesso ao ArgoCDInstalação do motor de GitOps no cluster:  Bash# Criar namespace e instalar
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Obter senha inicial do admin para o primeiro acesso
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
Passo 3: Injeção de Imagens (Contorno de Erro de Rede)Comando essencial para mitigar o erro connection reset em redes corporativas[cite: 2]:Bashdocker pull redis:alpine
k3d image import redis:alpine -c k3s-default
🚀 3. Deploy da Aplicação via GitOpsO ArgoCD monitora a branch feature/ia-intelligence e aplica automaticamente os manifestos da pasta k8s/[cite: 2].Executar o Deploy:Bashkubectl apply -f k8s/roulette-app.yaml
Componentes da Stack:Redis: Banco de dados in-memory para histórico de jogadas[cite: 2].Backend: API FastAPI para processamento de lógica e IA[cite: 2].Frontend: Interface React para visualização de dados[cite: 2].🌐 4. Acesso ao Ambiente (Port-Forward)Como o ambiente é local, utilize os comandos abaixo em background para liberar o acesso no navegador[cite: 2]:Bash# Comando único para liberar todos os acessos
kubectl port-forward svc/argocd-server -n argocd 8080:443 > /dev/null 2>&1 & \
kubectl port-forward svc/roulette-frontend -n roulette-prod 3000:80 > /dev/null 2>&1 & \
kubectl port-forward svc/roulette-backend -n roulette-prod 8000:8000 > /dev/null 2>&1 &
ServiçoURLPainel ArgoCDhttps://localhost:8080App Frontendhttp://localhost:3000Docs Backend (Swagger)http://localhost:8000/docs🧹 5. Manutenção e SREVerificar Logs: kubectl logs -l app=roulette-backend -n roulette-prod[cite: 2].Forçar Sincronização: No ArgoCD, clique em REFRESH e depois em SYNC.Encerrar Redirecionamentos: pkill kubectl.Remover Cluster: k3d cluster delete k3s-default.
---

### Por que agora vai funcionar?
1.  **Cercadinhos de Código**: Usei as "crases triplas" (` ```bash `) para que o GitHub crie aquela caixa cinza bonita de comandos[cite: 2].
2.  **Espaçamento**: Adicionei linhas em branco entre os títulos e os parágrafos, o que impede que o texto fique todo "grudado" como apareceu no seu print[cite: 2].
3.  **Links Clicáveis**: As tabelas de acesso agora possuem links funcionais[cite: 2].

Tente atualizar o arquivo com este conteúdo e me diga se o visual no GitHub ficou conforme o esperado!