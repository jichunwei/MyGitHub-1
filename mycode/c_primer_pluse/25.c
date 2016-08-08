#include<stdio.h>
#include<float.h>
int main()
{
    float f1=1.0,f2=3.0;
    printf("float precision=%d digits\n",FLT_DIG);
    printf("double precision=%d digits\n",DBL_DIG);
    printf("%0.4f\n",f1/f2);
    printf("%0.12f\n",f1/f2);
    printf("%0.26f\n",f1/f2);
    return 0;
}
    
