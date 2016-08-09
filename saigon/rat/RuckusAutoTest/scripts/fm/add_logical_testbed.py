import os
from libFM_TestSuite import select_item, input_with_default


testbed_arg = dict(
   mk_configure_testbed = dict(is_interactive=False,
                               ftp=dict(username='root',passwd='lab4man1')),
   mk_deviceview_testbed = dict(is_interactive=False,),
   mk_zds_testbed =  dict(is_interactive=False,
                          map_path='D:\map1.png'),
   mk_dualband_testbed = dict(is_interactive=False,),
   mk_behavior_testbed = dict(is_interactive=False,),
   mk_autoconfig_testbed = dict(is_interactive=False,),
   mk_ratclient_testbed = dict(is_interactive=False,
                               Clients=['192.168.30.252']),
                   )

def input_testbed(tbs):
    '''
    .  List out all logical testbed and let's user choose them.
    .  Input:
    .        tbs: list of testbed script file name
    '''
    print 'Available logical testbed:\n%s' % \
          '\n'.join(['  %s - %s' % (i, v) for i, v in enumerate(tbs)])
    sel_tb = raw_input(
            'Select logical testbed (seperate by a space) or all [all]: ').strip()

    if sel_tb.lower() in ('all', ''):
        sel_tb = tbs
    else:
        sel_tb = sel_tb.split(' ')
        sel_tb = [tbs[int(x)] for x in sel_tb]
    return sel_tb

def execute_logical():
    interactive_edit_arg = False
    sel_tb = input_testbed(testbed_arg.keys())
    interactive_edit_arg = input_with_default(
                           "Enter arguments in interactive mode  "
                           ,interactive_edit_arg)
    for tb in sel_tb:
        str_testbed = "%s.py" % tb
        print 'Generate %s logical testbed ..........' % (tb)
        for k_arg, v_arg in testbed_arg[tb].items():
            if interactive_edit_arg:
                testbed_arg[tb][k_arg] = \
                str(input_with_default("Enter %s" %(k_arg), v_arg)).replace(' ','')

            str_testbed = str_testbed + ' %s=%s' % \
                         (k_arg, str(testbed_arg[tb][k_arg]).replace(' ','') )
        os.system(str_testbed)

    return input_with_default('Do you want to continue?', 'y')

if __name__ == '__main__':
    while execute_logical() == 'y':
        pass


