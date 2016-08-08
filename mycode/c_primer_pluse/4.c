#include<stdio.h>
#include<inttypes.h>
int main()
{
    int16_t me16;
    me16=4593;
    printf("the first,assume int16_t is short:");
    printf("me16=%hd\n",me16);
    printf("next,let's not make any assumptions.\n");
    printf("instead,use a \"macro\" from inttypes.h:");
    printf("me16= %"PRID16"\n",me16);
    return 0;
}
