#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <malloc.h>
#include <sys/wait.h>
#include "job.h"

extern	char**	environ;

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

void execute_cmd(Job *job)
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
			if(execvp(job->progs[i].args[0],
					job->progs[i].args) < 0){
				perror("");
				exit(127);
			}
		}else{
			if(waitpid(pid, NULL, WUNTRACED)<0){
				perror("waitpid");
			}
		}
	}
}

int parse_cmd(Job *job, char *line)
{
	char	**args = (char**)malloc(100*sizeof(char*));
	char *cmd = strtok(line, " ");
	args[0] = (char*)malloc(strlen(cmd)*sizeof(char));
	strcpy(args[0], cmd);
	int i = 1;
	char *s;
	while((s=strtok(NULL, " ")) != NULL){
		args[i] = (char*)malloc(strlen(s)*sizeof(char));
		strcpy(args[i], s);
		i++;
	}
	Program *prog = create_program(args);
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

int main(void)
{
	char	buffer[MAX_COMMAND_LEN];
	memset(buffer, 0, MAX_COMMAND_LEN);
	ssize_t	size = strlen(prompt);
	write(STDOUT_FILENO, prompt, size);
	ssize_t	len;
	while(1){
		len = read(STDIN_FILENO, buffer, MAX_COMMAND_LEN);
		buffer[len - 1] = 0;
		if(strlen(buffer) > 0){
			Job *job = create_job(buffer);
			parse_cmd(job, buffer);
			execute_cmd(job);
			destroy_job(job);
		}
		write(STDOUT_FILENO, prompt, size);
		memset(buffer, 0, MAX_COMMAND_LEN);

	}
}




