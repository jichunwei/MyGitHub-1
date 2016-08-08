#include <linux/init.h>
#include <linux/module.h>

static  char *name = "tan";
static  int  age = 24;

MODULE_LICENSE("Dual BSD/GPL");

static int param_init(void)
{
    printk(KERN_INFO "param module init success!\n");
    printk(KERN_INFO "name:%s\n",name);
    printk(KERN_INFO "age:%d\n",age);
    return 0;
}

static void param_exit(void)
{
    printk(KERN_INFO "parme module exit success!\n");
}

module_init(param_init);
module_exit(param_exit);
module_param(name,charp,S_IRUGO);
module_param(age,int,S_IRUGO);

