#include<stdio.h>
int main()
{
   long int i, b;
   long int b1,b2,b4,b6,b10;
    
    printf("enter you data:");
    scanf("%d",&i);
    b1=100000*0.1; b2=b1+100000*0.075;b4=b2+200000*0.05;b6=b4+200000*0.03;
    b10=b6+200000*0.015;
    i=i/100000;
    switch(i)
    {
    case 0: b=i*100000*0.1; break;
    case 1: b=b1+(i*100000-100000)*0.075;break;
    case 2: b=b2+(i*100000-100000)*0.05;
    case 3:
    case 4:
    case 5: b=b4+(i*100000
            case 
            

