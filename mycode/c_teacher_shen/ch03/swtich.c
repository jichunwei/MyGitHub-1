#include<stdio.h>

int main()
{
    char grade;
    printf("input you grade:");
    scanf("%c",&grade);
    if (grade>'A'|| grade <'D')
    {printf("date error\n");
    }
    printf("you score:");
        switch(grade)
        {
            case 'A':printf("85-100\n");break;
            case 'B':printf("70-84\n");break;
            case 'C':printf("60-69\n");break;
            case 'D':printf("<60\n");break;
    //        default :printf("date error!\n");break;
        }
    return 0;
}

    
