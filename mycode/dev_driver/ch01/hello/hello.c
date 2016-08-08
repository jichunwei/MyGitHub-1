#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
{
    printk(KERN_INFO "hello init success!\n");
    return 0;
}

static void  hello_exit(void)
{
    printk(KERN_INFO "hello exit success!\n");    
}

module_init(hello_init);//注册模块初始化函数
module_exit(hello_exit);//注册模块卸载函数


