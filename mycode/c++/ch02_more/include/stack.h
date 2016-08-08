#ifndef __STATCK_H__
#define __STATCK_H__

#define MAXSIZE 100

namespace briup{
	typedef int	E;
	typedef unsigned int T;
	struct stack{
		E *stacks;
		T count;
		void init();
		void push(E);
		E pop();
		E gettop();
		void destroy();
		bool is_empty(){
			if(count == 0)
				return true;
			else
				return false;
		}
		bool is_full(){
			if(count == MAXSIZE)
				return true;
			else
				return false;
		}
	};
}

#endif

