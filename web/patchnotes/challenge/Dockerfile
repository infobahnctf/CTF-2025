FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm i

FROM deps AS builder
COPY . .
RUN npm run build
RUN apk add --no-cache build-base
COPY readflag.c /
RUN gcc -o /readflag /readflag.c

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /readflag /readflag
COPY flag.txt /flag.txt
RUN chown root:root /readflag && chmod 4755 /readflag
RUN chmod 644 /flag.txt && chown root:root /flag.txt

RUN apk add --no-cache su-exec

COPY docker-entrypoint.sh /usr/local/bin/entry.sh
RUN chmod +x /usr/local/bin/entry.sh

RUN addgroup -S ctf && adduser -S -G ctf -h /home/ctfuser -s /sbin/nologin ctfuser
RUN chown -R ctfuser:ctf /app

USER ctfuser

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/app/data /app/data
COPY --from=deps /app/node_modules ./node_modules
COPY package.json next.config.js ./

USER root

ENTRYPOINT ["/usr/local/bin/entry.sh"]

EXPOSE 3000
CMD ["npm", "run", "start"]
