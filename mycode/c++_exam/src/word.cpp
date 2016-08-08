#include <iostream>
#include <fstream>
#include <cstdlib>

using namespace std;

#define WHITE_SPACE \
	(c == ' ' || c == '\n' || c == '\t')
int main(int argc,char *argv[])
{
	int		c;
	int		chars = 0;
	int		words = 0;
	int		lines = 0;
	char	flag = 'n';

	fstream fin(argv[1],ios::in);
	if(fin == NULL){
		cout<<"create spIn error"<<endl;
		exit(EXIT_FAILURE);
	}

	while((c = fin.get()) != EOF){
		if(WHITE_SPACE){	
			flag = 'n';
			if(c == '\n')
				lines++;
		}else{
			chars++;
			if(flag == 'n'){
				words++;
				flag = 'y';
			}
		}
	}
	printf("Number of characters: %d\n",chars);
	printf("Number of words: %d\n",words);
	printf("Number of lines: %d\n",lines);

	fin.close();
}
