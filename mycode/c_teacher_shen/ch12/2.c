#define abs(x) (((x)>0)?(x):(-(x)))
main()
{
    int a=-3 ,b;
    float c= -2.4,d;
    b=abs(a);
    d=abs(c);
    printf("b=%d,d=%f\n",b,d);
    
}
