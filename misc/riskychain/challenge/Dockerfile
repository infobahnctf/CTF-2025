FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY risc-v.c /app/

RUN gcc -o risc-v risc-v.c -lssl -lcrypto

COPY flag.txt /app/

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./risc-v,stderr"]

