#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <sys/times.h>

static void pr_times(clock_t real,struct tms *tmsstart,struct tms *tmsend)
{
	static		long clktck = 0;
	if(clktck == 0)
		if((clktck = sysconf(_SC_CLK_TCK)) < 0){
			perror("sysconf");
			exit(1);
		}
	printf("	real:	%7.2f\n",real/(double) clktck);
	printf("	user:	%7.2f\n",
			(tmsend->tms_utime - tmsstart->tms_utime) /(double) clktck);
	printf("	sys:	%7.2f\n",
			(tmsend->tms_stime - tmsstart->tms_stime) / (double) clktck);
	printf("	child user:	%7.2f\n",
			(tmsend->tms_cutime - tmsstart->tms_stime) / (double) clktck);
	printf("	child sys:	%7.2f\n",
			(tmsend->tms_cstime - tmsstart->tms_cstime) / (double) clktck);

}

static void do_cmd(char *cmd)
{
	struct	tms		tmsstart,tmsend;
	clock_t			start,end;
	int				status;

	printf("\ncmommand:%s\n",cmd);
	if ((start = times(&tmsstart)) == -1){
		perror("times");
		exit(1);
	}
	if ((status = system(cmd)) < 0){
		perror("system");
		exit(1);
	}
	if ((end = times(&tmsend)) == -1){
		perror("times error");
		exit(1);
	}
	pr_times(end-start,&tmsstart,&tmsend);
//	pr_exit(status);
}

int main(int argc ,char *argv[])
{
	int		i;

	if(argc < 2){
	fprintf(stderr,"-usage:%s\n",argv[0]);
	exit(0);
	}

	setbuf(stdout,NULL);
	for(i = 1; i < argc ; i++)
		do_cmd(argv[i]);
	exit(0);	
}


