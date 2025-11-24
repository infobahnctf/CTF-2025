FROM python:3.10.13-slim as chroot

RUN /usr/sbin/useradd --no-create-home -u 1000 user

RUN pip install disjoint-set
COPY server.py key.txt run.sh /home/user/
RUN chmod +x /home/user/run.sh

FROM gcr.io/kctf-docker/challenge@sha256:0f7d757bcda470c3bbc063606335b915e03795d72ba1d8fdb6f0f9ff3757364f

COPY --from=chroot / /chroot

COPY nsjail.cfg /home/user/

CMD kctf_setup && \
    kctf_drop_privs \
    socat \
      TCP-LISTEN:1337,reuseaddr,fork \
      EXEC:"nsjail --config /home/user/nsjail.cfg -- /home/user/run.sh"