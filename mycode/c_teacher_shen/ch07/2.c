#include<stdio.h>
#include<stdarg.h>
float average(int n_values,...)
{
    va_list var_arg;
    int count,d;
    float sum=0;
    va_start(var_arg,n_values);

    for(count=0;count<n_values;count+=1)
    {
        d=va_arg(var_arg,int); 
        printf("%4d",d);
        sum+=d;

     //   sum+=va_arg(var_arg,int);
    }
    printf("\n");
    va_end(var_arg);
    return sum/n_values;
}
int main()
{
    printf("average=%f\n",average(4,1,2,3,4)); 
    return 0;
            
}

