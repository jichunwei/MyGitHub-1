'''
Testsuite: Device Registration (list tcs of this testsuite)

Auto ID    Manual ID
1.2.3.1    1.1.7.2.1    Admin denied
1.2.3.2    1.1.7.2.2    Permitted
1.2.3.3    1.1.7.2.3    RMA
1.2.3.4    1.1.7.2.4    Unavailable
1.2.3.5    1.1.7.2.5    Upload a device inventory file by Manufacturing data
1.2.3.7    1.1.7.2.6    Upload a device inventory file twice by pre-registration data with same serial number
1.2.3.8    1.1.7.2.6    Upload a device inventory file twice by Manufacturing data with same serial number
1.2.3.9    1.1.7.2.7    Save this inventory as XLS test

'''

import sys
import copy
from pprint import pprint

from libFM_TestSuite import start_fm, model_map, make_test_suite, \
        get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict


def get_fm_version(fm_cfg):
    '''
    '''
    sm, fm = start_fm(**fm_cfg)
    version = fm.get_version()
    fm.stop()
    sm.shutdown()
    del sm, fm

    return version


def get_specific_tcs(version='8.2'):
    '''
    This function is to rmove tcs relate "Manufacturing data". It is not available
    on version FM 9.
    '''
    MANUFACT_MODE = 'manufact'
    PREREG_MODE   = 'pre_regist'
    '''
        - data_matrix for pre_regist mode:
            [
                ['serial number 1', 'its tag'], # line 1
                ['serial number 2', 'its tag'], # line 2
                ....
            ]
        - data_matrix for manufact mode:
            [
                ['serial number 1', 'model', 'number', 'special string'], # line 1
                ['serial number 1', 'model', 'number', 'special string'], # line 2
                ....
            ]
    '''
    specific_manufact_tcs = [
        [
            'TCID:01.02.03.05 - Upload Inventory file by Manufacturing data',
            'FM_RegStatusUploadInvenFile',
            {
                'data_matrix': [], # this param empty means let the test script generate
                                  # list of device to avoid duplication
                'mode': MANUFACT_MODE,
                'no_devices': 3,
            },
        ],
        [
            'TCID:01.02.03.08 - Upload a device inventory file twice by Manufacturing'
            ' data with same serial number',
            'FM_RegStatusUploadInvenFileTwice',
            dict(
                data_matrix = [], # this param empty means let the test script generate
                                  # list of device to avoid duplication
                upload_mode = MANUFACT_MODE, # 'manufact'|'prereg' manufacturing data
                no_devices = 2,
            ),
        ],
    ]

    tc_templates = [
      [ 'TCID:01.02.03.07 - Upload a device inventory file twice by pre-registration'
        ' data with same serial number',
        'FM_RegStatusUploadInvenFileTwice',
        dict(
            data_matrix = [], # this param empty means let the test script generate
                              # list of device to avoid duplication
            upload_mode = PREREG_MODE, # 'manufact'|'prereg' manufacturing data
            no_devices = 2,
        ),
      ],
      [ 'TCID:01.02.03.09 - Save this inventory as XLS test',
        'FM_RegStatusSaveInvenFile',
        {
            'file_name':'inventory.xls',
        },
      ],
    ]

    if version < '9.0':
        tc_templates.append(specific_manufact_tcs)

    return tc_templates


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    tbCfg = eval(kwa['testbed'].config)
    aps = get_aps_by_models(kwa['models'], tbCfg)

    tc_id = [
            '01.02.03.01', '01.02.03.02', '01.02.03.03', '01.02.03.04',
            ]

    template = [ 'TCID:%s.%s - Change Inventory status to %s - %s',
        'FM_RegStatusMgmt',
        {
            'status':'%s',
            'comment':'Change status to %s',
            'ip_addr':'%s',
            'licenses_consume':'%s'
        }
    ]

    tcs = {
       '01.02.03.01' : 'Admin Denied',
       '01.02.03.02' : 'Permitted',
       '01.02.03.03' : 'RMA',
       '01.02.03.04' : 'Unavailable',
    }

    model_license_map = dict([(model,'1') for model in kwa['models']])

    tbCfg = eval(kwa['testbed'].config)
    fm_cfg = tbCfg['FM']
    tc_templates = get_specific_tcs(get_fm_version(fm_cfg))

    for model in kwa['models']:
        for tcid in tc_id:
            list_ip_of_model = aps[model] if model in aps else []
            if list_ip_of_model:
                for ip in list_ip_of_model:
                    temp = copy.deepcopy(template)

                    temp[0] = temp[0] % (tcid, model_map[model],tcs[tcid],
                                         model.upper())
                    temp[2]['status'] = tcs[tcid]
                    temp[2]['comment'] = temp[2]['comment'] % tcs[tcid]
                    temp[2]['ip_addr'] = ip
                    temp[2]['licenses_consume'] = model_license_map[model]
                    pprint(temp)
                    tc_templates.append(temp)

    print 'Generate test cases for Device Registration testsuite\n'
    test_cfgs = {}
    for template in tc_templates:
        tc = copy.deepcopy(template)
        test_cfgs[template[0]] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Inventory - Device Registration', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)




#===============================================================================
# [ 'TCID:01.02.03.01 - Change Inventory status to Admin denied',
#        'FM_RegStatusMgmt',
#        {
#            'status':'Admin Denied',
#            'comment':'Change status to Admin Denied'
#        },
#      ],
#      [ 'TCID:01.02.03.02 - Change Inventory status to Permitted',
#        'FM_RegStatusMgmt',
#        {
#            'status':'Permitted',
#            'comment':'Change status to Permitted'
#        },
#      ],
#      [ 'TCID:01.02.03.03 - Change Inventory status to RMA',
#        'FM_RegStatusMgmt',
#        {
#            'status':'RMA',
#            'comment':'Change status to RMA'
#        },
#      ],
#      [ 'TCID:01.02.03.04 - Change Inventory status to Unavailable',
#        'FM_RegStatusMgmt',
#        {
#            'status':'Unavailable',
#            'comment':'Change status to Unavailable'
#        },
#      ],
#===============================================================================
