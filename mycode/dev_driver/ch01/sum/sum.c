#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

int a = 6;
int b = 2;
int     c;
int     d;

int myadd(void)
{
    c = a+b;
	printk(KERN_INFO "c:%d\n",c);
	return 0;
}

EXPORT_SYMBOL_GPL(myadd);

int mysub(void)
{
    d = a-b;
	printk(KERN_INFO "d:%d\n",d);
	return 0;
}

EXPORT_SYMBOL_GPL(mysub);

static int sum_init(void)
{
    printk(KERN_INFO "sum_init module init success!\n");
    return 0;
}

static void sum_exit(void)
{
    printk(KERN_INFO "sum_exit module exit success!\n");
}

module_init(sum_init);
module_exit(sum_exit);

