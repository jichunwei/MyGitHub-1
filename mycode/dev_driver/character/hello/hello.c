#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/types.h>
#include <linux/cdev.h>
#include <asm/uaccess.h>

MODULE_LICENSE("Dual BSD/GPL");
#define MAXSIZE		50
#define	INFO		"hello 徐宏!\n"


static int hello_major = 200;
static char buf[MAXSIZE];
static struct cdev cdev;

int hello_open(struct inode *inodep,struct file *filep)
{
	return 0;
}

int hello_release(struct inode *inodep,struct file *filep)
{
	return 0;
}

int hello_read(struct file *filep,char *userbuf,size_t count,loff_t *pos)
{
	//int ret;
	if(count > MAXSIZE)
		count = MAXSIZE;
	if(copy_to_user(userbuf,buf,count))
		return -1;
	return count;
}

int hello_write(struct file *filep,const char *userbuf,size_t count,loff_t *pos)
{
	if(count > MAXSIZE)
		count = MAXSIZE;
	if(copy_from_user(buf,userbuf,count))
		return -1;
	return count;
}

struct file_operations fops = {
	.owner = THIS_MODULE,
	.open = hello_open,
	.read = hello_read,
	.write = hello_write,
	.release = hello_release
};

static int hello_init(void)
{
	dev_t	dev = MKDEV(hello_major,0);
	int		ret;

	if(hello_major){
		ret = register_chrdev_region(dev,1,"hellochar");
	}else{
		ret = alloc_chrdev_region(&dev,0,1,"hellochar");
	}
	if(ret < 0)
		return -ret;
	cdev_init(&cdev,&fops);
	hello_major = MAJOR(dev);
	cdev.owner = THIS_MODULE;
	cdev.ops = &fops;
	if(cdev_add(&cdev,dev,1)){
		printk(KERN_ERR "cdev_add error\n");
		unregister_chrdev_region(dev,1);
		return -1;
	}
	printk(KERN_INFO "cdev_add success!\n");
	memset(buf,0,MAXSIZE);
	memcpy(buf,INFO,sizeof(INFO));
	printk(KERN_INFO "%s",buf);
	return 0;		
}

static void hello_exit(void)
{
	cdev_del(&cdev);
	unregister_chrdev_region(MKDEV(hello_major,0),1);
	printk(KERN_INFO "cdev_rmove success!\n");
}

module_init(hello_init);
module_exit(hello_exit);
module_param(hello_major,int,S_IRUGO);
