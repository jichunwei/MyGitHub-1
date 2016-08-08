#include <stdio.h>
#define MAXTITL 41
#define MAXAUTL 31
struct book{
    char title[MAXTITL];
    char author[MAXAUTL];
    float value;
}library;
int main()
{
    struct book library = {
	.title = "C primer plus",
	.author = "stephen prata",
	.value = 60.0,
	.value = 42.0
    };

/*    struct book library;
    printf("Please enter the book title.\n");
    gets(library.title);
    printf("Now enter the author.\n");
    gets(library.author);
    printf("NOw enter the value.\n");
    scanf("%f",&library.value);
    */
    printf("%s by %s:$%.2f\n",library.title,library.author,
	    library.value);
    printf("%s: \"%s\"\($%.2f)\n",library.author,library.title,
	    library.value);
    printf("Done.\n");

    return 0;
}

