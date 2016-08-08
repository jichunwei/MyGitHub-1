#include<stdio.h>
void report_count();
void accumulate(int k);
int count = 0;
int main()
{
    int value;
    register int i;

    printf("Enter a positive interger(0 to quit):");
    while(scanf("%d",&value)== 1 && value > 0)
    {
        ++count;
        for(i=value;i >= 0; i--)
            accumulate(i);
        printf("Enter a positiver integer(0 to quit):");
    }
    report_count();
    return 0;
}

void report_count()
{
    printf("Loop executer %d times\n",count);
}

#include<stdio.h>
extern int count;

static int total = 0;
//void accumulate( int k);
void accumulate (int k)
{
    static int subtotal =0;

    if(k <= 0)
    {
        printf("Loop cycle: %d\n",count);
        printf("subtotal:%d: total:%d\n",subtotal,total);
        subtotal = 0;
    }
    else 
    {
        subtotal += k;
        total += k;
    }
}
    
    
        

