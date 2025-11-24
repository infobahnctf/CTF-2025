FROM ubuntu:24.04 AS chroot

RUN /usr/sbin/userdel -r ubuntu && /usr/sbin/useradd --no-create-home -u 1000 user

COPY chall flag.txt /home/user/
RUN chmod +x /home/user/chall

FROM gcr.io/kctf-docker/challenge@sha256:9f15314c26bd681a043557c9f136e7823414e9e662c08dde54d14a6bfd0b619f

COPY --from=chroot / /chroot

COPY nsjail.cfg /home/user/

CMD kctf_setup && \
    kctf_drop_privs \
    socat \
      TCP-LISTEN:1337,reuseaddr,fork \
      EXEC:"kctf_pow nsjail --config /home/user/nsjail.cfg -- /home/user/chall"
