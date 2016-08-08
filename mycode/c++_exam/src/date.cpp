#include "date.h"
#include <iostream>

using namespace std;

void date::date_out()
{
//	cout<<"the day info"<<endl;
	cout<<"year:"<< year;
	cout<<" month:"<< month;
	cout<<" day:"<< day<<endl;
	cout<<"================"<<endl;
}

void date::date_next_day()
{
	cout<<"the date of next day!"<<endl;
	int flag = 0;

	if((year % 400 == 0) || (year % 4 == 0 &&  year % 100 != 0)){
		flag = 1;
		cout<<"the year is rep!"<<endl;
		}
		if(!flag){
		switch(month){
			case 1: 
				if (day < 31){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 2:
				if (day < 29){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 3:
				if (day < 31){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 4:
				if(day < 30){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 5:
				if(day < 31){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 6:
				if(day < 30){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 7:
				if(day < 31){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 8:
				if(day < 31) day++;
				day = 1;
				month++;
				break;
			case 9:
				if(day < 30) day = 1;
				day = 1;
				month++;
				break;
			case 10:
				if(day < 31) day++;
				day = 1;
				month++;
				break;
			case 11:
				if(day < 30) day++;
				day = 1;
				month++;
				break;
			case 12:
				if(day < 31) day++;
				day = 1;
				month = 1;
				year++;
				break;
			default:
				cout<<"month shuode be low 12!"<<endl;
		}
		}
		if(flag){
		switch(month){
			case 1: 
				if (day < 31){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 2:
				if (day < 28){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 3:
				if (day < 31){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 4:
				if(day < 30){
					day++;
				}else {
					day = 1;
					month++;
				}
				break;
			case 5:
				if(day < 31){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 6:
				if(day < 30){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 7:
				if(day < 31){
					day += 1;
				}else {
					day = 1;
					month++;
				}
				break;
			case 8:
				if(day < 31) day++;
				day = 1;
				month++;
				break;
			case 9:
				if(day < 30) day = 1;
				day = 1;
				month++;
				break;
			case 10:
				if(day < 31) day++;
				day = 1;
				month++;
				break;
			case 11:
				if(day < 30) day++;
				day = 1;
				month++;
				break;
			case 12:
				if(day < 31) day++;
				day = 1;
				month = 1;
				year++;
				break;
			default:
				cout<<"month shoud be low 12!"<<endl;
		}
	}
}

