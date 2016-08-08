#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <memory.h>
#include <unistd.h>


int main(int argc,char *argv[])
{
	if(argc < 3){
		fprintf(stderr,"-usage:%ss ip #port\n",argv[0]);
		exit(1);
	}
	//1.construct the socket
	int sockfd = socket(AF_INET,SOCK_STREAM,0);
	if(sockfd < 0){
		perror("socket");
		exit(1);
	}
	//2.construct the addr and fill the data
	struct sockaddr_in  saddr;
	memset(&saddr,0,sizeof(saddr));
	saddr.sin_family = AF_INET;
	saddr.sin_port = htons(atoi(argv[2]));
	inet_pton(AF_INET,argv[1],&saddr.sin_addr.s_addr);
	//3.connect to the server
	if(connect(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) <0){
		perror("connect");
		exit(1);
	}
	//4,receive the data form server
	char buffer[1024];
	memset(buffer,0,1024);
	ssize_t size;
	while(1){
		size = read(sockfd,buffer,1024);
		if(size < 0){
			perror("read");
		}else if(size == 0){
			break;
		}
		else{
			write(STDOUT_FILENO,buffer,size);
		}
		//5,release the resource
	}
	close(sockfd);

	exit(0);
}
