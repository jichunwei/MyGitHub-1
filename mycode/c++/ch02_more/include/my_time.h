#ifndef __TIME_H__
#define  __TIME_H__
#include <iostream>
using namespace std;
class Time{
	private:
		int hour;
		int min;
		int seconds;
	public:
//		Time():hour(0),min(0),seconds(0){};

		Time(){
			this->hour = 0;
			this->min = 0;
			this->seconds = 0;
		};
		

		Time(int hour,int min){
			this->hour = hour;
			this->min = min;
		};

		Time(int hour,int min,int seconds){
			this->hour = hour;
			this->min = min;
			this->seconds = seconds;
		};

		void reset(int hour,int min,int seconds){
			this->hour = hour;
			this->min = min;
			this->seconds = seconds;
		};

		int get_hour(){return this->hour;};
		void set_hour(int hour){
			this->hour = hour;
		};
		int get_min(){return this->min;};
		void set_min(int min){
			this->min = min;
		};

		int get_seconds(){return this->seconds;};
		void set_seconds(int seconds){
			this->seconds = seconds;
		};

		void display(){
			cout<<"hour:"<<hour;
			cout<<",min:"<<min;
			cout<<",seconds:"<<seconds<<endl;
			cout<<"************"<<endl;
		};

		Time add_time(Time &time){
			Time total;
			int mins = this->min + time.min;
			int seconds = this->seconds + time.seconds;
			total.hour = this->hour + time.hour + mins/60; 
		//	total.min = mins % 60 ;
			total.min = mins % 60 + seconds / 60;
			total.seconds = seconds % 60;
			return total;
		};
		Time operator + (Time &time)
		{
			Time total;
			int mins = this->min + time.min;
			int seconds = this->seconds + time.seconds;
			total.hour = this->hour + time.hour + mins /60;
			total.min = mins % 60 + seconds / 60;
			total.seconds = seconds % 60;

			return total;
		};
		Time operator - (Time &time)
		{
			Time result;
			int seconds1 = this->seconds + this->hour*3600 + this->min*60;
			int seconds2 = time.seconds + time.hour *3600 + time.min*60;
			int seconds = seconds1 - seconds2;
			result.hour = seconds/3600;
			result.min = (seconds - result.hour * 3600)/ 60;
			result.seconds = seconds % 60;

			return result;
		};
		Time operator ++(int)
		{
			Time time = *this;
			this->hour++;
			this->min++;
			if(min >= 60){
				hour = hour + min /60;
				min = min % 60;
			}
			this->seconds++;
			if(seconds >= 60){
				min = seconds / 60;
				seconds = seconds % 60;
			}
			return time;
		};
		Time operator++()
		{
			Time time = *this;
			int seconds = this->seconds + 1 + (this->hour+1)*3600 + (this->min + 1)*60;
			this->hour = seconds / 3600;
			this->min = (seconds - this->hour * 3600)/60;
			this->seconds = seconds % 60;

			return time;
		}
		Time operator*(int value)
		{
			int seconds = this->seconds *value + (this->hour * value)*3600 + (this->min *value)*60;
			this->hour = seconds /3600;
			this->min = (seconds - this->hour * 3600) /60;
			this->seconds = seconds % 60;
			return (*this);
		}
		friend Time operator*(double value,Time &time);
};

Time operator*(double value,Time &time)
{
	Time result;
	int seconds = time.seconds *value + (time.hour *value *3600) + (time.min *value * 60);
	result.hour = seconds /3600;
	result.min = (seconds - result.hour * 3600) / 60;
	result.seconds = seconds % 60;

	return result;

}

#endif
