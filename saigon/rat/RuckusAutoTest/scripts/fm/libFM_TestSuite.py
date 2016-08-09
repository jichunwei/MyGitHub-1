'''
REQUIREMENTs for addtestsuite_*.py:
- The script should detect the number of APs and their models
  which you should use to create test suite/cases.
- The test suite should prompt the user for which AP's to create test cases
  (default 'all' - all available models).
- The test structure in the addtestsuite_xxx.py should be geared
  so if a new AP is introduced, just added a AP model and each test's TCID.

TODO: Clean up this file, move functions to libraries
'''


import os
import sys
import tarfile
import re
import copy
from pprint import pformat

debug_tslib = True if os.environ.has_key('RAT_DEBUG_TESTSUITE') else False

from django.core.management import setup_environ
rat_path = os.path.realpath(os.path.join(os.getcwd(), "../../.."))
sys.path.append(rat_path)
import settings
setup_environ(settings)

from django.core.exceptions import ObjectDoesNotExist
from RuckusAutoTest.models import (
        TestSuite, Testbed, TestbedType, Build, BuildStream, TestCase, TestRun,
)

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.FlexMaster  import FlexMaster
from RuckusAutoTest.common.utils import (
        compare, init_firmware_path, log, get_fws_on_local_file_system, is_in,
)
from RuckusAutoTest.common.lib_Constant import _ap_model_id, single_band, \
                                    dual_band, media, zd, device_models



def get_available_models(model_type, tb_cfg_model):
    '''
    .    Get available model name for test suite bases on
    .      -  model_type (list of model type (single_band, dual_band, media, zd)
    .         that are available on test suite)
    .      -  tb_cfg_model (list of model exist in testbed)
    .    Output:
    .        list of available model
    '''
    available_models = []
    for type in model_type:
        try:
            available_models = available_models + device_models[type]
        except:
            available_models.append(type)

    return [type for type in tb_cfg_model if type in available_models]


if debug_tslib:
    pfmt = "%12s: %s"
    print "\ntslib.py Runtime environment:\n"
    print pfmt % ('RUN DIR', os.getcwd())
    print pfmt % ('DATABASE', settings.DATABASE_NAME)
    print pfmt % ('TSLIB', __file__)


'''
AP Naming Convention:
. all zf models from lib_Constant: counting from 0x...
. all zd starting from 2x
. all vf starting from 4x
converting to string since FM requires string
'''
model_map = copy.deepcopy(_ap_model_id)
model_map.update(dict(
    vf7811=41,
    zd1k=21,
))

for k in model_map.iterkeys():
    model_map[k] = '%02d' % model_map[k]
#log(model_map)


'''
Some buildstreams can be filtered by adding its name
(which will be searched by re) in IgnoreStreams
'''
BuildServerInfo = dict(
    k2 = dict(
        BuildStreamUrl = 'http://k2.video54.local/cgi-bin/build_info.pl',
        BuildStreamDetailUrl = 'http://k2.video54.local/cgi-bin/build_info.pl?filename=',
        BuildStreamPrefix = 'www_',
        IgnoreStreams = ['make a selection', 'fd1000', 'mm2225', 'zd.000',
                         'ab1000', 'mainline'],
    ),
    lhotse = dict(
        BuildStreamUrl = 'http://172.16.15.221/cgi-bin/build_info.pl',
        BuildStreamDetailUrl = 'http://172.16.15.221/cgi-bin/build_info.pl?filename=',
        BuildStreamPrefix = 'www_',
        IgnoreStreams = ['make a selection', 'fd1000', 'mm2225', 'zd.000',
                         'ab1000', 'mainline'],
    ),
)


FirmwareMap = dict(fm='Flex Master', fs='File System', k2='K2', lhotse='LHotse')


testsuites = dict(
    dv_mgmt='03.02.02. Device View - Management',
    fm_cfg_reboot='01.04.08. Configure - Reboot',
    fm_admin_user='01.05.04. Administer - Users',
    fm_inv_devicemgmt='01.02.01. Inventory - Manage Devices',
    fm_inv_reports_fm='01.02.02. Inventory - Reports',
    fm_delegated_admin='07.01. Delegated Admin - Basic Operating',
    prov_reboot='Provisioning - Reboot',
)

def get_testsuitename(brief):
    return testsuites[brief]


