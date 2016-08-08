	.file	"test1.c"
	.section	.rodata
.LC3:
	.string	"%f, %f"
	.text
.globl main
	.type	main, @function
main:
	leal	4(%esp), %ecx
	andl	$-16, %esp
	pushl	-4(%ecx)
	pushl	%ebp
	movl	%esp, %ebp
	pushl	%ecx
	subl	$52, %esp
	movl	$0x41200000, %eax
	movl	%eax, -8(%ebp)
	flds	-8(%ebp)
	fldl	.LC1
	fmulp	%st, %st(1)
	flds	-8(%ebp)
	fmulp	%st, %st(1)
	fstps	-12(%ebp)
	flds	-8(%ebp)
	fldl	.LC2
	fmulp	%st, %st(1)
	fstps	-16(%ebp)
	flds	-16(%ebp)
	flds	-12(%ebp)
	fxch	%st(1)
	fstpl	12(%esp)
	fstpl	4(%esp)
	movl	$.LC3, (%esp)
	call	printf
	movl	$0, %eax
	addl	$52, %esp
	popl	%ecx
	popl	%ebp
	leal	-4(%ecx), %esp
	ret
	.size	main, .-main
	.section	.rodata
	.align 8
.LC1:
	.long	1374389535
	.long	1074339512
	.align 8
.LC2:
	.long	1374389535
	.long	1075388088
	.ident	"GCC: (Debian 4.3.2-1.1) 4.3.2"
	.section	.note.GNU-stack,"",@progbits
