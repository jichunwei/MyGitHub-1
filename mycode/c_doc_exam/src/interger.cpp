#include <iostream>
using namespace std;

class interger{ private: int a; int b;
	public:
		interger(){
			this->a = 1;
			this->b = 1;
		};
		interger(int a,int b){
			this->a = a;
			this->b = b;
		};
		class my_exception{
			private:
				int e;
				friend class interger;
			public:
				my_exception(int e){
					this->e = e;
				};
				int what(){
					return this->e;
					//				cout<<"the num to be div can't be zero!"<<endl;
				};
		};

		int get_a(){return this->a;};
		void set_a(int a){
			this->a = a;
		};
		int get_b(){return this->b;};
		void set_b(int b){
			this->b = b;
		};
		void display(){
			cout<<"a:"<<a;
			cout<<",b:"<<b<<endl;
		};
		bool div(){
			bool flag;
			if(b == 0 || a == 0)
				throw 1;
			if(this->a % this->b == 0)
			{
				flag = true;
				cout<<"a can be div by b!"<<endl;
			}else if( b % a == 0){
				flag = true;
				cout<<"b can be div by a!"<<endl;
			}else {
				flag = false;
				cout<<"no!"<<endl;
			}
		}
};

int main(void)
{
	interger I1;
	I1.display();

	interger I2(8,4);
	I2.display();
	I2.div();

	try{
		interger I3(2,0);
		I3.display();
		I3.div();
	}catch(int e){
		cout<<"b can't be zero!"<<endl;
	}

	return 0;
}
