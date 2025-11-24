FROM python:3.14.0-slim AS app

COPY chall.py /app/run
COPY flag.txt /flag.txt
RUN chmod 755 /app/run
RUN chmod 444 /flag.txt && mv /flag.txt "/flag_$(cat /dev/urandom | tr -cd a-f0-9 | head -c32).txt"

FROM pwn.red/jail
COPY --from=app / /srv

ENV JAIL_TIME=120 JAIL_MEM=10M JAIL_PORT=1337