FROM node:16-alpine
WORKDIR /app/frontend
# ENV PATH /app/frontend/node_modules/.bin:$PATH
COPY package.json ./
COPY package-lock.json ./
RUN npm install -g npm@9.1.2
RUN npm install --save --legacy-peer-deps
COPY . ./