#define STR(s) #s
#define CONCAT(a,b) a##b
CONCAT(a,b);
#define showlist(...) printf(#__VA_ARGS__)
#define report(test,...)((test)?printf(#test):\
        printf(__VA_ARGS__))
showlist(tan,shi,xiong);
report(x>y,"x is %d but y si %d",x,y);

    

int main()
{

printf(STR(hello       world));
}
