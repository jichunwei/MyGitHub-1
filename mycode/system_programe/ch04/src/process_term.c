#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

void term_fun1(void)
{
    printf("first term function\n");
}

void term_fun2()
{
    printf("second term function\n");
}

void term_fun3()
{
    printf("third term function\n");
}

int main(int argc ,char *argv[])
{
    if(argc < 3)
    {
        fprintf(stderr,"-usage:%s [exit|_exit|return]\n",argv[0]);
        exit(1);
    }
    atexit(term_fun1);
    atexit(term_fun2);
    atexit(term_fun3);

    FILE * fp = fopen(argv[1],"w");
    fprintf(fp,"hello ,process");
    if(!strcmp(argv[2],"exit"))
    {
        exit(0);
    }
    else if (!strcmp(argv[2],"_exit"))
        {
            _exit(0);
        }
    else if (!strcmp(argv[2],"return "))
    {
        return 0;
    }
  /*  else 
    {
        fprintf(stderr,"-usage:%s [exit|_exit|return]\n",argv[0]);
    }
    */
    fclose(fp);
    exit(0);

}


