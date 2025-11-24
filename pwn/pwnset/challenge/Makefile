CC = gcc

LDFLAGS_LOG = -no-pie -fno-stack-protector -Wl,-z,norelro

all: chal log

chal: chal.c
	$(CC) chal.c -o chal

log: log.c
	$(CC) log.c -o log $(LDFLAGS_LOG)

clean:
	rm -f chal log
