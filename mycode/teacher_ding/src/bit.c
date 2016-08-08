#include "bit_op.h"
#include<stdio.h>
//#include<stdlib.h>
int  is_bit(int d, int index)
{
    return (((d & (1<<(index -1))) == 0)?0:1);
}

void set_bit(int *d,int index)
{
    *d = *d | (1<< (index -1));
}

void clr_bit(int *d,int index)
{
    *d = *d & (~(1<<(index - 1)));
} 

void bin_out(int d)
{
    int i = 31;
    printf("%-10d:",d);
    for(; i >= 0;i--)
    {
	printf("%d",(d>>i)&1);
    }
    printf("\n");

}
    
int main()
{
    int d = 0x01111111;
    bin_out(d);
    printf("the 32th bit is %d\n",
	    is_bit(d,32));
    clr_bit(&d,10);
    clr_bit(&d,5);
    bin_out(d);
    set_bit(&d,5);
    set_bit(&d,9);
    bin_out(d);
    return 0;

}
	    