def _filter_tcs(model, tcs, filtered_tcs):
    '''
    . filtering incompatible testcases for the given model
    '''
    if model not in filtered_tcs:
        return tcs
    return [tc for tc in tcs if tc not in filtered_tcs[model]]


def filter_tcs(models, tcs, filtered_tcs):
    '''
    . a generator, yield model and tcid after filtering out those incompatible
    '''
    for m in models:
        for tc in _filter_tcs(m, tcs, filtered_tcs):
            yield m, tc


def sort_tcfg(tcfg):
    '''
    . transform all config of testcases to a ordered list
    '''
    ks = tcfg.keys()
    ks.sort()
    return [tcfg[k] for k in ks]


def get_tcid(tc_name):
    return re.search('TCID:(.*?) -', tc_name).group(1)


def start_fm(**kwa):
    ''' start the Flex Master Web UI base on the given config '''
    cfg = dict(
        ip_addr='192.168.30.252',
        username='admin@ruckus.com',
        password='ruckus',
        model='fm',
        browser_type='firefox',
        version='8',
    )
    cfg.update(kwa)

    sm = SeleniumManager()
    fm = FlexMaster(sm, cfg['browser_type'], cfg['ip_addr'], cfg)
    fm.start()
    return sm, fm


def get_fm_devices(cfg):
    ''' start the Flex Master and get all the associated APs/ZDs '''
    sm, fm = start_fm(**cfg)
    aps = fm.get_all_aps()
    zds = fm.get_all_zds()
    fm.stop()
    sm.shutdown()
    del fm, sm
    return dict(APs=aps,ZDs=zds)


def get_testsuite(ts_name, description, interactive_mode = False):
    _name = ts_name
    if interactive_mode:
        print "\nYou can assign test suite name to same set of test case.\n" \
              "Use test suite to group your test cases."
        _name = input_with_default('Testsuite name', ts_name)

    print "Adding TestSuite %s " % _name
    try:
        ts = TestSuite.objects.get(name=_name)
        print "TestSuite '%s' is already in database." % _name
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % _name
        ts = TestSuite(name=_name, description=description)
        ts.save()
    print "Adding test cases to TestSuite %s " % ts.name
    return ts


def input_with_default(prompt, default):
    txt = raw_input('%s [%s]: ' % (prompt, default))
    if txt.strip() == '':
        return default
    return txt


def input_clients():
    clients = []
    if not compare(input_with_default('Do you want to add clients?', 'y'), 'y', 'seq'):
        return clients

    isAdded = True
    while isAdded:
        clients.append(input_with_default('Client IP', '192.168.1.11').strip())
        isAdded = compare(input_with_default('Do you want to add more?', 'n'), 'y', 'seq')

    print 'List of Clients:\n%s\n' % pformat(clients)
    return clients


def get_fm_testbed(**kwa):
    '''
    expected kwas:
      name, location, owner
      FM=dict(ip_addr,username,password,..), APs=[..], ZDs=[..], Clients=[..]
    '''
    p = dict(tbtype='SimplifiedFM_Stations')
    p.update(kwa)

    tb_name = p['name'] if 'name' in p else raw_input("Your test bed name: ")
    try:
        tb = Testbed.objects.get(name=tb_name)
    except ObjectDoesNotExist:
        tb_location = p['location'] if 'location' in p else input_with_default('Testbed location', 'RuckusWireless')
        tb_owner = p['owner'] if 'owner' in p else input_with_default('Testbed owner', 'admin')

        # note: add version option to specify which FlexMaster version is being used
        #         Will remove this code later
        tbcfg = dict(
            FM=p['FM'] if 'FM' in p else dict(
                ip_addr=input_with_default('FlexMaster IP', '192.168.30.252'),
                username=input_with_default('FlexMaster Username', 'admin@ruckus.com'),
                password=input_with_default('FlexMaster Password', 'admin'),
                model='fm',
                browser_type='firefox',
            ),
        )
        devices = get_fm_devices(tbcfg['FM']) if 'APs' not in p or 'ZDs' not in p else None
        tbcfg.update(
            APs=p['APs'] if 'APs' in p else devices['APs'],
            ZDs=p['ZDs'] if 'ZDs' in p else devices['ZDs'],
            Clients=p['Clients'] if 'Clients' in p else input_clients(),
        )

        m = re.match(r'^([^@]+)@(|[^\s]+)', tb_owner)
        if not m:
            tb_owner = tb_owner + '@ruckuswireless.com'
        elif len(m.group(2)) < 1:
            tb_owner = m.group(1) + '@ruckuswireless.com'

        testbed = dict(
            name=tb_name,
            tbtype=TestbedType.objects.get(name=p['tbtype']),
            location=tb_location,
            owner=tb_owner,
            resultdist=tb_owner,
            config=str(tbcfg),
        )
        tb = Testbed(**testbed)
        tb.save()
    return tb



