#include <iostream>
#include "queue.h"

using namespace briup;
using namespace std;

int main(void)
{
	queue	q;
	q.init();
	q.enqueue(1);
	q.enqueue(2);
	q.enqueue(3);
	q.enqueue(4);
	
	cout<<"first dequeue:"<<q.dequeue()<<endl;
	cout<<"second dequeue:"<<q.dequeue()<<endl;
	cout<<"top dequeue:"<<q.topqueue()<<endl;
	
	return 0;
}
