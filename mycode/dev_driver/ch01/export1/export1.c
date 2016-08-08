#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

void myfun(void)
{
    printk(KERN_INFO "我们的歌!\n");
}

EXPORT_SYMBOL_GPL(myfun);

static  int export1_init(void)
{
    printk(KERN_INFO "export1 module init success!\n");
    return 0;
}

static  void export1_exit(void)
{
    printk(KERN_INFO "export1 module exit success!\n");
}

module_init(export1_init);
module_exit(export1_exit);
