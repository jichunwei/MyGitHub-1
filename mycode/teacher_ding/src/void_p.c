#include<stdio.h>


void fcntl(int cmd, void *f)
{
    if(cmd == 1){
	printf("interger value is %d\n",*((int *)f));
    }
    else if(cmd ==2)
    {
	printf("doubel value is %f\n",*((double *)f));
    }
    else if(cmd == 3)
{
    void (* fun)(int ,int);
    fun =(void (*)(int ,int ))f;
    (* fun)(3,4);
}
}

void add(int i,int j)
{
    printf("add value: %d\n",(i+j));
}
int main()
{
    int i = 3;
    double d = 3.14;
    fcntl(1,&i);
    fcntl(2,&d);
    fcntl(3,add);
    return 0;
}
