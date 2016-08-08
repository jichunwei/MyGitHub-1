#include<stdio.h>

void int_out(int d)
{
    int i = 1;
    int size = 1;
    while((i=(i<<1)) !=  0)
    {
	size++;
    }
    printf("%-10d:",d);
    int j;
    for(j = size - 1; j >= 0; j--)
    {
	int bit = (d >> j) & 1;
	printf("%d",bit);
    }
    printf("\n");

}
void char_out(char c)
{

}

void float_out(float d);
int main()
{
    int i = 65;
    int_out(i);
     i = -65;
    int_out(i);
    int_out(i >> 2);
    int_out(i << 2);
    float_out(3.14);
    return 0;

}

void float_out(float d)
{
    int *p = (int *)&d;

    printf("%-10f:",d);
    int j;
    for(j = 31; j >= 0; j--)
    {
	int bit = (*p >> j) & 1;
	printf("%d",bit);
    }
    printf("\n");
} 
  
    
    

