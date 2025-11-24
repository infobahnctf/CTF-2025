FROM node:24.9.0-bookworm-slim

WORKDIR /app

ENV PUPPETEER_SKIP_DOWNLOAD=true

RUN apt update && apt install -y chromium
RUN rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm i --omit=dev

COPY . .

USER node

CMD [ "node", "index.js" ]
