#include <setjmp.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TOK_ADD 5 
#define TOK_SUB 6 
jmp_buf env;

void do_line(char *line);
void cmd_add();
void cmd_sub();
int get_token(char *s);


char *prompt = "cal:";

int main()
{
    ssize_t size= strlen(prompt)*sizeof(char);
    char buff[256];
    ssize_t len;
    if(setjmp(env) < 0)
    {
        perror("setjmp");
    }
    write(STDIN_FILENO,prompt,size);
    while(1){
        len = read(STDIN_FILENO,buff,256);
            if(len <= 0)
            {
                break;
            }
        buff[len -1 ] = 0;
        do_line(buff);
        write(STDOUT_FILENO,prompt,size);
    }
}

void do_line(char *line)
{
    int cmd = get_token(line);
    switch(cmd)
    {
        case TOK_ADD:
            cmd_add();
            break;
        case TOK_SUB:
            break;
            cmd_sub(); 
        default:
            fprintf(stderr,"error command\n");
    }

}
            
            
void cmd_add()
{
    int i = get_token(NULL);
    int j = get_token(NULL);
    printf("res is %d\n",i + j);
}

void cmd_sub()
{
    int i = get_token(NULL);
    int j = get_token(NULL);
    printf("res is %d\n",i - j);
}

static int is_number(char *item)
{
    int len = strlen(item);
    int i = 0;
    for(; i < len; i++)
    {
        if(item[i] > '9' || item[i] < '0')
            return 0;
    }
    return 1;
}

    
int get_token(char *s)
{
    char *item = strtok(s," " );
    if(s != NULL){
        if(!strcmp("add",item)) 
            return TOK_ADD;
        if(!strcmp("sub",item)) 
            return TOK_SUB;
    }
    else
    {
        if(is_number(item)){
        int i =atoi(item);
        return i;
        }
        else
            {
                fprintf(stderr,"arg not number\n");
                longjmp(env,1);
            }
    }
}
