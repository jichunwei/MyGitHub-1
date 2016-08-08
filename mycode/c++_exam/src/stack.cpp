#include "stack.h"
#include <iostream>
#include <cassert>

namespace briup{
	template <class E>
	void stack<E>::init()
	{
		stacks = new E[MAXSIZE];
		assert(stacks != NULL);
		count = 0;
	}

	template <class E>
	void stack<E>::push(E element)
	{
		if(is_full()){
			return;
		}else {
			stacks[count] = element;
			count++;
		}
	}

	template <class E>
	E stack<E>::pop()
	{
		if(is_empty()){
			return -1;
		}else {
		/*	E ret;
			ret = stacks[count -1];
			count--;
			return ret;
			*/
			return stacks[--count];
		}
	}

	template <class E>
	E stack<E>::gettop()
	{
		if(is_empty())
			return -1;
		return stacks[count - 1];
	}
	
	template <class E>
	void stack<E>::destroy()
	{
		if(stacks != NULL)
			delete [] stacks;
	}
}


