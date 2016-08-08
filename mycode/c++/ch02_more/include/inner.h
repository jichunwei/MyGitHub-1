#ifndef __INNER_H__
#define __INNER_H__

class Outer{
	private:
		int outer_value;
	public:
		Outer(int outer_value){
			this->outer_value = outer_value;
		};
		void display();
		int get_outer_value(){return this->outer_value;};
		void set_outer_value()
		{
			this->outer_value = outer_value;
		};

		class Inner{
			private:
				int inner_value;
//				friend class Outer;
			public:
//				int inner_value;
				Inner(int inner_value){
					this->inner_value = inner_value;
				};
				void display();
				int get_inner_value(){
					return this->inner_value;
				};
				void set_inner_value(int inner_value){
					this->inner_value = inner_value;
				};
				void display(Outer &outer);
		};
};

#endif
