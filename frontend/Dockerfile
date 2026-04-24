# Estágio 1: Build
FROM node:18-alpine AS build

WORKDIR /app

# Copia os arquivos de configuração do Node
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o código do frontend e gera a versão de produção
COPY . .
RUN npm run build

# Estágio 2: Serve (Produção com Nginx)
FROM nginx:stable-alpine

# Copia os arquivos gerados no estágio de build para o diretório do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta 80 (padrão web)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]