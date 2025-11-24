FROM node:23-bookworm-slim

RUN apt update && apt install -y chromium xvfb
RUN rm -rf /var/lib/apt/lists/*

RUN groupadd -r pptruser \
    && useradd -r -g pptruser -G audio,video pptruser \
    && mkdir -p /home/pptruser/Downloads \
    && chown -R pptruser:pptruser /home/pptruser

WORKDIR /app
COPY package.json package-lock.json ./
ENV PUPPETEER_SKIP_DOWNLOAD=true
RUN npm install --omit=dev
COPY . .

USER pptruser

CMD xvfb-run --auto-servernum node index.js
