#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int sig_int_flag;

int main()
{
	int		sig_int();
	int		a = 1,b = 2;
	int		sum = 0;

	if(signal(SIGINT,sig_int) == SIG_ERR){
		perror("signal");
		exit(1);
	}
	sum = a + b;
	printf("sum is %d\n",sum);
	while (sig_int_flag == 0)
		pause();
	
	return 0;
}

sig_int()
{
	signal(SIGINT,sig_int);
	sig_int_flag = 1;
}
