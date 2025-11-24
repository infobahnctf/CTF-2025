FROM oven/bun:latest

RUN apt-get update && apt-get install -y --no-install-recommends php-cli chromium ca-certificates fonts-liberation && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app /app
RUN chmod +x /app/run.sh

ENV NODE_ENV=production PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN bun add puppeteer

EXPOSE 1337
ENTRYPOINT ["/app/run.sh"]
