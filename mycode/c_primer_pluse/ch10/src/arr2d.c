#include <stdio.h>
#define ROWS 3
#define COLS 3

int sum_rows(int ar[][COLS],int rows)
{
    int r;
    int c;
    int tot;

    for(r = 0; r < rows; r++)
    {
        tot = 0; for(c = 0; c < COLS; c++) {
            tot += ar[r][c];
        }
        printf("sum_rows %d is %d\n",r,tot);
    }
}

int sum_cols(int (*ar)[COLS] , int rows)
{
    int r;
    int c;
    int tot;

    for( c = 0; c < COLS; c++)
    {
        tot = 0;
        for(r = 0; r < rows; r++)
        {
            tot += ar[r][c];
        }
        printf("sum_cols %d is %d\n",c,tot);
    }
}

int sum_rc(int (*ar)[COLS],int rows)
{
    int r;
    int c;
    int tot = 0;

    for(r = 0; r < rows; r++)
        for(c = 0; c < COLS; c++)
            tot += ar[r][c];
//    printf("sum_rc is %d\n",tot);
    return tot;
}

int main()
{
    int  a[ROWS][COLS] = {{1,2,3},{5,6,7},{1,2,3}};

    sum_rows(a,ROWS);
    sum_cols(a,ROWS);
    printf("sum_rc is %d\n",sum_rc(a,ROWS));
    return 0;
}
        
            
