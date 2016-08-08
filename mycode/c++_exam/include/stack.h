#ifndef __STATCK_H__
#define __STATCK_H__

#define MAXSIZE 100
//#include "../src/stack.cpp"

/*
namespace briup{
	template <typename T,typename E>
	class Stack{
		private:
			T  *stacks;
			int count;
		public:
			Stack():count(0){};
			Stack(T t1,int count):stacks(t1){
				stacks = new E[MAXSIZE];
				this->count = count;
			}
		//	template <class E>
			void push(E);
		//	template <class E>
				E pop();
		//	template <class E>
				E get_top();
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
//}
*/

namespace briup{
	//typedef int	E;
	typedef unsigned int T;
	template <typename E>
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

