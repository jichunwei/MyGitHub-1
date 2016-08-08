''' add components here so python 'import *' works properly! '''

'''
WARNING:
. don't import anything but 'sys' here so that these imports don't
  be added on the testbed-components table
'''
import sys

if sys.platform == "win32":
    __all__ = ['DUT', 'RuckusAP', 'FTPServer',
               'Station', 'StationWinPC', 'RemoteStationWinPC', 'LinuxPC',
               'FlexMaster', 'APWebUIs', 'ZDWebUIs', 'MetroWebUIs', 'PushKeypadDevice']
else:
    __all__ = ['DUT', 'RuckusAP', 'FTPServer',
               'Station']

_objs = []

#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def create_fm_by_ip_addr(
        ip_addr = '192.168.30.252',
        username = 'admin@ruckus.com',
        password = 'admin',
        **kwargs
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        username = username,
        password = password
    )
    params.update(kwargs)

    return _create_fm(params)


def create_zd_by_ip_addr(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        **kwargs
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        username = username,
        password = password
    )
    params.update(kwargs)

    return _create_zd(params)


def create_station_by_ip_addr(ip_addr = '192.168.1.11', **kwargs):
    '''
    '''
    params = dict(
        sta_ip_addr = ip_addr,
    )
    params.update(kwargs)

    return _create_station(params)


def create_linux_station_by_ip_addr(ip_addr = '192.168.1.101', **kwargs):
    '''
    '''
    params = dict(
        sta_ip_addr = ip_addr,
    )
    params.update(kwargs)

    return _create_linux_station(params)


def create_ruckus_ap_by_ip_addr(
        ip_addr = '192.168.0.1',
        username = 'super',
        password = 'sp-admin',
        **kwargs
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        username = username,
        password = password
    )
    params.update(kwargs)

    return _create_ruckus_ap(params)


def create_server_by_ip_addr(
        ip_addr = '192.168.0.252',
        username = 'lab',
        password = 'lab4man1',
        root_password = 'lab4man1',
        **kwargs
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        user = username,
        password = password,
        root_password = root_password
    )
    params.update(kwargs)

    return _create_server(params)


def create_zd_cli_by_ip_addr(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        shell_key = '!v54!',
        **kwargs
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        username = username,
        password = password,
        shell_key = shell_key
    )
    params.update(kwargs)

    return _create_zd_cli(params)


def create_zd_shell_by_ip_addr(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        shell_key = '!v54!',
        protocol = 'SSH'
    ):
    '''
    '''
    params = dict(
        ip_addr = ip_addr,
        username = username,
        password = password,
        shell_key = shell_key,
        protocol = protocol
    )
    return _create_zd_shell(params)


def create_ap_by_model(
        model = 'zf2942',
        ip_addr = '192.168.0.1',
        username = 'super',
        password = 'sp-admin',
        **kwargs
    ):
    '''
    '''
    params = dict(
        model = model,
        ip_addr = ip_addr,
        username = username,
        password = password
    )
    params.update(kwargs)

    return _create_ap(params)


def create_metro_by_model(
        model = 'mf7211',
        ip_addr = '192.168.0.1',
        username = 'super',
        password = 'sp-admin',
        **kwargs
    ):
    '''
    '''
    params = dict(
        model = model,
        ip_addr = ip_addr,
        username = username,
        password = password
    )
    params.update(kwargs)

    return _create_ap(params)


def clean_up_rat_env():
    '''
    . clean up the Se Mgr on global
    '''
    import logging    
    global se_mgr
    if 'se_mgr' in globals():
        try:
            logging.debug('Clean up the Selenium Manager')
            se_mgr.shutdown()
            del se_mgr

        except:
            pass


def destroy_comp(obj):
    '''
    . recursively destroying components
    '''
    if type(obj) in [dict]:
        for ins in obj.itervalues():
            destroy_comp(ins)

    elif type(obj) in [list, tuple]:
        for ins in obj:
            destroy_comp(ins)

    else:
        try:
            obj.__del__()

        except Exception, e:
            print "[ERROR] on destroying object [%s]" % (e.message)
            pass


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
def _get_se_mgr():
    '''
    . find and use the se_mgr on global
    . if not found then create a SeMgr instance and put it in env
    '''
    import logging
    from RuckusAutoTest.common import SeleniumControl as sc
    global se_mgr
    try:
        return se_mgr

    except:
        logging.debug('Creating the Selenium Manager')
        se_mgr = sc.SeleniumManager() # setting the global
        return se_mgr


