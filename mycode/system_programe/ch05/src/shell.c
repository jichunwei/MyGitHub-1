#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <malloc.h>
#include <sys/wait.h>
#include <fcntl.h>
#include "job.h"
#include <sys/stat.h>

extern	char**	environ;

#define FOREGROUND	0
#define BACKGROUND	1

void env_fun(void)
{
	int i = 0;
	char *env = NULL;
	while((env=environ[i]) != NULL){
		printf("%s\n", env);
		i++;
	}
}

void export_fun(Program *prog)
{
	if(prog->args[1] == NULL){
		fprintf(stderr, "export: invalid argument\n");
		return;
	}
	putenv(prog->args[1]);
}

void echo_fun(Program *prog)
{
	char *s = prog->args[1];
	if(s == NULL){
		fprintf(stderr, "echo: invalid argument\n");
		return;
	}
	if(s[0] == '$'){
		char *v = getenv(s+1);
		printf("%s\n", v);
	}else{
		printf("%s\n", s);
	}
}

void cd_fun(Program *prog)
{
	if(chdir(prog->args[1]) < 0){
		perror("cd");
	}
}

void pwd_fun(Program *prog)
{
	char	buffer[256];
	memset(buffer, 0, 256);
	if(getcwd(buffer, 256) == NULL){
		perror("pwd");
	}
	printf("%s\n", buffer);
}

void exit_fun(Program *prog)
{
	exit(0);
}

void execute_cmd(Job *job, int bg)
{
	int i = 0;
	for(; i < job->progs_num; i++){
		if(!strcmp(job->progs[i].args[0], "cd")){
			cd_fun(&job->progs[i]);
			return;
		}
		if(!strcmp(job->progs[i].args[0], "pwd")){
			pwd_fun(&job->progs[i]);
			return;
		}
		if(!strcmp(job->progs[i].args[0], "exit")){
			exit_fun(&job->progs[i]);
			return;
		}
		if(!strcmp(job->progs[i].args[0], "env")){
			env_fun();
			return;
		}
		if(!strcmp(job->progs[i].args[0], "export")){
			export_fun(&job->progs[i]);
			return;
		}
		if(!strcmp(job->progs[i].args[0], "echo")){
			echo_fun(&job->progs[i]);
			return;
		}
		pid_t	pid;
		if((pid=fork()) < 0){
			perror("fork");
		}else if(pid == 0){
			signal(SIGINT, SIG_DFL);
			signal(SIGTSTP, SIG_DFL);
			signal(SIGTTIN, SIG_DFL);
			signal(SIGTTOU, SIG_DFL);
			signal(SIGCHLD, SIG_DFL);

			if(0 == i){
				if(setpgid(getpid(), getpid()) < 0){
					perror("setpgid");
				}
				job->pgid = getpgid(getpid());
			}else{
				if(setpgid(getpid(), job->pgid) < 0){
					perror("setpgid");
				}
			}
			if(bg == FOREGROUND){
				tcsetpgrp(0, getpgid(getpid()));
			}
			int k = 0;
			for(; k < job->progs[i].redirect_num; k++){
				if(job->progs[i].redirects[k].redirect 
						== RedirectRead){
					if(dup2(job->progs[i].redirects[k].fd, STDIN_FILENO) != STDIN_FILENO){
						perror("dup2");
					}
				}
				if((job->progs[i].redirects[k].redirect
						== RedirectWrite)||
					(job->progs[i].redirects[k].redirect
					    == RedirectAppend)){
					if(dup2(job->progs[i].redirects[k].fd, STDOUT_FILENO) != STDOUT_FILENO){
						perror("dup2");
					}
				}
			}
			if(execvp(job->progs[i].args[0],
					job->progs[i].args) < 0){
				perror("");
				exit(127);
			}
		}else{
			if(0 == i){
				if(setpgid(pid, pid) < 0){
					perror("setpgid");
				}
				job->pgid = getpgid(pid);
			}else{
				if(setpgid(pid, job->pgid)){
					perror("setgpid");
				}
			}
			if(bg == FOREGROUND){
				tcsetpgrp(0, job->pgid);
				waitpid(-job->pgid, NULL, WUNTRACED);
			}
			if(bg == BACKGROUND){
				waitpid(-job->pgid, NULL, WNOHANG);

			}
		}
	}
}


int parse_cmd(Job *job, char *line, int *bg)
{
	char	**args = (char**)malloc(100*sizeof(char*));
	char *cmd = strtok(line, " ");
	args[0] = (char*)calloc(strlen(cmd)+1, sizeof(char));
	strcpy(args[0], cmd);
	int i = 1;
	char *s;
	Redirection* rs[5];
	int redirect_num = 0;
	*bg = FOREGROUND;
	while((s=strtok(NULL, " ")) != NULL){
		if(!strcmp(s, "&")){
			*bg = BACKGROUND;
			continue;
		}
		if(!strcmp(s, "<")){
			char *file = strtok(NULL, " ");
			if(file == NULL)continue;
			else{
				int fd = open(file, O_RDONLY);
				rs[redirect_num++] = create_redirect(fd, RedirectRead);
			}
			continue;
		}
		if(!strcmp(s, ">")){
			char *file = strtok(NULL, " ");
			if(file == NULL)continue;
			else{
				int fd = open(file, O_WRONLY|O_CREAT|O_TRUNC, S_IRWXU|S_IRWXG|S_IRWXO);
				rs[redirect_num++] = create_redirect(fd, RedirectWrite);
			}
			continue;
		}
		if(!strcmp(s, ">>")){
			char *file = strtok(NULL, " ");
			if(file == NULL)continue;
			else{
				int fd = open(file, O_WRONLY|O_CREAT|O_APPEND, S_IRWXU|S_IRWXG|S_IRWXO);
				rs[redirect_num++] = create_redirect(fd, RedirectAppend);
			}
			continue;
		}
		args[i] = (char*)calloc(
			strlen(s) + 1, sizeof(char));
		strcpy(args[i], s);
		i++;
	}
	Program *prog = create_program(args);
	int k = 0;
	for(; k < redirect_num; k++){
		add_redirection(prog, rs[k]);
		destroy_redirect(rs[k]);
	}
	add_program(job, prog);
	int j = 0;
	for(; j < i; j++){
		free(args[j]);
	}
	free(args);
	return 0;
}

char*	prompt = "mshell> ";
#define MAX_COMMAND_LEN  256

void sig_handler(int signo)
{
	if(SIGCHLD == signo){
		waitpid(-1, NULL, WNOHANG);
		tcsetpgrp(0, getpgid(getpid()));
	}
}

int main(void)
{
	setpgid(getpid(), getpid());
	signal(SIGINT, SIG_IGN);
	signal(SIGTSTP, SIG_IGN);
	signal(SIGTTIN, SIG_IGN);
	signal(SIGTTOU, SIG_IGN);
	signal(SIGCHLD, sig_handler);

	char	buffer[MAX_COMMAND_LEN];
	memset(buffer, 0, MAX_COMMAND_LEN);
	ssize_t	size = strlen(prompt);
	write(STDOUT_FILENO, prompt, size);
	ssize_t	len;
	int	bg;
	while(1){
		len = read(STDIN_FILENO, buffer, MAX_COMMAND_LEN);
		buffer[len - 1] = 0;
		if(strlen(buffer) > 0){
			Job *job = create_job(buffer);
			parse_cmd(job, buffer, &bg);
			execute_cmd(job, bg);
			destroy_job(job);
		}
		write(STDOUT_FILENO, prompt, size);
		memset(buffer, 0, MAX_COMMAND_LEN);
	}
}




