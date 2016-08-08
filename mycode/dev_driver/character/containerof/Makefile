ifneq ($(KERNELRELEASE),)
	obj-m := containerof.o
else
	KERNELDIR ?= /lib/modules/$(shell uname -r)/build
	PWD := $(shell pwd)
default:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules
endif

clean:
	rm -rf *.ko *.o Module.* *.mod.* *.order