def _create_server(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import LinuxPC
    p = dict(
        ip_addr = '192.168.0.2',
        user = 'lab',
        password = 'lab4man1',
        root_password = 'lab4man1'
    )
    p.update(cfg)

    logging.info('Creating linuxPC component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    server = LinuxPC.LinuxPC(p)
    _reg_obj(server)

    return server


def _create_ruckus_ap(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import RuckusAP
    p = dict(
        ip_addr = '192.168.0.1',
        username = 'super',
        password = 'sp-admin'
    )
    p.update(cfg)

    logging.info('Creating RuckusAP component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    ap = RuckusAP.RuckusAP(p)
    _reg_obj(ap)

    return ap


def _create_station(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import RemoteStationWinPC
    p = dict(
        sta_ip_addr = '192.168.1.11',
    )
    p.update(cfg)

    logging.info('Creating RemoteStationWinPC component [%s]' % p['sta_ip_addr'])
    logging.debug(pformat(p))
    sta = RemoteStationWinPC.RemoteStationWinPC(p)
    _reg_obj(sta)

    return sta


def _create_linux_station(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import StationLinuxPC
    p = dict(
        sta_ip_addr = '192.168.1.101',
    )
    p.update(cfg)

    logging.info('Creating StationLinuxPC component [%s]' % p['sta_ip_addr'])
    logging.debug(pformat(p))
    sta = StationLinuxPC.StationLinuxPC(p)
    _reg_obj(sta)

    return sta


def _create_zd_cli(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import ZoneDirectorCLI
    p = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        shell_key = '!v54!'

    )
    p.update(cfg)

    logging.info('Creating ZoneDirectorCLI component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    zd_cli = ZoneDirectorCLI.ZoneDirectorCLI(p)
    _reg_obj(zd_cli)

    return zd_cli


def _create_ap(cfg = {}):
    from pprint import pformat
    import logging
    p = dict(
        ip_addr = '192.168.0.1',
        model = 'zf7942',
        username = 'super',
        password = 'sp-admin',
        # -- should be internal --
        browser_type = 'firefox',
        semgr = _get_se_mgr(),
        https = True,
    )
    p.update(cfg)

    logging.info('Creating AP WebUI component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    ap = create_com(p['model'], p, p['semgr'], p['https'])
    _reg_obj(ap)

    return ap


def _create_zd(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import ZoneDirector
    p = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        # -- should be internal --
        browser_type = 'firefox',
        selenium_mgr = _get_se_mgr(),
        https = True,
    )
    p.update(cfg)

    # this conversion is for ZD expected config
    p['config'] = dict(
        username = p.pop('username'),
        password = p.pop('password'),
    )
    logging.info('Creating Zone Director component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    zd = ZoneDirector.ZoneDirector(p)
    _reg_obj(zd)

    return zd


def _create_zd_shell(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import ZoneDirectorShell
    p = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        shell_key = '!v54!',
        protocol = 'SSH'
    )
    p.update(cfg)

    logging.info('Creating ZoneDirectorShell component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    zd_shell = ZoneDirectorShell.ZoneDirectorShell(p)
    _reg_obj(zd_shell)

    return zd_shell

def _create_fm(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import FlexMaster
    p = dict(
        ip_addr = '192.168.30.252',
        username = 'admin@ruckus.com',
        password = 'admin',
        # -- should be internal --
        browser_type = 'firefox',
        selenium_mgr = _get_se_mgr(),
        https = False,
    )
    p.update(cfg)

    # this conversion is for FM expected config
    p['config'] = dict(
        username = p.pop('username'),
        password = p.pop('password'),
    )
    logging.info('Creating Flex Master component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))

    fm = FlexMaster.FlexMaster(**p)
    _reg_obj(fm)
    fm.start()

    return fm


def get_cls(module, model, class_tmpl = '%sWebUI'):
    '''
    . get the class from the given module, to match specified model
    '''
    cls = None
    exec('''cls = module.%s''' % (class_tmpl % model.upper()))
    if not cls:
        raise Exception('Class for %s in %s is not found' %
                        (model.upper(), str(module)))
    return cls


def create_com(model, cfg, semgr = None, https = True):
    '''
    . creating testbed component based on the given model
    . this function is a helper function which decouples testbed from
      component creating task

    . all the components are stored on RuckusAutoTest.components
    '''
    from RuckusAutoTest.components import (
        FlexMaster, RemoteStationWinPC, APWebUIs, ZDWebUIs, MetroWebUIs
    )

    coms = dict(
        fm = FlexMaster.FlexMaster,
        client = RemoteStationWinPC.RemoteStationWinPC,
    )

    # create selenium manager if it None
    if not semgr: semgr = _get_se_mgr()

    if model in coms:
        com = coms[model]
        if model == 'client':
            return com(cfg)
        else:
            cfg['model'] = model
            return com(semgr, cfg['browser_type'], cfg['ip_addr'], cfg, https = https)

    cfg['model'] = model.lower()
    if model.lower()[:2] in ['zf', 'vf']: # is this an AP model?
        return get_cls(APWebUIs, model)(
            semgr, cfg['browser_type'], cfg['ip_addr'], cfg, https = https
        )
    if model.lower()[:2] in ['zd']: # is this an ZD model?
        cfg['init_s'] = False
        return get_cls(ZDWebUIs, model)(
            semgr, cfg['browser_type'], cfg['ip_addr'], cfg, https = https
        )
    if model.lower()[:2] in ['mf']: # is this a Metro model?
        return get_cls(MetroWebUIs, model)(
            semgr, cfg['browser_type'], cfg['ip_addr'], cfg, https = https
        )
    return None


def get_zd_model(model):
    ''' model is from FM WebUI, something likes 'zd1006' '''
    return dict(
        zd1 = 'zd1k',
        zd3 = 'zd3k',
    )[model[:3]]


def get_fmdv_com(cfg):
    '''
    cfg: fm, model, serial, ip_addr
    '''
    import copy
    from RuckusAutoTest.components import FMDeviceViews
    dvcfg = copy.deepcopy(cfg['fm'].config)
    dvcfg.update(cfg)

    return get_cls(FMDeviceViews, cfg['model'], '%sFMDV')(
        None, cfg['fm'].browser_type, cfg['fm'].ip_addr, dvcfg, cfg['fm'].selenium
    )


def _reg_obj(obj):
    '''
    . register a newly created component
    '''
    if obj not in _objs:
        _objs.append(obj)


import atexit
atexit.register(clean_up_rat_env)
atexit.register(destroy_comp, _objs)

