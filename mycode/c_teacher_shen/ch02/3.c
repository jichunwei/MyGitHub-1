#include<stdio.h>

int main()
    { 
        int a=100, b=200;
        int const *pci=&a;
        printf("*pci=%d\n",*pci);
//        *pci=b;

 //   printf("pci=%d\n",*pci);
    pci=&b;
    printf ("pcib=%d\n",*pci);
return 0;
    }
