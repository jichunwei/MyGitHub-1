#include<stdio.h>
#include<string.h>
int main()
{
    char str1[20],str2[20],str3[20];
    char t[220];
    printf("please input 3 string\n:");
    scanf("%s %s %s",str1,str2,str3);
    if(strcmp(str1,str2)>0)
        strcpy(t,str1);strcpy(str1,str2);strcpy(str2,t);
    if(strcmp(str1,str3)>0)
        strcpy(t,str1);strcpy(str1,str3);strcpy(str3,t);
    if(strcmp(str2,str3)>0)
    strcpy(t,str2);strcpy(str2,str3);strcpy(str3,t);
    printf("%s\n %s\n %s\n",str1,str2,str3);
    return 0;
}

