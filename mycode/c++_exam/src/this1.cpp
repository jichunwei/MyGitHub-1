#include <string.h>
#include <iostream>

using namespace std;

struct X{
	private:
		int len;
		char *ptr;
	public:
		int GetLen(){
			return len;
		}
		char *GetPtr(){
			return ptr;
		}
		X& Set(char *);
		X& Cat(char *);
		X& Copy(X&);
		void Print();
};

X& X::Set(char *pc){
	len = strlen(pc);
	ptr = new char[len];
	strcpy(ptr,pc);
	return *this;
}

X& X::Cat(char *pc){
	len += strlen(pc);
	strcat(ptr,pc);
	return *this;
}

X& X::Copy(X& x){
	Set(x.GetPtr());
	return *this;
}

void X::Print(){
	cout<<len<<endl;
	cout<<ptr<<endl;
	cout<<"============"<<endl;
}


int main(void)
{
	X xobj1;
	char a[] = "abcd";
	char b[] = "efgh";
	char c[] = "ijkl";

	xobj1.Set(a);
	xobj1.Cat(b);
	xobj1.Print();

	X xobj2;
	xobj2.Copy(xobj1);
	xobj2.Cat(c);

	xobj2.Print();
}
