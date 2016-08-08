/*
   container_of(pointer,struct(type),member):根据结构体成员地址，
   获取结构体的地址；
2) typeof(expresion) :获取expresion的类型
他不是C于语言中的而是GNU
   */

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("Dual BSD/GPL");

struct student{
	char	name[50];
	int		age;
};
struct student	stu = {"Jack",20};
//struct student	stu[] = {{"徐宏",20},{"sb",20}};

struct student	*stup;

static int containerof_init(void)
{
	printk(KERN_INFO "containerof module init success!\n");
	//..传入stu.age
	stup = container_of(&stu.age,struct student,age);
	printk(KERN_INFO "name:%s,age:%d\n",stup->name,stup->age);
//	stup[1] = container_of(&stu[1].name,struct student,name);
//	printk(KERN_INFO "name:%s,age:%d\n",stup[1]->name,stup[1]->age);
	return 0;
}

static void containerof_exit(void)
{
	printk(KERN_INFO "containerof module exit success!\n");
}

module_init(containerof_init);
module_exit(containerof_exit);
