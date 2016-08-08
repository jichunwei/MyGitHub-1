#include<stdio.h>
int main()
{    char i,j,k;
    for(i='x';i<='z';i++)
    { for(j='x';j<='z';j++)
        { for(k='x';k<='x';k++)
            {
                if(i!=j&&i!=k&&j!=k&&i!='x'&&k!='x'&&k!='z')
                    printf("a--%cb--%cc--%c\n",i,j,k);
            }
        }
    }
}
