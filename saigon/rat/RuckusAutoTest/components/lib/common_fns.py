''' refer to admin_users_fm.py to know how to use this '''
from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import cfg_data_flow2


def get_order(m, order, cfg):
    '''
    . parse the order to create a data flow
    order: a string to specify the order
      1. None:      don't use order
      2. 'default': use the default
      3. string:    use this as order
    '''
    if not order:
        return []
    co = m['ctrl_order'] if order.lower() == 'default' else order
    cfg_ks = cfg.keys() if isinstance(cfg, dict) else cfg
    return cfg_data_flow2(cfg_ks, co)


def set(m, o, cfg, is_nav = True, order = 'default'):
    if is_nav:
        m['nav_to'](o, force = True)
    return ac.set(o.selenium, m['locators'], cfg, get_order(m, order, cfg))


def get(m, o, cfg, is_nav = True, order = 'default'):
    #log_cfg(cfg, 'cfg')
    if is_nav:
        m['nav_to'](o, force = True)
    return ac.get(o.selenium, m['locators'], cfg, get_order(m, order, cfg))


def get_tbl(m, o, tbl, tcfg, is_nav = False, order = None):
    '''
    most of the case, is_nav=False, order=None
    input:
    . tbl: name of the table
    . cfg: dict of config or (get='iter'). Default is get='all'
    '''
    return get(m, o, {tbl:tcfg}, is_nav = is_nav, order = order)[tbl]


def _delete_all(m, o, tbl = 'tbl'):
    ''' delete what delete-able items '''
    tcfg = dict(get = 'iter', is_advance = False, match = dict(action = 'delete'), op = 'in')
    for r in get_tbl(m, o, tbl, tcfg, is_nav = True, order = 'default'):
        #log_cfg(r)
        o.selenium.click_and_wait(r['links']['delete'])


def _delete(m, o, mcfg, tbl = 'tbl', op = 'eq', is_nav = True):
    '''
    find the first match and perform the action accordingly
    '''
    r = get_tbl(m, o, tbl, dict(get = '1st', match = mcfg, op = op), is_nav = is_nav)
    if r and 'delete' in r['row']['action'].lower():
        o.selenium.click_and_wait(r['links']['delete'])
        return True
    return False


def _find(m, o, mcfg, tbl = 'tbl', op = 'eq', is_nav = False):
    ''' NOTE: find first only '''
    return get_tbl(m, o, tbl, dict(get = '1st', match = mcfg, op = op), is_nav = is_nav)


'''
def _find_iter(m, o, mcfg, tbl='tbl', op='eq'):
    return get_tbl(m, o, tbl, dict(get='iter',match=mcfg,op=op))
'''