# @TODO: Clean up this function
def testsuite_usage():
    u = [ ""
    , "This library is to replace all statements, in your addtestsuite_xyz.py program,"
    , "that are to deal with testbed retrival and creation."
    , "Use the 'from TestSuiteLib import *' command, so all objects/attributes in the TestSuiteLib.py"
    , "can be directly referenced by your scripts."
    , "\nExample:\n"
    , "   from TestSuiteLib import *"
    , "   tb = getTestbed()"
    , "   tbcfg = eval(tb.config)"
    , "   tbx = getMeshTestbed(name='mesh-depth-2', ap_mac_list=['00:1d:2e:16:4f:60', '00:1d:2e:0f:9e:88'])"
    , "   tby = getMeshTestbed(name='mesh d4', owner='mesh4', sta_ip_list=['192.168.1.11', '192.168.1.12'])"
    , "   tbz = getMeshTestbed(name='mesh', ApUseSym=1, sta_ip_list=['192.168.1.11'])"
    , "\nCaveat:\n"
    , "    settings.DATABASE_NAME must be in full path name."
    , "    Change DATABASE_NAME=RuckusAutoTest.db in setting.py to\n"
    , "        import os"
    , "        DATABASE_NAME = os.path.realpath(os.path.join(os.path.dirname(__file__), 'rat.db'))"
    ]
    for x in u: print x
    print ""


def get_models(**kwa):
    '''
    Get the list of models from testbed config
    kwa:
    - cfg: testbed config
    return:
    - a list of available models
    '''
    aps = kwa['cfg']['APs']
    models = []
    for ap in aps:
        if not ap['model'].lower() in models:
            models.append(ap['model'].lower())

    # enhance to support ZDs
    for zd in kwa['cfg']['ZDs']:
        if not zd['model'].lower() in models:
            models.append(zd['model'].lower())

    return models


def get_aps_by_models(models, tbCfg):
    '''
    . return a dict of lists, based on ap model, something likes:
      { 'zf2925': ['192.168.20.191'],
        'zf7942': ['192.168.20.170', '192.168.20.171'], }
    input:
    . models: a list of models
    '''
    apCfgs = tbCfg['APs']
    aps = dict([(m, []) for m in models]) # transforming models list to dict
    for ap in apCfgs:
        if ap['model'].lower() in models:
            aps[ap['model'].lower()].append(ap['ip_addr'])
    #log('\n%s' % pformat(aps))
    return aps

def get_zd_by_models(models, tbCfg):
    '''
    . return a dict of lists, based on ap model, something likes:
      { 'zf2925': ['192.168.20.191'],
        'zf7942': ['192.168.20.170', '192.168.20.171'], }
    input:
    . models: a list of models
    '''
    zd_cfgs = tbCfg['ZDs']
    zds = dict([(m, []) for m in models]) # transforming models list to dict
    for zd in zd_cfgs:
        if zd['model'].lower() in models:
            zds[zd['model'].lower()].append(zd['ip_addr'])
    #log('\n%s' % pformat(aps))
    return zds


def select_ap_by_model(cfg, is_interactive = True):
    '''
    . select an AP of given Model for testing, since there are many APs
      with the same model
    input:
    . cfg: a dict of lists, refer to the returning of get_aps_by_models()
    output:
    . cfg will be updated (and returned)
    '''
    if not is_interactive:
        return _select_default_ap_by_model(cfg)

    for k in cfg.iterkeys():
        if len(cfg[k]) > 1:
            cfg[k] = cfg[k][select_item(items=cfg[k], name='AP',
                                       inputHint='AP for model %s' % k)]
        else: # only one item in the list
            cfg[k] = cfg[k][0]
    return cfg


def _select_default_ap_by_model(cfg):
    '''
    . select a default ap for given model
    '''
    for k in cfg.iterkeys():
        cfg[k] = cfg[k][0]

    return cfg


