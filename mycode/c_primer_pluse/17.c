#include<stdio.h>
#include<limits.h>
#include<float.h>
int main()
{
    printf("some number limits for this system:\n");
    printf("Biggst int: %d\n" ,INT_MAX);
    printf("Smallest long:%lld\n",LONG_MIN);
    printf("one byte=%d bits on this systerm.\n",CHAR_BIT);
    printf("Largest double:%e\n",DBL_MAX);
    printf("Smallest normal float:%e\n",FLT_MIN);
    printf("float precison=%d digist\n",FLT_DIG);
    printf("float epsilon=%e\n",FLT_EPSILON);
    return 0;
}


