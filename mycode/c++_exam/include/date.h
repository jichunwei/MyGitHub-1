#ifndef __DATE_H__
#define __DATE_H__

class date{
	private:
		int		year;
		int		month;
		int		day;
	public:
	    date():year(2011),month(1),day(1){};
		date(int year,int month,int day)
		{
			this->year = year;
			this->month = month;
			this->day = day;
		}

		void set_year(int year)
		{
			this->year = year;
		};

		int get_year(){return this->year;};

		void set_month(int month)
		{
			this->month = month;
		};

		int get_month(){return this->month;};

		void set_day(int day)
		{
			this->day = day;
		}

		int get_day(){return this->day;};

		void change_day(int year,int month,int day)
		{
			this->year = year;
			this->month = month;
			this->day = day;
		}
		
		void date_out();
		void date_next_day();
};

#endif

