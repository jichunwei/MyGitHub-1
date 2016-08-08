#include<stdio.h>
int main()
{
    int bph2o=212;
    int rv;
    rv=printf("%d F is water's boiling point.\n",bph2o);
    printf("the printf() function printed %d characters.\n",rv);
    printf("the printf() function printed %d number.\n",rv);
    printf("Hello,young"   "lovers"  ",wherever are you.\n");
    printf("Hello,young lovers"
            ",wherever you are.\n");
    return 0;
}
