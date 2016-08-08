#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int sb_init(void)
{
    printk(KERN_INFO "徐宏是帅哥\n");
    return 0;
}

static void sb_exit(void)
{
    printk(KERN_INFO "徐宏是傻比\n");
}

module_init(sb_init);
module_exit(sb_exit);
