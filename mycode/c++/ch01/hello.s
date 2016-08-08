	.file	"hello.cpp"
	.text
	.type	_Z41__static_initialization_and_destruction_0ii, @function
_Z41__static_initialization_and_destruction_0ii:
.LFB993:
	pushl	%ebp
.LCFI0:
	movl	%esp, %ebp
.LCFI1:
	subl	$24, %esp
.LCFI2:
	cmpl	$1, 8(%ebp)
	jne	.L3
	cmpl	$65535, 12(%ebp)
	jne	.L3
	movl	$_ZStL8__ioinit, (%esp)
	call	_ZNSt8ios_base4InitC1Ev
	movl	$_ZNSt8ios_base4InitD1Ev, %eax
	movl	$__dso_handle, 8(%esp)
	movl	$_ZStL8__ioinit, 4(%esp)
	movl	%eax, (%esp)
	call	__cxa_atexit
.L3:
	leave
	ret
.LFE993:
	.size	_Z41__static_initialization_and_destruction_0ii, .-_Z41__static_initialization_and_destruction_0ii
	.type	_GLOBAL__I_main, @function
_GLOBAL__I_main:
.LFB994:
	pushl	%ebp
.LCFI3:
	movl	%esp, %ebp
.LCFI4:
	subl	$8, %esp
.LCFI5:
	movl	$65535, 4(%esp)
	movl	$1, (%esp)
	call	_Z41__static_initialization_and_destruction_0ii
	leave
	ret
.LFE994:
	.size	_GLOBAL__I_main, .-_GLOBAL__I_main
	.section	.ctors,"aw",@progbits
	.align 4
	.long	_GLOBAL__I_main
	.section	.rodata
.LC0:
	.string	"\345\276\220\345\256\217!"
.LC1:
	.string	"Hello world!"
.LC2:
	.string	"name:"
.LC3:
	.string	"age:"
.LC4:
	.string	"Please input two number:"
.LC5:
	.string	"sum:"
.globl _Unwind_Resume
	.text
.globl main
	.type	main, @function
main:
.LFB952:
	leal	4(%esp), %ecx
.LCFI6:
	andl	$-16, %esp
	pushl	-4(%ecx)
.LCFI7:
	pushl	%ebp
.LCFI8:
	movl	%esp, %ebp
.LCFI9:
	pushl	%esi
.LCFI10:
	pushl	%ebx
.LCFI11:
	pushl	%ecx
.LCFI12:
	subl	$60, %esp
