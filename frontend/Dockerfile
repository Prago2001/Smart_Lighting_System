FROM node:16-buster-slim

WORKDIR /app/frontend

COPY package.json /app/frontend/
RUN npm install --save --legacy-peer-deps
COPY . /app/frontend/
# EXPOSE 3000
# CMD ["npm", "start"]
