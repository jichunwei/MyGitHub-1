#include<stdio.h>
#define DAY_PER_WEEK 7
int main()
{
    int days,week,left;
    printf("Conver days to week:\n");
    printf("Please enter the days(<=0 to quit):\n");
    scanf("%d",&days);
    while(days>0)
    {
        week=days/DAY_PER_WEEK;
        left=days%DAY_PER_WEEK;
        printf("%d days are %d weeks,%d days\n",days,week,left);
        printf("Enter next days(<=0 to quit):\n");
        scanf("%d",&days);
        if(days==0) break;
    }
    printf("Done!\n");
    return 0;
}
