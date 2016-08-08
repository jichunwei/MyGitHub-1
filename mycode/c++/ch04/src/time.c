#include <time.h>
#include <stdio.h>

int main(void)
{
	time_t	seconds = time(NULL);
	printf("seconds:%lu\n",seconds);

	char *current_time = ctime(&seconds);
	printf("current_time:%s\n",current_time);

	return 0;
}
