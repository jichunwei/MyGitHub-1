#ifndef __DETAIL_H__
#define __DETAIL_H__
#include <iostream>

class rectangle{
	private:
		int height;
		int width;
		const int heavy;
		int &ref;
	public:
		rectangle():height(5),width(5),heavy(10),ref(height){
			std::cout<<"construct1 occurred!"<<std::endl;
		}

		rectangle(int height,int width):heavy(10),ref(this->height)
		{
			std::cout<<"construct2 occurred!"<<std::endl;
			this->height = height;
			this->width = width;
		}

	~rectangle()
	{
		std::cout<<"deconstructor occurred!"<<std::endl;
	};

	int getHeight(){return height;}
	void setHeight(int height)
	{
		this->height = height ;
	}
	int getWidth(){return width;}
	void setWidth(int width)
	{
		this->width = width;
	}
	void change(int height,int width)const
	{
//		this->height = height;
//		this->width = width;
		std::cout<<"in change,height:"<<height;
		std::cout<<",width"<<width<<std::endl;
	}

	void display();
};

#endif

