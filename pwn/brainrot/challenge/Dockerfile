FROM ubuntu:22.04 AS app

COPY brainrot /app/run
COPY flag.txt /flag.txt

RUN chmod 444 /flag.txt && mv /flag.txt "/flag_$(cat /dev/urandom | tr -cd a-f0-9 | head -c32).txt"
RUN chmod 755 /app/run

FROM pwn.red/jail

COPY --from=app / /srv

ENV JAIL_MEM=0 JAIL_PIDS=0 JAIL_TIME=600 JAIL_PORT=1337
