#ifndef __MYWC_H__
#define __MYWC_H__
#include <iostream>
using namespace std;

class Mywc{
	private:
		char	ch;
		int		words;
		int		lines;
	public:
		Mywc(){};
		Mywc(char ch,int words,int lines){
			this->ch = ch;
			this->words = words;
			this->lines = lines;
		}
		void out(){
			cout<<"character:"<<ch<<",name:"<<name<<",lines"<<lines<<endl;
		}
//		char get_ch(){return this->ch;}
//		char get_word(){return this->words;}
//		char get_lines(){return this->lines;};

};
#endif
