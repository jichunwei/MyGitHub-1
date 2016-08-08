#ifndef __VECTOR_H__
#define __VECTOR_H__

#define MAX_SIZE 5
#define INCREMENT_SIZE 3
typedef int		E;
typedef unsigned int	T;
namespace briup{
	struct vector{
		//指向动态数组的指针
		E *p;
		//动态数组已有的元素的个数
		T t_size;
		//初始化数组
		void init();

		//检查数组的大小并进行扩展
		void check();

		//动态数组尾部加入元素
		void push_back(E e);

		//动态数组头部加入元素
		void push_front(E e);

		//动态数组指定位置加入元素
		void insert(T index ,E e);

		//查询动态数组的当前元素的个数
		T size(){return t_size;}

		//查询动态数组能存放的最大元素个数
		T maxsize(){return MAX_SIZE;};

		//判断数组是否为空
		bool is_empty(){return t_size == 0;}
		
		//判断数组是否为满
		bool is_full(){return t_size >= MAX_SIZE;}

		//调整数组的大小
		void resize(T size);

		//获取第一个元素
		E front();
		//获取最后一个元素
		E back();
		//获取在指定位置的元素
		E get(T index);
		//将指定位置的元素清除
		void clear(T index);
		//将start,end位置的元素删除
		void clear(T start ,T end);
		//清空所有元素
		void clear();
		//遍历数组
		void iterate();
		void destory();
	};
}

#endif
