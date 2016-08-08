#include <iostream>
using namespace std;

template <typename T>
class Binary_operation{
	private:
	T x;
	T y;
	char op;
	void add(){
		cout<<x<<op<<y<<"="<<x+y<<endl;
	}
	void sub(){
		cout<<x<<op<<y<<"="<<x-y<<endl;
	}
//	void mul();
//	void div();
	void mul(){
		cout<<x<<op<<y<<"="<<x*y<<endl;
	}
	void div(){
		cout<<x<<op<<y<<"="<<x/y<<endl;
	}
	public:
	Binary_operation(T x,T y):x(x),y(y){};
	void determine_op(char op);
};

/*
template <typename T>
void Binary_operation <T>::mul()
{
	cout<<x<<op<<y<<"="<<x*y<<endl;
}

template <typename T>
void Binary_operation <T>::div()
{
	cout<<x<<op<<y<<"="<<x/y<<endl;
}
*/

template <typename T>
void Binary_operation <T>::determine_op(char op)
{
	this->op = op;
	switch(op)
	{
		case '+':
			add();
			break;
		case '-':
			sub();
			break;
		case '*':
			mul();
			break;
		case '/':
			div();
			break;
		default:
			cout<<"this operation is wrong"<<endl;
			break;
	}
}

int main(void)
{
	Binary_operation<int> op(10,10);
	op.determine_op('+');
	op.determine_op('-');
	op.determine_op('*');
	op.determine_op('/');

	return 0;
}
