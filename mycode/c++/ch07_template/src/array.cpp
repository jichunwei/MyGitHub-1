#include <iostream>
using namespace std;

template <class T,int N>
void array_init(T (&array)[N])
{
	int		i = 0;
	for(; i < N; i++){
		array[i] = i;
	}
}

template <class T,int N>
void array_out(T (&array)[N])
{
	int		i = 0;
	for(; i < N; i++){
	//	cout<<i<<" " ;
		cout<<array[i]<<" " ;
	}
	cout<<endl;
}

int main(void)
{
	int		a[10];
	array_init(a);
	array_out(a);

	double  b[20];
	array_init(b);
	array_out(b);

	return 0;
}
