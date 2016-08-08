#include<stdio.h>
#include "names_st.h"

void get_names(names *pn)
{
    int i;
    printf("please3 enter your first name:");
    fget(pn->first,SLEN,stdin);
    i = 0;
    while(pn->first[i] != '\n' && pn->first[i] != '\0')
	i++;
    if(pn->first[i] == '\n')
	pn->first[i] = '\0';
    else
	while(getchar() != '\n')
	    continue;

    printf("Please enter your last name:");
    fgets(pn->last,SLEN,stdin);
    i = 0;
    while(pn->last[i] != '\n' && pn->last[i] != '\0')
	i++;
    if(pn->last[i] == '\n')
	pn->last[i] = '\0';
    else
	while(getchar() != '\n')
	    continue;
}

void show_names(const names * pn)
{
    printf("%s %s\n",pn->first,pn->last);
}
/*
int main()
{
    names candidate;
    get_names(&candidate);
    printf("Let's welcome");
    show_name(&candidate);
    printf("to this program!\n");

    return 0;
}
*/
