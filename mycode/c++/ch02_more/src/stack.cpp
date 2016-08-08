#include "stack.h"
#include <iostream>
#include <cassert>

namespace briup{
	void stack::init()
	{
		stacks = new E[MAXSIZE];
		assert(stacks != NULL);
		count = 0;
	}

	void stack::push(E element)
	{
		if(is_full()){
			return;
		}else {
			stacks[count] = element;
			count++;
		}
	}

	E stack::pop()
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

	E stack::gettop()
	{
		if(is_empty())
			return -1;
		return stacks[count - 1];
	}
	
	void stack::destroy()
	{
		if(stacks != NULL)
			delete [] stacks;
	}
}


