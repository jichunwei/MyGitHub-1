'''
Steps
1. make the testbed with given info
2. call all the addtestsuite scripts sequentially

'''
import copy
import os
from pprint import pformat

import libFM_TestSuite as testsuite


internal_cfg = ['imported_testsuites', 'usage', 'input']

unaccepted_cfg_error = '''
ERROR: You have just input some params which is not supported by this script:
   %s
'''

testbed_cfg = dict(
    name = '',
    location = 'RuckusWireless',
    owner = 'admin',
    FM= dict(
            ip_addr='192.168.30.252',
            username='admin@ruckus.com',
            password='admin',
            model='fm',
            browser_type='firefox',
        ),
    Clients=[]
)


def generate_ts_interactively(testbed, testsuites=[]):
    '''
    . run in interactive mode for each test scripts
    . Input:
    .         list of test script name
    '''
    for ts in testsuites:
        os.system('%s%s name=%s' % (ts,'.py',testbed))


def get_running_mode(accepted_ks, input):
    '''
    . did operator input the required information? if not, then prompt them
    '''
    unaccepted_cfg = [i for i in input if i not in accepted_ks]
    if unaccepted_cfg:
        print unaccepted_cfg_error % unaccepted_cfg
        return 'usage'

    if ('is_interactive' in input) and input['is_interactive'] :
        return 'interactive'

    return 'auto'


def add_test_script(**kwa):
    '''
    . Run in automatic mode
    . Import each test script and add into test bed with its test cases
    . Input:   kwa:
        {'imported_testsuites': [
            {'ts': '<test script name>', 'ignoreModel': <False|True>},
          ],
          'name': '<test bed name>',
          'Clients': [],
          '<arguments of each test bed>': '<arg value>',
          'owner': '<owner name>',
          'device': '<kind of devices used in this test: APs | ZDs>',
          'location': '<RuckusWireless>',
          'is_interactive': <interactive mode True|False>,
          'usage': "<show the way to use this script>",
          'FM': {'username': 'admin@ruckus.com',
                 'browser_type': 'firefox',
                 'model': 'fm',
                 'password': 'admin',
                 'ip_addr': '192.168.30.252'}}
    '''
    failed_ts = []
    for ts_info in kwa['imported_testsuites']:
        try:
            ts = __import__(ts_info['ts'])
            kwa.update({'define_ts_cfg':ts.define_ts_cfg,
                        'ignoreModel':ts_info['ignoreModel']})
            if not ts_info['ignoreModel']:
                kwa['define_device_type'] = ts.define_device_type
            ts.make_test_suite(**kwa)
        except:
            failed_ts.append(ts_info['ts'])

    print '\n-- SUMMARY:\n' \
          '  Testbed: %(name)s\n' \
          '  Successfully added %(total_added)s/%(total)s test scripts\n' % \
          dict(
              name = kwa['name'],
              total = len(kwa['imported_testsuites']),
              total_added = len(kwa['imported_testsuites']) - len(failed_ts),
          )

    if failed_ts:
        print '  Failed to add testsuites:\n  %s' % pformat(failed_ts)


def get_accepted_key(**testbed_info):
    '''
    . Get accepted arguments for each test bed
    '''
    return [k for k in testbed_info.keys() if k not in internal_cfg]


def define_logical_testbed(**testbed_info):
    '''
    . Define a logical testbed
      . create a testbed
      . add its belonging test suites

    testbed_info:
        {'device': 'ZDs',
         'imported_testsuites': [{'ignoreModel': <True|False>,
                                  'ts': '<>'}],
         'is_interactive': <True|False>,
         '<arguments>': '<arg value>',
         'name': '<testbed name>',
         'usage': "<show the way to use this script>"}
    '''
    running_mode = get_running_mode(get_accepted_key(**testbed_info),
                                    testbed_info['input'])

    input = copy.deepcopy(testbed_info['input'])
    del testbed_info['input']
    testbed_info.update(input)

    if running_mode == 'usage':
        print testbed_info['usage']
        exit()

    # interactive or auto will reach here, call the generation code
    print('Your config:\n%s' % pformat(testbed_info))

    tb_name = input.get('name',testsuite.input_with_default("Your test bed name",
                                                            testbed_info['name']))

    testbed_info['name'] = tb_name
    testbed_cfg.update(testbed_info)

    # create a logical testbed
    testsuite.get_fm_testbed(**testbed_cfg)

    if running_mode == 'auto':
        add_test_script(**testbed_cfg)
        exit()

    # interactive mode
    testsuites = [v['ts'] for v in testbed_cfg['imported_testsuites']]
    generate_ts_interactively(tb_name, testsuites)