def select_zd_by_model(cfg, is_interactive = True):
    '''
    . select a ZD of given Model for testing, since there are many ZDs
      with the same model
    input:
    . cfg: a dict of lists, refer to the returning of get_aps_by_models()
    output:
    . cfg will be updated (and returned)
    '''
    if not is_interactive:
        return _select_default_zd_by_model(cfg)

    for k in cfg.iterkeys():
        if len(cfg[k]) > 1:
            cfg[k] = cfg[k][select_item(items=cfg[k], name='ZD',
                                       inputHint='ZD for model %s' % k)]
        else: # only one item in the list
            cfg[k] = cfg[k][0]
    return cfg


def _select_default_zd_by_model(cfg):
    '''
    . select a default zd for given model
    '''
    for k in cfg.iterkeys():
        cfg[k] = cfg[k][0]

    return cfg


def select_client(tbCfg, is_interactive = True):
    if 'Clients' not in tbCfg or not tbCfg['Clients']:
        print 'There is no client on this testbed. This testsuite requires client(s).'
        exit(1)

    if not is_interactive and len(tbCfg['Clients']) >= 1:
        return tbCfg['Clients'][0]

    if len(tbCfg['Clients']) == 1:
        return tbCfg['Clients'][0]
    return select_item(items=tbCfg['Clients'], name='Client',
                      inputHint='Client')


def input_models(**kwa):
    '''
    kwa:
    - models
    '''
    print 'Available device models:\n%s' % \
          '\n'.join(['  %s - %s' % (i, v) for i, v in enumerate(kwa['models'])])
    sel_models = raw_input('Select device models (seperate by a space) or all [all]: ').strip()

    if sel_models.lower() in ('all', ''):
        sel_models = kwa['models']
    else:
        sel_models = sel_models.split(' ')
        sel_models = [kwa['models'][int(x)] for x in sel_models]
    return sel_models


def make_test_suite(**kwa):
    '''
    kwa:
    - define_ts_cfg: a function for defining testsuite configs
    - ignoreModel: for those model-independent testsuites
    - is_interactive
    '''
    _kwa = dict(
        ignoreModel = False,
        is_interactive = True,
        device = None,
    )
    _kwa.update(kwa)

    testsuite_cfg = dict(
        testbed = get_fm_testbed(**_kwa),
    )

    testsuite_cfg.update(_kwa)

    if not _kwa['ignoreModel']:
        tb_config = testsuite_cfg['testbed'].config.replace('\n' , '').replace('\r','')
        if _kwa['is_interactive']:
           testsuite_cfg.update(models=input_models(models=
                                get_available_models(_kwa['define_device_type'](),
                                get_models(cfg=eval(tb_config)))))
        else:
           cfg = dict(APs=[], ZDs=[],)
           if 'APs' in testsuite_cfg['device']:
               cfg['APs']= eval(tb_config)['APs']
           if 'ZDs' in testsuite_cfg['device']:
               cfg['ZDs']= eval(tb_config)['ZDs']
           testsuite_cfg.update(models=get_available_models(
                                       _kwa['define_device_type'](),
                                       get_models(cfg=cfg)))

    (ts_name, cfgs) = _kwa['define_ts_cfg'](**testsuite_cfg)

    log('--- Debug -----------')
    log('Testsuite Name: %s; Config:\n%s' % (ts_name, pformat(cfgs)))
    log('--- Debug [End] -----')

    order = 1
    ts = get_testsuite(ts_name, '')

    for common_name, test_name, test_params in cfgs:
        print '%s [%s]' % (common_name, test_name)

        update_test_case(
            dict(suite=ts, test_name='fm.%s' % test_name, seq=order, \
                 test_params=str(test_params), common_name=common_name)
        )
        order += 1


def update_test_case(config):
    '''
    . updating the testcase and its generated testruns if the testcase is exist
    . otherwise, just add it in
    '''
    try:
        tc = TestCase.objects.get(common_name=config['common_name'])
    except ObjectDoesNotExist:
        TestCase(**config).save()
        return

    tc.test_params = config['test_params']
    tc.save()
    print "Updating testcase: %s" % config['common_name']

    trs = TestRun.objects.filter(common_name=config['common_name'])
    if trs:
        for tr in trs:
            tr.test_params = config['test_params']
            tr.save()


