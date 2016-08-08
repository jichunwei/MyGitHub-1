#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");
int a;
int b;

int myadd(int a,int b)
{
	return a+b;
}

int mysub(int a,int b)
{
	return a-b;
}
EXPORT_SYMBOL_GPL(myadd);
EXPORT_SYMBOL_GPL(mysub);

static int add_init(void)
{
	printk(KERN_INFO "add module init success!\n");
	return 0;
}

static void add_exit(void)
{
	printk(KERN_INFO "add module exit success!\n");
}

module_init(add_init);
module_exit(add_exit);
