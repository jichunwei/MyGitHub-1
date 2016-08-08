#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

extern void myfun(void);

static int  export2_init(void)
{
    printk(KERN_INFO "export2 module init success!\n");
    myfun();
    return 0;
}

static void export2_exit(void)
{
    printk(KERN_INFO "export2 module exit success!\n");
}

module_init(export2_init);
module_exit(export2_exit);

