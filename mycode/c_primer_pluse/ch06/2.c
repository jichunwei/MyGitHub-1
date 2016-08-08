#include<math.h>
#include<stdio.h>
int main()
{
    const double answer=3.14159;
    double r;
    printf("what is the value of pi?\n");
    scanf("%1f",&r);
    while(fabs(r-answer)>0.1)
    { 
        printf("try again!\n");
        scanf("%1f",&r);
    }
    printf("close enough!\n");
    return 0;
}
    
