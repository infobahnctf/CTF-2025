# <pre>
FROM python:3.11

COPY flag /flag
RUN mv /flag /flag-`cat /proc/sys/kernel/random/uuid`.txt

WORKDIR /app
RUN ln -s /lib/git-core /app/cgi-bin
COPY Dockerfile index.html

RUN useradd user
USER user
EXPOSE 1337
CMD ["python", "-m", "http.server", "--cgi", "1337"]
