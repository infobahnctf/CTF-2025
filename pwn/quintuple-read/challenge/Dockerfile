FROM python:3.11-slim@sha256:9e1912aab0a30bbd9488eb79063f68f42a68ab0946cbe98fecf197fe5b085506

RUN apt update
RUN apt install -y socat libseccomp-dev sudo

COPY server.py /
COPY binary /

RUN useradd -m restricted
RUN chmod 700 /server.py
RUN chmod 755 /binary

CMD socat TCP-LISTEN:1337,reuseaddr,fork EXEC:"timeout 60 python3 /server.py"
