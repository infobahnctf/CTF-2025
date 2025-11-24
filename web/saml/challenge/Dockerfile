FROM node:24-slim

RUN useradd -r  nodeuser

WORKDIR /srv
COPY . .

#RUN rm private.pem
RUN npm install --omit=dev

USER nodeuser

EXPOSE 1337

CMD ["node", "index.js"]

