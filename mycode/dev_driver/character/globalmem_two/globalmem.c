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
struct globalmem_dev *globalmem_devp;

static int globalmem_open(struct inode *inodep,struct file *filep)
{
	struct globalmem_dev *devp; 
	devp = container_of(inodep->i_cdev,struct globalmem_dev,cdev);
	filep->private_data = devp;
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
	struct globalmem_dev *dev = filep->private_data;

	if(p >= MAXSIZE)
		return count ? -1 : 0;
	if(count > MAXSIZE -p){
		count = MAXSIZE - p;
	}
	if(copy_to_user(userbuf,dev->mem + p, count)){
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
	struct globalmem_dev *dev = filep->private_data;

	if(p >= MAXSIZE)
		return count ? -1 : 0;
	if(count > MAXSIZE -p)
		count = MAXSIZE - p;
	if(copy_from_user(dev->mem + p,userbuf,count)){
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
		default:
			return -1;
	}
	return ret;
}

int globalmem_ioctl(struct inode *inodep,struct file *filep,unsigned int cmd, unsigned long arg)
{
	struct globalmem_dev *dev = filep->private_data;

	switch(cmd) {
		case MEM_CLEAR:
			memset(dev->mem,0,MAXSIZE);
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

static void globalmem_cdev_setup(struct globalmem_dev *devp,int minor)
{
	dev_t	devno =	MKDEV(globalmem_major,minor);

	cdev_init(&devp->cdev,&fops);
	devp->cdev.owner = THIS_MODULE;
	devp->cdev.ops = &fops;
	if(cdev_add(&devp->cdev,devno,1)){
		printk(KERN_ERR "cdev_add error!\n");
	}
}

static int globalmem_init(void)
{
	int		ret;

	dev_t	 devno = MKDEV(globalmem_major,0);
	if (globalmem_major){
		ret = register_chrdev_region(devno,2,"globalmem");
	}else {
		ret = alloc_chrdev_region(&devno,0,2,"globalmem");
		globalmem_major = MAJOR(devno);
	}
	if(ret < 0){
		printk(KERN_ERR "register device no error!\n");
		return -1;
	}

	globalmem_devp = (struct globalmem_dev *)kmalloc(sizeof(struct globalmem_dev) * 2,GFP_KERNEL);	
	if(globalmem_devp == NULL){
		printk(KERN_ERR "kmalloc error!\n");
		unregister_chrdev_region(devno,2);
		return -1;
	}
	memset(globalmem_devp,0,sizeof(struct globalmem_dev) * 2);
//	memset(globalmem_devp->mem,0,MAXSIZE);
//	printk(KERN_ERR "global_init success!\n");
	globalmem_cdev_setup(&globalmem_devp[0],0);
	globalmem_cdev_setup(&globalmem_devp[1],1);
	return 0;
}

static void globalmem_exit(void)
{
	cdev_del(&globalmem_devp[0].cdev);
	cdev_del(&globalmem_devp[1].cdev);
	kfree(globalmem_devp);
	unregister_chrdev_region(MKDEV(globalmem_major,0),2);
	printk(KERN_INFO "cdev_del success!\n");
}

module_init(globalmem_init);
module_exit(globalmem_exit);
module_param(globalmem_major,int,S_IRUGO);

