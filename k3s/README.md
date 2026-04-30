🎰 Projeto Análise Preditiva de RoletaInfraestrutura Kubernetes com GitOps & Inteligência ArtificialEste repositório contém a infraestrutura completa para o sistema de predição de roleta, utilizando microsserviços conteinerizados, orquestração com Kubernetes (k3s/k3d) e deploy contínuo via ArgoCD.  🛠️ 1. Preparação das Imagens (Docker Hub)Antes do deploy no Kubernetes, as imagens foram construídas e enviadas para o Docker Hub sob o namespace euclidesalgartelecom.  Build e Push do BackendBash# Navegar até a pasta do backend
cd backend/

# Construir a imagem (v1.0.0)
docker build -t euclidesalgartelecom/roulette-backend:v1.0.0 .

# Enviar para o Docker Hub
docker push euclidesalgartelecom/roulette-backend:v1.0.0
Build e Push do FrontendBash# Navegar até a pasta do frontend
cd ../frontend/

# Construir a imagem (v1.0.0)
docker build -t euclidesalgartelecom/roulette-frontend:v1.0.0 .

# Enviar para o Docker Hub
docker push euclidesalgartelecom/roulette-frontend:v1.0.0
🏗️ 2. Provisionamento da InfraestruturaPasso 1: Criação do Cluster Local (k3d)Criamos um cluster multi-nó para garantir alta disponibilidade e isolamento de recursos.  Bashk3d cluster create k3s-default --servers 3 --agents 4
Passo 2: Instalação do ArgoCDO ArgoCD é o responsável por sincronizar este repositório com o cluster.  Bash# Criar namespace e instalar
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Obter senha inicial do admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
Passo 3: Injeção de Imagens (Bypass de Rede)Para mitigar erros de conexão corporativa (connection reset), injetamos a imagem do Redis diretamente nos nós.  Bashdocker pull redis:alpine
k3d image import redis:alpine -c k3s-default
🚀 3. Deploy via GitOps (ArgoCD)Para iniciar o deploy, aplicamos o manifesto da Application que monitora a branch feature/ia-intelligence.  Bashkubectl apply -f k8s/roulette-app.yaml
Estrutura de Manifestos (/k8s)redis.yaml: Deployment do Redis com imagePullPolicy: IfNotPresent.  backend.yaml: API FastAPI com variável REDIS_HOST=redis.  frontend.yaml: Interface React exposta na porta 80.  ingress.yaml: Regras de roteamento para o tráfego HTTP.  🌐 4. Acesso ao AmbienteComo o cluster roda isolado, utilizamos o port-forward em background para liberar o acesso local.  Bash# Executar em background para liberar o terminal
kubectl port-forward svc/argocd-server -n argocd 8080:443 > /dev/null 2>&1 &
kubectl port-forward svc/roulette-frontend -n roulette-prod 3000:80 > /dev/null 2>&1 &
kubectl port-forward svc/roulette-backend -n roulette-prod 8000:8000 > /dev/null 2>&1 &
ServiçoURL de AcessoPainel ArgoCDhttps://localhost:8080Aplicação Roletahttp://localhost:3000Documentação APIhttp://localhost:8000/docs🧹 5. Comandos de ManutençãoVerificar saúde dos Pods: kubectl get pods -n roulette-prod.  Forçar Sync do ArgoCD: argocd app sync roulette-analysis-pro.Encerrar redirecionamentos: pkill kubectl.Parar Laboratório: k3d cluster stop k3s-default.