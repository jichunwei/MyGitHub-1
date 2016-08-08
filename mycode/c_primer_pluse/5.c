#include<stdio.h>
int main()
{
    float aboat=32000.0;
    float toobig=3.4E38*100.0f;
    printf("%e\n",toobig);
    printf("%f can be wrriten %e\n",aboat,aboat);
}
