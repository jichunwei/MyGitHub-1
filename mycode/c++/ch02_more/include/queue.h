#ifndef __QUEUE_H__
#define __QUEUE_H__

#define MAXSIZE 100

namespace briup{
	typedef int	E;
	typedef unsigned int T;
	struct queue{
		E *queues;
		T count;
		void init();
		void enqueue(E);
		E dequeue();
		E topqueue();
		void destory();
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

