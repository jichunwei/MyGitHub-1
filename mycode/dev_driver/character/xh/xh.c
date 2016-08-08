/*
字符设备驱动编程步骤：
1） 创建设备号，并进行注册;
	a)自己指定主设备号；
	dev_t	devno = MKDEV( major,minor);
register_chrdev_region(devno,count,name);
	b)由系统分配主设备号
	alloc_chrde_egion(&devno,0,count,name);
	major = MAJOR(devno);
2) 初始化字符设备(cdev);
	cdev_init(struct cdev*,struct file_operations*);
3) 向系统添加字符设备
	cdev_add(struct cdev*,devno,count);
4) 实现file_operations中成员；
   open(),read(),write(),llseek(),ioctl(),release()...
5)	删除字符设备.取消设备号注册
	cdev_del(struct cdev*);
unregister_chrdev_region(devno,count);
6) 插入模块到内核
insmod	xxx.ko
7) 创建字符设备文件
mknod /dev/xxx c major minor 
*/


#include <linux/init.h>
#include <linux/module.h>
#include <sys/types.h>
#include <asm/uaccess.h>
#include <linux/cdev.h>

#define MAXSIZE		1024

MODULE_LICENSE("Dual BSD/GPL");

static struct xhmem_dev{
	struct cdev cdev;
	char	mem[MAXSIZE];
};

static struct xhmem_dev		dev;	

static int xh_open(struct innode *inodep,struct file *filep)
{
	return 0;
}

static int xh_release(struct innode *inodep,struct file *filep)
{
	return 0;
}

ssize_t	xh_read(struct file *filep,char *userbuf,size_t count,loff_t *pos)
{
	int		ret;
	
	if(count > MAXSIZE)
		return count ? -1 : 0;
	if(copy_to_user(userbuf,mem,count)){
		printk(KERN_ERR "copy_to_user! error!\n");
		ret = -1;
	}else {
		ret = count;
	}
	printk(KERN_INFO "%d bytes readed success!\n",count);
	return 0;
}

sisze_t xh_write(struct file *filep,char *userbuf,size_t count,loff_t *pos)
{
	int		ret;

	if(count > MAXSIZE)
		return count ? -1:0;
	if(copy_from_user(mem,userbuf,count)) {
		printk(KERN_ERR "copy_to_user error!\n");
		ret = -1;
	}

}

struct file_operations {
	.open = xh_open,
	.read = xh_read,
	.write = xh_write,
	.llseek = xh_llseek,
	.ioctl = xh_ioctl,
	.release = xh_release
};

static int xh_init(void)
{
	int		ret;
	dev_t	devno =	MKDEV(xhmem_major,0);

	if(xhmem_major){
		ret = register_chrdev_region(devno,1,"xhmem");
	}else {
		ret = alloc_chrdev_region(devno,0,1,"xhmem");
		xhmem_major = MAJOR(devno);
	}
	if(ret < 0){
		printk(KERN_ERR "register_chrdev_region error!\n");
		return -1;
	}

	cdev_init(&dev.cdev,&fops);
	cdev_add(&dev.cdev,devno.1);
}

static void xh_exit(void)
{
}

module_init(xh_init);
module_exit(xh_exit);
