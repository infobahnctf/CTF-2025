FROM ubuntu:24.04 AS chroot

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nodejs ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/sbin/userdel -r ubuntu && /usr/sbin/useradd --no-create-home -u 1000 user

COPY chall.js /home/user/chall.js
RUN chmod 644 /home/user/chall.js

FROM gcr.io/kctf-docker/challenge@sha256:9f15314c26bd681a043557c9f136e7823414e9e662c08dde54d14a6bfd0b619f

COPY --from=chroot / /chroot
COPY nsjail.cfg /home/user/nsjail.cfg

CMD kctf_setup && \
    kctf_drop_privs \
    socat TCP-LISTEN:1337,reuseaddr,fork \
      EXEC:'kctf_pow nsjail --config /home/user/nsjail.cfg -E FLAG=infobahn{hidding_code_in_comments_in_big_25_49ad95} -- /usr/bin/node /home/user/chall.js'
