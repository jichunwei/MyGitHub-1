#include <iostream>
#include "vector.h"
#include <memory.h>
#include <assert.h>

using namespace std;

namespace briup{
		//初始化数组
		void vector::init()
		{
			p = new E[MAX_SIZE];
			assert(p != NULL);
			t_size = 0;
			T maxsize;
			maxsize = MAX_SIZE;
		}

		//检查数组的大小并进行扩展
		void vector::check()
		{
			if(t_size <=  MAX_SIZE)
				return;
			E *q;
			q = p;
			p = new E[MAX_SIZE + INCREMENT_SIZE];
			memcpy(p,q,t_size*sizeof(E));
			delete [] q;
		}

		//动态数组尾部加入元素
		void vector::push_back(E e)
		{
			if(is_full())
				return;
			check();
			p[t_size] = e;
			t_size++;
		}

		//动态数组头部加入元素
		void vector::push_front(E e)
		{
			if(is_full())
				return;
	//		int a = p[0];
			int i = 0;
			for(; i <= t_size; i++){
				p[i] = p[i - 1];
			}
			p[0] = e;
			t_size++;
		}

		//动态数组指定位置加入元素
		void vector::insert(T index ,E e)
		{
			if(is_full())
				return;
			p[index] = e;
			int i = index + 1;
			for(i ; i <= t_size; i++){
				p[i] = p[i + 1];
			}
			t_size++;
		}

		//调整数组的大小
		void vector::resize(T size)
		{
			assert(p != NULL);
			if(MAX_SIZE < size){
				p = new E[size];
			}
			if( MAX_SIZE >= size){
				int i = MAX_SIZE;
				for(; i <= size; i++){
					p[i] = NULL;
				}
			}
		}

		//获取第一个元素
		E vector::front()
		{
			assert(p != NULL);
			return p[0];
		}

		//获取最后一个元素
		E vector::back()
		{
			assert(p != NULL);
			if(is_empty())
				return -1;
			return p[t_size -1];
		}

		//获取在指定位置的元素
		E vector::get(T index)
		{
			assert(p != NULL);
			return p[index];
		}

		//将指定位置的元素清除
		void vector::clear(T index)
		{
			assert(p != NULL);
			p[index] = 0;
			int i = index + 1; 
			for(i; i < t_size -1; i++){
				p[i] = p[i + 1];
			}
			t_size--;
		}

		//将start,end位置的元素删除
		void vector::clear(T start ,T end)
		{
			assert(p != NULL);
			p[start] = 0;
			p[end] = 0;
			int i = start + 1;
			int j = end;
			for(i; i < j; i++){
			p[i] = p[i + 1];
			t_size--;
			}
		}

		//清空所有元素
		void vector::clear()
		{
			assert( p != NULL);
			t_size = 0;
			delete  [] p;
		}

		//遍历数组
		void vector::iterate()
		{
			int i = 0;
			for(; i <= MAX_SIZE;i++){
				cout<<p[i]<<"";
			}
			cout<<endl;
		}
		 
		void vector::destory()
		{
			if(p != NULL)
				delete [] p;
		}
}

