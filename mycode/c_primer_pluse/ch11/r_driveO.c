static unsigned long int next = 1;
int randO()
{
    next = next * 1103515245 + 12345;
    return (unsigned int)(next/65536) % 32768;
}

void srand1(unsigned int seed)
{
    next = seed;
}

#include<stdio.h>
extern int randO();
extern void strand1(unsigned int x);
int main()
{
    int count;
    unsigned seed;

    printf("Plsase enter your choice for seed.\n");
    while(scanf("%u",&seed) == 1)
    {
       srand1(seed);
    
    for(count = 0; count < 5; count++)
        printf("%hd\n",randO());
    printf("Please enter next (q to quit):\n");
    }
    printf("Done\n");

    return 0;
}

  
