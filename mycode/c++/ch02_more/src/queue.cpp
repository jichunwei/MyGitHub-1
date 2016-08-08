#include <iostream>
#include "queue.h"
#include <assert.h>

namespace briup{
	void queue::init()
	{
		queues = new E[MAXSIZE];
		assert(queues != NULL);
		count = 0;
	}

	void queue::enqueue(E element)
	{
		if(is_full())
			return;
		else 
			queues[count] = element;
		count++;
	}

	E queue::dequeue()
	{
		if(is_empty())
			return -1;
		E ret = queues[0];
			int i = 0;
			for(; i < count ; i++){
				queues[i] = queues[i + 1];
				count--;
			}
		return ret;
	}

	E queue::topqueue()
	{
		if(is_empty())
			return -1;
		else
			return queues[0];
	}

	void queue::destory()
	{
		if(queues == NULL)
			return;
		else {
			delete [] queues;
			queues = NULL;
		}
	}
}


