#include <linux/init.h>
#include <linux/module.h>
#include <linux/types.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <asm/uaccess.h>

MODULE_LICENSE("Dual BSD/GPL");

#define MAXSIZE		1024
#define	MEM_CLEAR	1

static int globalmem_major = 200;
struct globalmem_dev{
	struct cdev		cdev;
	char			mem[MAXSIZE];
};
struct globalmem_dev dev;

static int globalmem_open(struct inode *inodep,struct file *filep)
{
	return 0;
}

static int globalmem_release(struct inode *inodep,struct file *filep)
{
	return 0;
}

ssize_t globalmem_read(struct file *filep,char *userbuf,size_t count,loff_t *pos)
{
	int		ret;
	unsigned long p = *pos;

	if(p >= MAXSIZE)
		return count ? -1 : 0;
	if(count > MAXSIZE -p){
		count = MAXSIZE - p;
	}
	if(copy_to_user(userbuf,dev.mem + p, count)){
		printk(KERN_ERR "copy_to_user error!\n");
		ret = -1;
	}else {
		*pos += count;
		ret = count;
		printk(KERN_INFO "read %d bytes to %ld success!\n",count,p);
	}
	return ret;
}

ssize_t globalmem_write(struct file *filep,const char *userbuf,size_t count,loff_t *pos)
{
	int		ret = 0;
	unsigned long p = *pos;

	if(p >= MAXSIZE)
		return count ? -1 : 0;
	if(count > MAXSIZE -p)
		count = MAXSIZE - p;
	if(copy_from_user(dev.mem + p,userbuf,count)){
		printk(KERN_ERR "copy_from_user error!\n");
		ret = -1;
	}else {
		*pos += count;
		ret = count;
		printk(KERN_INFO "write %d bytes from %ld sucess!\n",count,p);
	}
	return ret;
}

loff_t globalmem_llseek(struct file *filep,loff_t offset,int flag)
{
	loff_t	ret;

	switch(flag){
		case	0:
			if((unsigned long)offset > MAXSIZE)
				return -1;
			filep->f_pos = offset;
			ret	= filep->f_pos;
			break;
		case	1:
			if((filep->f_pos + offset) > MAXSIZE)
				return -1;
			filep->f_pos += offset;
			ret = filep->f_pos;
			break;
		case	2:
			if(filep->f_pos ==  MAXSIZE){
				return -1;
			filep->f_pos = MAXSIZE - offset;
			ret = filep->f_pos;
			}
		default:
			return -1;
	}
	return ret;
}

int globalmem_ioctl(struct inode *inodep,struct file *filep,unsigned int cmd, unsigned long arg)
{
	switch(cmd) {
		case MEM_CLEAR:
			memset(dev.mem,0,MAXSIZE);
			printk(KERN_INFO "memory clear zero success!\n");
			break;
			//...
		default:
			return -1;
	}
	return 0;
}

struct file_operations fops = {
	.owner = THIS_MODULE,
	.open  = globalmem_open,
	.read  = globalmem_read,
	.write = globalmem_write,
	.llseek = globalmem_llseek,
	.ioctl = globalmem_ioctl,
	.release = globalmem_release
};

static int globalmem_init(void)
{
	int		ret;

	dev_t	 devno = MKDEV(globalmem_major,0);
	if (globalmem_major){
		ret = register_chrdev_region(devno,1,"globalmem");
	}else {
		ret = alloc_chrdev_region(&devno,0,1,"globalmem");
		globalmem_major = MAJOR(devno);
	}
	if(ret < 0){
		printk(KERN_ERR "register device no error!\n");
		return -1;
	}

	cdev_init(&dev.cdev,&fops);
	dev.cdev.owner = THIS_MODULE;
	dev.cdev.ops = &fops;
	if(cdev_add(&dev.cdev,devno,1)){
		printk(KERN_ERR "cdev_add error!\n");
		unregister_chrdev_region(devno,1);
		return -1;
	}

	memset(dev.mem,0,MAXSIZE);
	printk(KERN_ERR "global_init success!\n");
	return 0;
}

static void globalmem_exit(void)
{
	cdev_del(&dev.cdev);
	unregister_chrdev_region(MKDEV(globalmem_major,0),1);
	printk(KERN_INFO "cdev_del success!\n");
}

module_init(globalmem_init);
module_exit(globalmem_exit);
module_param(globalmem_major,int,S_IRUGO);

