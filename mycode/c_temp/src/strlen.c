#include<stdio.h>
#define SIZE 30 

int main()
{
    char a[SIZE];
    int i = 0;
   
    printf("Please enter some words:(q to quit)\n");
    scanf("%s",a);
    for(; a[i] != '\0';i++);
 //   {
//	if(a[i] != '\0')
//	    printf("%s\n",a);
  //  printf("i= %d\n",i);
//	printf("enter  next some words:(q to quit)\n");
   // }
    printf("i=%d\n",i);
    return 0;
}


