#include<stdio.h>
#define MIN_PER_HOUR  60
int main()
{
    int min,hour,left;
    printf("Convert min to hours and min:\n");
    printf("Enter the number of min(<=0 to quit):\n");
    scanf("%d",&min);
    while(min>0)
    {
        hour=min/MIN_PER_HOUR;
        left=min%MIN_PER_HOUR;
        printf("%d min si %d hour and %d min\n",min,hour,left);
        printf("Enter next min\n");
        scanf("%d",&min);
    }
    printf("Done!\n");
    return 0;
}
