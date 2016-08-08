#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

extern int  myadd(void);
extern int  mysub(void);

static int sum1_init(void)
{
    printk(KERN_INFO "sum1 module init success!\n");
    myadd();
    mysub();
    return 0;
}

static void sum1_exit(void)
{
    printk(KERN_INFO "sum1 module exit success!\n");
}

module_init(sum1_init);
module_exit(sum1_exit);
