#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
 .name = KBUILD_MODNAME,
 .init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
 .exit = cleanup_module,
#endif
 .arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x83df6f39, "struct_module" },
	{ 0xa5423cc4, "param_get_int" },
	{ 0xcb32da10, "param_set_int" },
	{ 0x2da418b5, "copy_to_user" },
	{ 0x994e1983, "__wake_up" },
	{ 0xf2a644fb, "copy_from_user" },
	{ 0xdb8bd46f, "down" },
	{ 0x5878e0d0, "finish_wait" },
	{ 0x4292364c, "schedule" },
	{ 0x2caa52dc, "prepare_to_wait" },
	{ 0xdd503bfb, "per_cpu__current_task" },
	{ 0xc8b57c27, "autoremove_wake_function" },
	{ 0x381da1, "up" },
	{ 0x79101ee3, "cdev_add" },
	{ 0x39a4a86, "cdev_init" },
	{ 0xffd3c7, "init_waitqueue_head" },
	{ 0x529c3dd6, "kmem_cache_alloc" },
	{ 0xeb1de92, "malloc_sizes" },
	{ 0x29537c9e, "alloc_chrdev_region" },
	{ 0xd8e484f0, "register_chrdev_region" },
	{ 0x1b7d4074, "printk" },
	{ 0x7485e15e, "unregister_chrdev_region" },
	{ 0x37a0cba, "kfree" },
	{ 0xb3a26be, "cdev_del" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

