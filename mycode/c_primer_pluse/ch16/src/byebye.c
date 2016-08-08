#include <stdio.h>
#include <stdlib.h>
void sign_off();
void too_bad();

int main()
{
    int n;

    atexit(sign_off);
    puts("Enter an integer:");
    if(scanf("%d",&n) != 1)
    {
	puts("that's no integer!");
	atexit(too_bad);
	exit(EXIT_FAILURE);
    }
    printf("%d is %s \n",n,(n % 2 == 0)?"enve":"odd");
    return 0;
}

void sign_off(void)
{
    puts("Thus terminates another magnificent program from");
    puts("SeeSaw Soofeware");
}

void too_bad(void)
{
    puts("SeeSaw Software extends its heartfelt condolences");
    puts("to you upon the failure of your program.");
}