OutOfRangeErrMsg = 'Please make sure the selection is in the given range [0 - %s]'
def select_item(**kwa):
    '''
    - print out a list of options and let user choose one
    - the list of options is
      . a regular list
      . a combination of many items in a dict
    kwa:
    - items: a dict of list, likes dict(a=[1,2], b=[3,4])
             or a list of item, likes [1,2,3,4]
    - name
    - action:    (optional) can be
                 1. '' or 'normal' (default): ask and input
                 2. 'askOnly'
                 3. 'inputOnly'
    - inputHint: optional in case askOnly
    return:
    - selected item: (key, item-index) or item-index only
                     based on type of 'items'
    '''
    p = dict(action='', inputHint='')
    p.update(kwa)

    lst = p['items']
    isDict = False
    if isinstance(lst, dict):
        # transform a dict(a=[1,2], b=[3,4]) to a list [[a,1], [a,2], [b,3], [b,4]]
        lst = [[k, i] for k in p['items'].keys() for i in p['items'][k]]
        isDict = True

    if p['action'].lower() != 'inputOnly'.lower():
        print 'Availabe %ss:\n%s' % \
              (p['name'], '\n'.join(['  % 2s - %s' % \
               (i, v[1] if isDict else v) for i, v in enumerate(lst)]))

    if p['action'].lower() != 'askOnly'.lower():
        i = int(raw_input('Select a(n) %s: ' % p['inputHint']))
        while i >= len(lst) or i < 0:
            print OutOfRangeErrMsg % (len(lst)-1)
            i = int(raw_input('Select a(n) %s: ' % p['inputHint']))
        if isDict:
            key =  lst[i][0]
            item = lst[i][1]
            return key, p['items'][key].index(item)
        return i


LocalOrServerFwPrompt = 'Use these local firmwares or download others from K2, LHotse? (u: Use; d: Download) '
def input_builds(**kwa):
    '''
    - Let user select stream/build for each model,
      . download that firmware from k2,
      . extract and store it to /rat/firmwares/ directory

    kwa:
    - models:   a list of models
    - localFws: a local firmware dict
    return:
    - filenames map with input models, likes:
        dict(zf2942: ('fs', '2942_xxxx.Bl7'))
    '''
    p = dict(isFmFwIncluded=True, is_interactive=True)
    p.update(kwa)

    filenames = {}
    fws = p['localFws']
    totalLocalFws = len(fws['fs']) + (len(fws['fm']) if fws.has_key('fm') else 0)

    if p['is_interactive']:
        sel = 'd'
        if totalLocalFws > 0:
            select_item(items=fws, name='firmware', action='askOnly')
            sel = input_with_default(LocalOrServerFwPrompt, 'u')
        if sel.strip().lower() != 'u':
            return input_server_builds(**p)

    for m in p['models']:
        # filter by the model first
        _fws = {}
        for k in fws.keys():
            _fws[k] = [f for f in fws[k] if m[2:] in f]
        #log_cfg(_fws, '_fws')
        # in this case, select_item return a list of key, index
        k, i = select_item(items=_fws, name='firmware',
                          inputHint='firmware for model %s' % m)
        filenames[m] = k, _fws[k][i]
    log('filenames:\n%s' % pformat(filenames))
    return filenames


def input_server_builds(**kwa):
    '''
    kwa:
    - models: a list of model
    '''
    filenames = {}
    buildstreams = get_build_streams()
    if (len(buildstreams['k2'])+len(buildstreams['lhotse'])) <= 0:
        print 'There is no buildstream available. Check your k2, LHotse connections.'
        exit(1)

    for m in kwa['models']:
        hostId, idx = select_item(items=buildstreams, name='buildstream',
                                 inputHint='buildstream for model %s' % m)
        builds = get_server_build_list(stream=buildstreams[hostId][idx], hostId=hostId)
        if len(builds) <= 0:
            raise Exception('No build is available for build stream: %s' % kwa['stream'])
        i = select_item(items=[b['number'] for b in builds],
                       name='build number', inputHint='build number')
        print 'Downloading build...'
        fn = download_build(build=builds[i], fileTmpl='%s_.*\\.Bl7' % m[-4:],
                           extractPath=init_firmware_path())
        filenames[m] = 'fs', fn # since the file is downloaded
    return filenames


