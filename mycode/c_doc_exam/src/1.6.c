#include <stdio.h>

void fun(int *ch,char *s)
{
	if(s = "int")
		ch[0] = 0;
	else if(s = "unsigned int")
		ch[0] = 1;
}

int main(void)
{
	int  i = -1;
	int  j = 0;
	char *s;
	int  ch[32];

	if(i = -1){
		for(; j <= 31; j++){
			ch[j] = 0;
			ch[0] = 1;
			ch[31] = 1;
			printf("%d",ch[j]);
		}
		printf("\n");
	}


	printf("i is %d\n",i);
	printf("i is %u\n",(unsigned int)i);

	return 0;
}
