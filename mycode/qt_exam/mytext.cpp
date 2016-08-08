#include "mytext.h"

float fun(char flag,float a,float b)
{
    switch(flag)
    {
    case '+': return a+b;
    case '-': return a-b;
    case '*': return a*b;
    case '/': return a/b;
    default: return -1;
    }
}

void mytext::operation()
{
    char a[10] = {'\0'};
    int i=0,j=0;
    char flag = '\0';
    for(;i<len;i++)
    {
        if((this->equation[i] =='.'||this->equation[i] >='0') && this->equation[i] <='9')
        {
            a[j++] = this->equation[i];
            continue;
        }
        else{
            if(flag == 0)
            {
                this->result = atof(a);
                memset(a,0,10);
                flag = this->equation[i];
            }
            else{
                this->result = fun(flag,this->result,atof(a));
                flag = this->equation[i];
            }
            j=0;
        }
    }
 memset(this->equation,0,1024);
 len=0;
 sprintf(a,"%g",this->result);
 this->setText(a);
}
void mytext::mySlot_0()
{
    this->equation[this->len++] = '0';
    this->setText(equation);
}
void mytext::mySlot_1()
{
    equation[len++] = '1';
    this->setText(equation);
}
void mytext::mySlot_2()
{
    equation[len++] = '2';
    this->setText(equation);
}
void mytext::mySlot_3()
{
    equation[len++] = '3';
    this->setText(equation);
}
void mytext::mySlot_4()
{
    equation[len++] = '4';
    this->setText(equation);
}
void mytext::mySlot_5()
{
    equation[len++] = '5';
    this->setText(equation);
}
void mytext::mySlot_6()
{
    equation[len++] = '6';
    this->setText(equation);
}
void mytext::mySlot_7()
{
    equation[len++] = '7';
    this->setText(equation);
}
void mytext::mySlot_8()
{
    equation[len++] = '8';
    this->setText(equation);
}
void mytext::mySlot_9()
{
    equation[len++] = '9';
    this->setText(equation);
}
void mytext::mySlot_back()
{
    equation[--len] = '\0';
    this->setText(equation);
}
void mytext::mySlot_ce()
{
    equation[0] = '\0';
    this->len = 0;
    this->setText(equation);
}
void mytext::mySlot_clr()
{
    this->len = 0;
    equation[0] = '\0';
    this->setText(equation);
}
void mytext::mySlot_convert()
{

    int i=this->len+1;
    for(;i > 1; i--)
    {
        equation[i] = equation[i-2];
    }
    equation[0]='-';
    equation[1]='(';
    len += 2;
    equation[len++]=')';
    this->setText(equation);

}
void mytext::mySlot_div()
{
    equation[len++] = '/';
    this->setText(equation);

}
void mytext::mySlot_mul()
{
    equation[len++] = '*';
    this->setText(equation);
}
void mytext::mySlot_add()
{
    equation[len++] = '+';
    this->setText(equation);
}
void mytext::mySlot_sub()
{
    equation[len++] = '-';
    this->setText(equation);
}
void mytext::mySlot_point()
{
    equation[len++] = '.';
    this->setText(equation);
}
void mytext::mySlot_equal()
{
    equation[len++] = '=';
    operation();

}