def get_local_firmwares(**kwa):
    '''
    - start FM, get all the firmwares
    - get all firmwares on /rat/firmwares
    - remove duplications on filesystem list (since these have been uploaded to FM)
    kwa:
    - isFmFwIncluded: (optional) default: True
    - fmCfg: refer to start_fm() for details
    Return:
    - a dict: {'fs': [list of fw names]}
    '''
    p = dict(isFmFwIncluded=True)
    p.update(kwa)

    fws = dict(fs=get_fws_on_local_file_system())
    if p['isFmFwIncluded']:
        from RuckusAutoTest.components.lib.fm import fw_manager_fm_old as fw
        sm, fm = start_fm(**p['fmCfg'])
        fws['fm'] = [fw['firmwarename'] for fw in fw.get_all_firmwares(fm)]
        fm.stop()
        sm.shutdown()
        del fm, sm

        # clean up what have been uploaded to FM from FileSystem list
        fws['fs'] = [i for i in fws['fs'] if not i in fws['fm']]
    log('fws:\n%s\n' % pformat(fws))
    return fws


def get_server_build_list(**kwa):
    '''
    - go to K2/LHotse get the list of builds of the given stream
    kwa:
    - stream
    - hostId
    return:
    - list of builds
    '''
    bs = BuildStream()
    BSInfo = BuildServerInfo[kwa['hostId']]
    return bs.GetK2Builds('%s%s%s' % (BSInfo['BuildStreamDetailUrl'],
                                      BSInfo['BuildStreamPrefix'], kwa['stream']))


def download_build(**kwa):
    '''
    - download, extract the build to given directory
      and return build name
    WARNING: fileTmpl should be something likes '2925_.*\\.Bl7'
             because 2925 & 2942 share the same build

    WARNING: Since Build.saveLocal() do NOT have a way to specify
             target directory, it will save to current
             working directory by default
    kwa:
    - build:       a build (from the list of get_server_build_list)
    - fileTmpl:    the name of Bl7 file, firmware file name
                   Default: '_.*\\.Bl7'
    - extractPath: extract the file to this directory
    return:
    - extracted build file name or None (in error case)
    '''
    p = dict(fileTmpl = '_.*\\.Bl7', extractPath='')
    p.update(kwa)

    log('p:\n%s' % pformat(p))
    b = Build()
    b.URL = p['build']['URL']
    b.number = int(p['build']['number'])
    b_tfname = b.saveLocal()

    build_name = None
    b_tf = tarfile.TarFile.open(b_tfname, 'r:gz')
    tarfile_names = b_tf.getnames()
    log('tarfile_names:\n%s' % pformat(tarfile_names))
    for name in tarfile_names:
        if re.search(p['fileTmpl'], name, re.I):
            b_tf.extract(name, os.path.realpath(p['extractPath']))
            build_name = name
            break
    if not build_name:
        raise Exception('Filename could not be searched: %s\nList of filenames:\n\%s' % \
                        (p['fileTmpl'], pformat(tarfile_names)))
    return build_name


def get_build_streams():
    bs = {}
    for k in BuildServerInfo.keys():
        BuildStream = BuildServerInfo[k]
        bs[k] = _get_build_streams(url=BuildStream['BuildStreamUrl'],
                                 ignoreStreams=BuildStream['IgnoreStreams'])
    log('bs:\n%s\n' % pformat(bs))
    return bs


def _get_build_streams(**kwa):
    '''
    - Get the list of buildstreams from url (k2 or lhotse)
    NOTE:
    - Temporarily, put this here!
    kwa:
    - url
    - ignoreStreams: a list of un-used streams
    - proxies: A dictionary mapping scheme names to proxy URLs to support proxy setting
               + proxies=None: use setting of IE
               + proxies={}: No proxies to be used
               + proxies={'http': 'http://www.someproxy.com:3128'}: Use this proxy
                 to connect.
    Note: Refer to doc of urlopen for more detail.
    '''
    _kwa = {
        'proxies': None,
    }
    _kwa.update(kwa)
    from RuckusAutoTest import BeautifulSoup
    import urllib

    try:
        soup = BeautifulSoup.BeautifulSoup(''.join(urllib.urlopen(kwa['url'])))
    except:
        return []
    bs_select = soup('select')[0]
    bs = []
    for o in bs_select('option'):
        stream = o('font')[0].contents[0].strip()
        if not is_in(item=stream, list=kwa['ignoreStreams'], op='re'):
            bs.append(stream)
    return bs

