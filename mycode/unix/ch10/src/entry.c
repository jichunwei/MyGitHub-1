#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <pwd.h>

static void my_alarm(int signo)
{
	struct passwd	*rootptr;

	printf("int signal handler\n");
	if((rootptr = getpwnam("root")) == NULL){
		perror("getwnam");
//		exit(1);
	}
	alarm(1);
}

int main(void)
{
	struct passwd *ptr;

	if(signal(SIGALRM,my_alarm) == SIG_ERR){
		perror("signal");
		exit(1);
	}
	alarm(1);
	while(1){
		if((ptr = getpwnam("tan")) == NULL){
			perror("getpwnam");
			exit(1);
		}
		if(strcmp(ptr->pw_name,"tan") != 0){
			printf("return value corrupted!,pw_name = %s\n",ptr->pw_name);
		}
	}
	return 0;
}