.LCFI13:
	leal	-21(%ebp), %eax
	movl	%eax, (%esp)
	call	_ZNSaIcEC1Ev
	leal	-21(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	$.LC0, 4(%esp)
	leal	-28(%ebp), %eax
	movl	%eax, (%esp)
.LEHB0:
	call	_ZNSsC1EPKcRKSaIcE
.LEHE0:
	leal	-21(%ebp), %eax
	movl	%eax, (%esp)
	call	_ZNSaIcED1Ev
	movl	$10, -20(%ebp)
	movl	$0, -16(%ebp)
	movl	$.LC1, 4(%esp)
	movl	$_ZSt4cout, (%esp)
.LEHB1:
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
	movl	%eax, %edx
	leal	-28(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
	call	_ZStlsIcSt11char_traitsIcESaIcEERSt13basic_ostreamIT_T0_ES7_RKSbIS4_S5_T1_E
.LEHE1:
	jmp	.L13
.L12:
	movl	%eax, -52(%ebp)
	movl	%edx, -48(%ebp)
.L8:
	movl	-48(%ebp), %esi
	movl	-52(%ebp), %ebx
	leal	-21(%ebp), %eax
	movl	%eax, (%esp)
	call	_ZNSaIcED1Ev
	movl	%ebx, -52(%ebp)
	movl	%esi, -48(%ebp)
	movl	-52(%ebp), %eax
	movl	%eax, (%esp)
.LEHB2:
	call	_Unwind_Resume
.LEHE2:
.L13:
	movl	%eax, %edx
	movl	-20(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
.LEHB3:
	call	_ZNSolsEi
	movl	$_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_, 4(%esp)
	movl	%eax, (%esp)
	call	_ZNSolsEPFRSoS_E
	movl	$.LC2, 4(%esp)
	movl	$_ZSt4cout, (%esp)
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
	movl	%eax, %edx
	leal	-28(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
	call	_ZStlsIcSt11char_traitsIcESaIcEERSt13basic_ostreamIT_T0_ES7_RKSbIS4_S5_T1_E
	movl	$_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_, 4(%esp)
	movl	%eax, (%esp)
	call	_ZNSolsEPFRSoS_E
	movl	$.LC3, 4(%esp)
	movl	$_ZSt4cout, (%esp)
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
	movl	%eax, %edx
	movl	-20(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
	call	_ZNSolsEi
	movl	$_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_, 4(%esp)
	movl	%eax, (%esp)
	call	_ZNSolsEPFRSoS_E
	movl	$.LC4, 4(%esp)
	movl	$_ZSt4cout, (%esp)
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
	leal	-32(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$_ZSt3cin, (%esp)
	call	_ZNSirsERi
	movl	%eax, %edx
	leal	-36(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
	call	_ZNSirsERi
	movl	-32(%ebp), %eax
	movl	-36(%ebp), %edx
	addl	%edx, %eax
	movl	%eax, -16(%ebp)
	movl	$.LC5, 4(%esp)
	movl	$_ZSt4cout, (%esp)
	call	_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
	movl	%eax, %edx
	movl	-16(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	%edx, (%esp)
	call	_ZNSolsEi
	movl	$_ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_, 4(%esp)
	movl	%eax, (%esp)
	call	_ZNSolsEPFRSoS_E
.LEHE3:
	movl	$0, %ebx
	leal	-28(%ebp), %eax
	movl	%eax, (%esp)
.LEHB4:
	call	_ZNSsD1Ev
.LEHE4:
	movl	%ebx, %eax
	addl	$60, %esp
	popl	%ecx
	popl	%ebx
	popl	%esi
	popl	%ebp
	leal	-4(%ecx), %esp
	ret
.L11:
	movl	%eax, -52(%ebp)
	movl	%edx, -48(%ebp)
.L9:
	movl	-48(%ebp), %esi
	movl	-52(%ebp), %ebx
	leal	-28(%ebp), %eax
	movl	%eax, (%esp)
	call	_ZNSsD1Ev
	movl	%ebx, -52(%ebp)
	movl	%esi, -48(%ebp)
	movl	-52(%ebp), %eax
	movl	%eax, (%esp)
.LEHB5:
	call	_Unwind_Resume
.LEHE5:
.LFE952:
	.size	main, .-main
.globl __gxx_personality_v0
	.section	.gcc_except_table,"a",@progbits
.LLSDA952:
	.byte	0xff
	.byte	0xff
	.byte	0x1
	.uleb128 .LLSDACSE952-.LLSDACSB952
.LLSDACSB952:
	.uleb128 .LEHB0-.LFB952
	.uleb128 .LEHE0-.LEHB0
	.uleb128 .L12-.LFB952
	.uleb128 0x0
	.uleb128 .LEHB1-.LFB952
	.uleb128 .LEHE1-.LEHB1
	.uleb128 .L11-.LFB952
	.uleb128 0x0
	.uleb128 .LEHB2-.LFB952
	.uleb128 .LEHE2-.LEHB2
	.uleb128 0x0
	.uleb128 0x0
	.uleb128 .LEHB3-.LFB952
	.uleb128 .LEHE3-.LEHB3
	.uleb128 .L11-.LFB952
	.uleb128 0x0
	.uleb128 .LEHB4-.LFB952
	.uleb128 .LEHE4-.LEHB4
	.uleb128 0x0
	.uleb128 0x0
	.uleb128 .LEHB5-.LFB952
	.uleb128 .LEHE5-.LEHB5
	.uleb128 0x0
	.uleb128 0x0
.LLSDACSE952:
	.text
	.local	_ZStL8__ioinit
	.comm	_ZStL8__ioinit,1,1
	.weakref	_ZL20__gthrw_pthread_oncePiPFvvE,pthread_once
	.weakref	_ZL27__gthrw_pthread_getspecificj,pthread_getspecific
	.weakref	_ZL27__gthrw_pthread_setspecificjPKv,pthread_setspecific
	.weakref	_ZL22__gthrw_pthread_createPmPK14pthread_attr_tPFPvS3_ES3_,pthread_create
	.weakref	_ZL22__gthrw_pthread_cancelm,pthread_cancel
	.weakref	_ZL26__gthrw_pthread_mutex_lockP15pthread_mutex_t,pthread_mutex_lock
	.weakref	_ZL29__gthrw_pthread_mutex_trylockP15pthread_mutex_t,pthread_mutex_trylock
	.weakref	_ZL28__gthrw_pthread_mutex_unlockP15pthread_mutex_t,pthread_mutex_unlock
	.weakref	_ZL26__gthrw_pthread_mutex_initP15pthread_mutex_tPK19pthread_mutexattr_t,pthread_mutex_init
	.weakref	_ZL30__gthrw_pthread_cond_broadcastP14pthread_cond_t,pthread_cond_broadcast
	.weakref	_ZL25__gthrw_pthread_cond_waitP14pthread_cond_tP15pthread_mutex_t,pthread_cond_wait
	.weakref	_ZL26__gthrw_pthread_key_createPjPFvPvE,pthread_key_create
	.weakref	_ZL26__gthrw_pthread_key_deletej,pthread_key_delete
	.weakref	_ZL30__gthrw_pthread_mutexattr_initP19pthread_mutexattr_t,pthread_mutexattr_init
	.weakref	_ZL33__gthrw_pthread_mutexattr_settypeP19pthread_mutexattr_ti,pthread_mutexattr_settype
	.weakref	_ZL33__gthrw_pthread_mutexattr_destroyP19pthread_mutexattr_t,pthread_mutexattr_destroy
	.section	.eh_frame,"a",@progbits
.Lframe1:
	.long	.LECIE1-.LSCIE1
.LSCIE1:
	.long	0x0
	.byte	0x1
	.string	"zPL"
	.uleb128 0x1
	.sleb128 -4
	.byte	0x8
	.uleb128 0x6
	.byte	0x0
	.long	__gxx_personality_v0
	.byte	0x0
	.byte	0xc
	.uleb128 0x4
	.uleb128 0x4
	.byte	0x88
	.uleb128 0x1
	.align 4
.LECIE1:
.LSFDE1:
	.long	.LEFDE1-.LASFDE1
.LASFDE1:
	.long	.LASFDE1-.Lframe1
	.long	.LFB993
	.long	.LFE993-.LFB993
	.uleb128 0x4
	.long	0x0
	.byte	0x4
	.long	.LCFI0-.LFB993
	.byte	0xe
	.uleb128 0x8
	.byte	0x85
	.uleb128 0x2
	.byte	0x4
	.long	.LCFI1-.LCFI0
	.byte	0xd
	.uleb128 0x5
	.align 4
.LEFDE1:
.LSFDE5:
	.long	.LEFDE5-.LASFDE5
.LASFDE5:
	.long	.LASFDE5-.Lframe1
	.long	.LFB952
	.long	.LFE952-.LFB952
	.uleb128 0x4
	.long	.LLSDA952
	.byte	0x4
	.long	.LCFI6-.LFB952
	.byte	0xc
	.uleb128 0x1
	.uleb128 0x0
	.byte	0x9
	.uleb128 0x4
	.uleb128 0x1
	.byte	0x4
	.long	.LCFI7-.LCFI6
	.byte	0xc
	.uleb128 0x4
	.uleb128 0x4
	.byte	0x4
	.long	.LCFI8-.LCFI7
	.byte	0xe
	.uleb128 0x8
	.byte	0x85
	.uleb128 0x2
	.byte	0x4
	.long	.LCFI9-.LCFI8
	.byte	0xd
	.uleb128 0x5
	.byte	0x4
	.long	.LCFI12-.LCFI9
	.byte	0x84
	.uleb128 0x5
	.byte	0x83
	.uleb128 0x4
	.byte	0x86
	.uleb128 0x3
	.align 4
.LEFDE5:
	.ident	"GCC: (Debian 4.3.2-1.1) 4.3.2"
	.section	.note.GNU-stack,"",@progbits
