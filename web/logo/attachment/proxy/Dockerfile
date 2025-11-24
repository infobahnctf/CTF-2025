FROM debian:bookworm-slim AS builder

RUN apt update && apt install curl xz-utils build-essential libssl-dev -y
RUN rm -rf /var/lib/apt/lists/*
RUN curl -fsS https://dlang.org/install.sh | bash -s dmd

WORKDIR /app
COPY . .

RUN /bin/bash -c "source ~/dlang/dmd-2.111.0/activate && dub build --build=release"

CMD ["./our_logo_proxy"]