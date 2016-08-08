#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int a = 5;
static int b = 1;
static int c;
static int d;

extern int myadd(int ,int );
extern int mysub(int ,int );

static int add1_init(void)
{
	printk(KERN_INFO "add1 module init success!\n");
	c = myadd(a,b);
	printk(KERN_INFO "c is %d\n",c);
	d = mysub(a,b);
	printk(KERN_INFO "d is %d\n",d);
	return 0;
}

static void add1_exit(void)
{
	printk(KERN_INFO "add1 module exit success!\n");
}
module_init(add1_init);
module_exit(add1_exit);
module_param(c,int,S_IRUGO);
module_param(d,int,S_IRUGO);

