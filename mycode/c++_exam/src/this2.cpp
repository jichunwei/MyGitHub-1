//把this指针改为非this指针，THIS作为参数传递
#include <string.h>
#include <iostream>

using namespace std;

struct X{
	private:
		int len;
		char *ptr;
	public:
		int Get_len(X* const THIS){
			return THIS->len;
		}
		char* Get_ptr(X* const THIS){
			return THIS->ptr;
		}
		X& Set(X* const,char *);
		X& Cat(X* const,char *);
		X& Copy(X* const,X &);
		void Print(X* const);
};

X& X::Set(X* const THIS,char *pc){
	THIS->len = strlen(pc);
	THIS->ptr = new char(THIS->len);
	strcpy(THIS->ptr,pc);
	return *THIS;
}

X& X::Cat(X* const THIS,char *pc){
	THIS->len += strlen(pc);
	strcat(THIS->ptr,pc);
	return *THIS;
}

X& X::Copy(X* const THIS,X& x){
	THIS->Set(THIS,x.Get_ptr(&x));
	return *THIS;
}

void X::Print(X* const THIS){
	cout<<THIS->ptr<<endl;
}

int main(void)
{
	char a[] = "abcd";
	char b[] = "efgh";
	char c[] = "ijkl";

	X xobj1;
	xobj1.Set(&xobj1,a);
	xobj1.Cat(&xobj1,b);

	xobj1.Print(&xobj1);

	X xobj2;
	xobj2.Copy(&xobj2,xobj1);
	xobj2.Cat(&xobj2,c);
	xobj2.Print(&xobj2);

	return 0;
}
