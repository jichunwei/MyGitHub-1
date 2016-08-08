#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int info_init(void)
{
	printk(KERN_INFO "info module init success!\n");
	return 0;
}

static void info_exit(void)
{
	printk(KERN_INFO "info module exit success!\n");
}

module_init(info_init);
module_exit(info_exit);
MODULE_AUTHOR("tan");
MODULE_DESCRIPTION("This is a info module test program");
MODULE_VERSION("version1.0");
MODULE_ALIAS("myinfo module");

