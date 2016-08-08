#include<stdio.h>
int main()
{
/*    char ch;
    char A,B,C;
    printf("enter the ch:");
    scanf("%c",&ch);
    switch(ch)
    {
        case A:"the grade is up 90.";break;
        case B:"the grade is in 60-80";break;
        case C:"the grade is low 60";break;
        default:"data error";break;
    }
    printf("\n");
    */
    int score;
    char grade;
    printf("please input the score\n");
    scanf("%d",&score);
    grade=score>=90?'A':(grade=score>=60?'B':'C');
        printf("%d belongs to %c\n",score,grade);
}
