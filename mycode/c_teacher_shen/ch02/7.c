#include<stdio.h>

int main()
    { 
        int a=100, b=200;
        int const *const pci=&a;
        int *pa;
        pa=&a;
        printf("*pci=%d\n",*pci);
//        *pci=b;
        *pa=a+b;
    printf("pci=%d\n",*pci);
//    pci=&b;
 //   printf ("pcib=%d\n",*pci);
return 0;
    }
