import copy
import time
import re
from pprint import pformat

from RuckusAutoTest.common.utils import is_row_match, log_cfg
from RuckusAutoTest.common import se_dojo_ui as dojo


'''
NOTES:
. lowercase module
. password field is a special case:
  we can get it values after setting but cannot when the page is just loaded

. most of the obtain/configure/restore on WebUI can be performed by 3 simple
  functions set/get/reset (on modules) accordingly
'''

# for debugging the provisioning of this module
# production testbed: this is set to 0
DELAY_PROVISIONING = 3 # secs
MULTI_CLICK_TRIES = 10 # times


class Ctrl:
    def __init__(self, loc, type = 'text', cfg = {}):
        self.loc = loc
        self.type = type
        self.cfg = cfg # additional configs


class CtrlType:
    def __init__(self, set_fn, get_fn):
        self.set = set_fn
        self.get = get_fn


def radio_group_get_fn(se, ctrl, cfg = {}):
    l = ctrl.loc
    for k in l.iterkeys():
        if CtrlTypes['radio'].get(se, Ctrl(l[k], 'radio')):
            return k
    return None


def ip_group_get_fn(se, ctrl, cfg = {}):
    '''
    l: list ip textbox locator
    '''
    l = ctrl.loc
    ip = [CtrlTypes['text'].get(se, Ctrl(l[i])) for i in range(len(l))]
    return '.'.join(ip)


def ip_group_set_fn(se, ctrl, v):
    '''
    NOTE:
    . support setting both text type and list
      ex: '192.168.0.10' or ['192', '168', '0', '10',]
    l: list ip textbox locator
    v: list value for each ip textbox
    '''
    l = ctrl.loc
    if isinstance(v, str):
        v = v.split('.')
    for i in range(len(l)):
        CtrlTypes['text'].set(se, Ctrl(l[i]), v[i])


def multi_click_set_fn(se, ctrl, v):
    '''
    . is the current state the desired state?
    . if not, store the current state
    . click on the instance to change the state
    . if the stored state re-occurs, raise exception
    '''
    l = ctrl.loc
    old_attr = CtrlTypes['multiClick'].get(se, l)
    if old_attr == v: return

    # trying to reach the desired state in 10 clicks
    for i in range(MULTI_CLICK_TRIES):
        se.click_and_wait(l, 1)
        attr = CtrlTypes['multiClick'].get(se, l)
        if attr == v:
            return
        if attr == old_attr:
            raise Exception('Failed to set to "%s" state' % v)
    raise Exception('Failed to set after trying %s times' % MULTI_CLICK_TRIES)


def multi_click_get_fn(se, ctrl, cfg = {}):
    '''
    . get current attribute status
    . map it to the 'states' to get and return key
    '''
    l = ctrl.loc
    attr = se.get_attr(l, cfg['attr'])
    for k, v in cfg['states'].iteritems():
        if v in attr:
            return k
    raise Exception('Unable to find current attribute - "%s" on cfg list %s' \
                    % (attr, cfg['states'].values()))


def drag_and_drop_set_fn(se, ctrl, cfg):
    '''
    Get the current list of items
    Is the expected in this list?
    If no, drag it to
    '''
    l = ctrl.loc
    for i in cfg:
        if i not in CtrlTypes['drag_and_drop'].get(se, l):
            se.drag_and_drop(cfg[i], l)


def drag_and_drop_get_fn(se, ctrl, cfg = {}):
    l = ctrl.loc
    return [k for k, v in cfg.iteritems()
              if se.is_element_present('%s//%s' % (l, v), 1)]


def unsupported_fn(se, ctrl, x = None):
    raise Exception('Unsupported operation of control "%s"' % ctrl.type)


def table_get_fn(se, ctrl, cfg = {}):
    '''
    cfg:
    . get: - all:  get all items (default)
           - iter: get iter
    '''
    # below are the other default params from iterTableRow:
    #   matches={}, op='in', is_advance=True,
    p = dict(
        get = cfg.get('get', 'all'), # get all by default
        loc = ctrl.loc,
        hdrs = ctrl.cfg['hdrs'],
    )
    p.update(cfg)

    if p.pop('get') == 'iter':
        return se.iter_table_rows(**p)
    return [i['row'] for i in se.iter_table_rows(**p)]


def htable_get_fn(se, ctrl, cfg = {}):
    '''
    . ks: if don't have this/or it is None in cfg then get all
          else get these only
    '''
    if cfg.get('no_hdrs', False) or ctrl.cfg.get('no_hdrs', False):
        ignore_case = cfg.get('ignore_case', ctrl.cfg.get('ignore_case', False))
        return se.get_htable_content(ctrl.loc, ignore_case = ctrl.cfg.get('ignore_case', False))

    p = dict(
        ks = cfg.get('ks', ctrl.cfg['hdrs']), # default -> get all
        loc = ctrl.loc,
        hdrs = ctrl.cfg['hdrs'],
    )

    return se.get_htable_rows2(**p)


def ltable_iter(se, ctrl, cfg, iter_nav_pages_fn):
    for p in iter_nav_pages_fn(se, ctrl.loc['nav']):
        for r in se.iter_table_rows(**cfg):
            r['page'] = p
            r['links'] = copy.deepcopy(ctrl.cfg.get('links', {}))
            for k in r['links'].iterkeys():
                r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k]
            yield r


def _ltable_get_fn(se, ctrl, cfg = {}):
    '''
    . this is original ltable, the new one adds click capability
    . refer to ltable doc for details
    '''
    p = dict(
        get = cfg.get('get', 'all'), # default
        search_box = cfg.get('search_box', None),
    )

    #TODO: describe a separated variable to get exact params for iter_table_rows func.
    #Note: whenever interface of iter_table_rows changed, must consider to fix this param also
    tbl_p = dict(
        loc = ctrl.loc['tbl'],
        hdrs = ctrl.cfg['hdrs'],
        match = cfg.get('match', {}),
        op = cfg.get('op', 'in'),
        is_advance = cfg.get('is_advance', True),
        fns = ctrl.cfg.get('fns', []),
    )
    #log_cfg(tbl_p, 'tbl_p')
    # if this table support search box, use it to filter data first
    if p['search_box']:
        if isinstance(p['search_box'], dict):
            CtrlTypes['search_box'].set(se, p['search_box']['loc'], p['search_box'].get('v', ''))
        else:
            CtrlTypes['search_box'].set(se, Ctrl(ctrl.loc['search_box']), p['search_box'])

    if p['get'] == 'iter':
        return ltable_iter(se, ctrl, tbl_p, dojo.iter_nav_pages)

    if p['get'] == '1st':
        for page in dojo.iter_nav_pages(se, ctrl.loc['nav']):
            for r in se.iter_table_rows(**tbl_p):
                r['page'] = page
                r['links'] = copy.deepcopy(ctrl.cfg.get('links', {}))
                for k in r['links'].iterkeys():
                    r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k]
                return r
        return {}
    tbl = []
    for page in dojo.iter_nav_pages(se, ctrl.loc['nav']):
        tbl += [i['row'] for i in se.iter_table_rows(**tbl_p)]
    return tbl


def ltable_get_fn(se, ctrl, cfg = {}):
    '''
    . extending ltable by providing click capability
    . 2 usecases: click on match items only or all items
    . why matches is a list? refer to the usecase selecting devices
    - matches: a list of dictionary as below:
        [
            {'device_name': 'RuckusAP', 'model': 'Zf2925'},
            {'internal_ip': '192.168.0.222', 'serial': '1234'},
        ]

    UPDATE
    . automatically get the header if no is given
    . DESIGN INTENTION: hdrs or hdr_attr must be on the cfg
      . reason: if hdrs is there use it. If not, hdr_attr must be there,
        since once the hdrs is updated, the next get will used the old one
        and in inv_device_mgmt\tbl case, it is there to support 3 tables:
        aps, zds, clients and the hdrs are changed accordingly
    '''
    if 'hdr_attr' in ctrl.cfg: # re-get the hdrs eveytime
        ctrl.cfg['hdrs'] = se.get_tbl_hdrs_by_attr(ctrl.loc['tbl'],
                                                   ctrl.cfg['hdr_attr'])
        if 'hdr_map' in ctrl.cfg:
            ctrl.cfg['hdrs'] = \
                [ctrl.cfg['hdr_map'][k] if k in ctrl.cfg['hdr_map'] else k
                 for k in ctrl.cfg['hdrs']]

    if not 'link' in cfg:
        return _ltable_get_fn(se, ctrl, cfg)

    p = dict(
        link = cfg.pop('link', ''),
        link_fmt = cfg.pop('link_fmt', ''),
        matches = cfg.pop('matches', []),
        ops = cfg.pop('ops', 'in'),
    )
    cfg['get'] = 'iter' # must be

    for r in _ltable_get_fn(se, ctrl, cfg):
        if p['matches']:
            if is_row_match(r['row'], p['matches'], p['ops'], is_delete = True):
                _link_click(se, r['links'][p['link']], p['link_fmt'])
                if not p['matches']: # no more matches, return
                    # must return a match row here
                    return r
        else:
            # in this case we click all rows so don't need to return anything here
            _link_click(se, r['links'][p['link']], p['link_fmt'])
    if not p['matches']:
        return
    # remaining match are not found
    log_cfg(p['matches'], 'not found matches')
    raise Exception('Some match items not found')


def check_set_fn(se, ctrl, v):
    if v:
        se.click_if_not_checked(ctrl.loc)
    else:
        se.click_if_checked(ctrl.loc)


def search_box_set_fn(se, ctrl, v):
    CtrlTypes['text'].set(se, ctrl, v)
    ENTER_CODE = "\13"
    se.key_up(ctrl.loc, ENTER_CODE)
    time.sleep(2.5)


def _link_click(se, link, link_fmt):
    ''' helper func for tbl_click_fn '''
    if link_fmt:
        link = link % tuple(link_fmt)
    return se.click_and_wait(link)


def tbl_click_fn(se, ctrl, cfg):
    '''
    WARNING: OBSOLETE BY ltable itself
    help clicking table rows' link
    if there is match obj, then clicking on matched obj only
    else clicking all of the rows' link

    TODO: put the usage here

    input
    . all the cfg from tbl, most of the time it is match obj
    . link: what link to be clicked
    . link_fmt: args for formatting the link (a tuple or list)
    '''
    p = dict(link = '', link_fmt = '', op = 'in')
    p.update(copy.deepcopy(cfg))
    p['get'] = 'iter'
    link, link_fmt = p.pop('link'), p.pop('link_fmt')
    if 'match' in p:
        match = p.pop('match')
        for r in CtrlTypes['ltable'].get(se, ctrl, p):
            #log_cfg(r['row'])
            #log_cfg(match)
            if is_row_match(r['row'], match, p['op'], is_delete = True):
                _link_click(se, r['links'][link], link_fmt)
                if not match: # found them all, no more searching
                    return
        # remaining match are not found
        raise Exception('Match not found: %s' % pformat(match))
    else:
        for r in CtrlTypes['ltable'].get(se, ctrl, p):
            _link_click(se, r['links'][link], link_fmt)


def multi_btn_click_fn(se, ctrl, cfg):
    se.click_and_wait(ctrl.loc[cfg])


def loading_ind_wait_fn(se, ctrl, cfg):
    time.sleep(1)
    if not se.wait_for_element_disappered(ctrl.loc):
        raise Exception('Timed out while waiting for Loading Indicator disappear')
    time.sleep(3)


def dojo_select_get_fn(se, ctrl, cfg = None):
    '''
    default is get selected
    get = all then get all
    '''
    if cfg and 'get' in cfg and cfg['get'] == 'all':
        return dojo.get_cb_options(se, ctrl.loc)
    return dojo.get_cb_selected_option(se, ctrl.loc)


# NOTE: in some functions, v is not used but be there for interface conforming
# Add cfg=None into get functions to make it has the same interface with get func
# of ltable and htable. This is to make simplify when calling the get function
CtrlTypes = dict(
    text = CtrlType(
        lambda se, ctrl, v: se.type_text(ctrl.loc, v),
        lambda se, ctrl, cfg = None: se.get_value(ctrl.loc),
    ),
    select = CtrlType(
        lambda se, ctrl, v: se.select_option(ctrl.loc, v, True),
        lambda se, ctrl, cfg = None: se.get_selected_option(ctrl.loc),
    ),

    # WARNING: Obsoleted! will be removed, use text instead
    password = CtrlType(
        lambda se, ctrl, v: se.type_text(ctrl.loc, v),
        lambda se, ctrl, cfg = None: se.get_value(ctrl.loc),
    ),
    radio = CtrlType(
        lambda se, ctrl, v = None: se.safe_click(ctrl.loc),
        lambda se, ctrl, cfg = None: se.is_checked(ctrl.loc),
    ),
    #button or link: should not be returned?
    button = CtrlType(
        lambda se, ctrl, v = None: se.click_and_wait(ctrl.loc, ctrl.cfg['wait'] if 'wait' in ctrl.cfg else 1.5),
        lambda se, ctrl, cfg = None: se.click_and_wait(ctrl.loc, ctrl.cfg['wait'] if 'wait' in ctrl.cfg else 1.5),
    ),
    # a read-only control to wrap selenium.get_text() function
    html = CtrlType(
        unsupported_fn,
        lambda se, ctrl, cfg = None: se.get_text(ctrl.loc),
    ),
    htable = CtrlType(
        unsupported_fn,
        htable_get_fn,
    ),
    _htable = CtrlType(# TODO: clean this up soon
        unsupported_fn,
        lambda se, ctrl, cfg = None: se.get_htable_content(ctrl.loc, ignore_case = ctrl.cfg.get('ignore_case', False)),
    ),
    table = CtrlType(# table without page nav
        table_get_fn,
        table_get_fn,
    ),
    ltable = CtrlType(# table with page nav
        ltable_get_fn,
        ltable_get_fn,
    ),
    dojo_select = CtrlType(
        lambda se, ctrl, v: dojo.select_cb_option(se, ctrl.loc, v, ctrl.cfg.get('exact', True)),
        dojo_select_get_fn,
    ),
    search_box = CtrlType(#
        search_box_set_fn,
        search_box_set_fn,
    ),
    # a boolean control
    check = CtrlType(
        check_set_fn,
        lambda se, ctrl, cfg = None: se.is_checked(ctrl.loc),
    ),
    tbl_click = CtrlType(
        tbl_click_fn,
        tbl_click_fn,
    ),
    multi_buttons = CtrlType(
        multi_btn_click_fn,
        multi_btn_click_fn,
    ),
    loading_ind = CtrlType(
        loading_ind_wait_fn,
        loading_ind_wait_fn,
    ),
)


CtrlTypes.update(dict(
    # An example of radioGroup control definition on Locators
    #   encryptionMode = Ctrl(
    #       dict(disable="//input...",
    #            wep=    "//input...",
    #            wpa=    "//input...",),
    #       type='radioGroup'
    #   )
    radioGroup = CtrlType(
        lambda se, ctrl, v: CtrlTypes['radio'].set(se, Ctrl(ctrl.loc[v.lower()], 'radio')),
        radio_group_get_fn,
    ),

    ipGroup = CtrlType(
        ip_group_set_fn,
        ip_group_get_fn,
    ),

    # a multi-click state control
    # raise exception when current state is re-occurence
    # . this type of control requires an additional configs
    #   . an attribute:    self.cfg['attr']
    #   . a dict of stats: self.cfg['states']
    multiClick = CtrlType(
        multi_click_set_fn,
        multi_click_get_fn,
    ),

    # drag and drop control, requires additional configs
    # . a list of containable items: self.cfg['items']
    drag_and_drop = CtrlType(
        drag_and_drop_set_fn,
        drag_and_drop_get_fn,
    ),
))


def _is_special_ctrl(loc):
    '''
    . up 2 now, there are 3 (special) transitional controls which help
      configuring the system
      . button
      . multi_button
      . loading_ind(icator)
      this function helps identifying them
    '''
    special_ctrls = ['button', 'multi_button', 'loading_ind']
    for c in special_ctrls:
        if c == loc.type:
            return True
    return False


def set(se, loc, cfg, ctrl_order = []):
    '''
    se:  selenium
    loc: locators
    cfg: config
    orderedCtrls: + must not be None, a [] list is acceptable.
                  + It may has a element "sleep" (a dict: {'sleep':2}) to make
                    the set function sleep a moment before doing next.
                    E.g: ctrl_order = ['item 1', 'item 2', {'sleep':2}, 'item 3']
    '''
    cfg_ks = cfg.keys()
    if not cfg_ks:
        raise Exception('No config is given')

    ks = list(copy.deepcopy(ctrl_order)) + [k for k in cfg_ks if k not in ctrl_order]
    for k in ks:
        # This is to support for the case users want to sleep a moment before do next.
        if isinstance(k, dict) and k.get('sleep', 0):
            time.sleep(k['sleep'])
            continue

        if k not in cfg_ks and not _is_special_ctrl(loc[k]): continue
        CtrlTypes[loc[k].type].set(se, loc[k], cfg.get(k, ''))
        time.sleep(DELAY_PROVISIONING)


def get(se, loc, cfg, ctrl_order = []):
    '''
    NOTE:
    . raising the exceptions in this function are for debugging purpose
    TODO/WARNING:
    . this function can have side effect on 'button' case and must be reviewed
    . joining keys before setting/getting so code don't dup

    input:
    . cfg: a list of keys
           or a dict: which values are getting-cfgs
    '''
    if not cfg:
        raise Exception('No config is given')

    cfg_ks = cfg if isinstance(cfg, list) else cfg.keys()
    ks = list(copy.deepcopy(ctrl_order)) + [k for k in cfg_ks if k not in ctrl_order]
    _cfg = {}
    for k in ks:
        if k not in cfg_ks and not _is_special_ctrl(loc[k]): continue
        if not isinstance(loc[k], Ctrl):
            raise Exception('Invalid config is given: %s' % loc[k])

        in_cfg = cfg.get(k, {}) if isinstance(cfg, dict) else {}
        v = CtrlTypes[loc[k].type].get(se, loc[k], in_cfg)

        # don't return if this item is a transitional one
        if _is_special_ctrl(loc[k]): continue
        _cfg[k] = v
    return _cfg


'''
NOTE:
. the interface of _format*() is complicated by the 'pass by ref' nature
 of Python
'''
def _format_str(ctrls, k, fmt_args):
    ctrls[k] %= fmt_args

def _format_ctrl_str(ctrls, k, fmt_args):
    ctrls[k].loc %= fmt_args

def _format_ctrl_dict(ctrls, k, fmt_args):
    for i in ctrls[k].loc.iterkeys():
        ctrls[k].loc[i] %= fmt_args

def _format_ctrl_list(ctrls, k, fmt_args):
    for i in range(len(ctrls[k].loc)):
        ctrls[k].loc[i] %= fmt_args


def formatCtrl(ctrls, fmt_args):
    '''
    NOTE: please call format_ctrl instead of this
    . return a copied formatted controls of the the given ctrls
    . for other item which is NOT an instance of Ctrl, _format_str() is used
    input:
    . ctrls: a dict of ctrls
    . fmt_args: can be a list or a dict
    '''
    l = copy.deepcopy(ctrls)
    for k in l.iterkeys():
        fn = _format_str
        if isinstance(l[k], Ctrl):
            fn = dict(
                str = _format_ctrl_str,
                list = _format_ctrl_list,
                dict = _format_ctrl_dict,
            )[str(type(l[k].loc)).split("'")[1]]
        fn(l, k, fmt_args if isinstance(fmt_args, dict) else tuple(fmt_args))
    return l


def format_ctrl(ctrls, fmt_args):
    return formatCtrl(ctrls, fmt_args)


def cfg_data_flow(cfg, ctrl_order):
    return cfgDataFlow(cfg, ctrl_order)


def cfgDataFlow(cfg, ordered_groups):
    '''
    This function is to create a data flow. A data flow is a way to access elements which
    are being in cfg_items. This function is to apply for items need to be in order.
    kwa:
    - cfg: a list/dictionary of config items
    - ordered_groups: a list of group item need to be set in order. Each element will have
    a structure like:
        dict(
            enter  = 'edit_common_btn',
            items = ['downlink', 'uplink'],
            exit   = 'back_link',
        ),
        flow to access "items" can be described as:
        1. Click "enter" to see "items"
        2. => Reach "items" for this page
        3. Click "exit" to exit this page or submit this page and back to main page
    Note: if the ordered items don't need to "enter"/"exit", leave it as blank ('') or
    just skip it
    '''
    ret_list = []
    for group in ordered_groups:
        if isinstance(group, dict):
            # filter items of this "group" which they are being in the cfg_items only
            ordered_list = [k for k in group['items'] if k in cfg]
            # if the list is not empty
            if ordered_list:
                # not empty => add the item need to be clicked to see items
                if 'enter' in group and group['enter']:
                    # enhance to support for the case "enter" item is a list
                    list_fn = {
                        True: ret_list.extend,
                        False: ret_list.append,
                    }[isinstance(group['enter'], list)](group['enter'])
                # append ordered items which in cfg_items
                ret_list.extend(ordered_list)
                # not empty => add the item need to be clicked to exit this page
                if 'exit' in group and group['exit']:
                    ret_list.append(group['exit'])
        else: # text-only item
            if group in cfg:
                ret_list.append(group)
    return ret_list


def _remove_blank_pairs(ctrl_order, level = 0):
    '''
    NOTE: if exception is raised here, then double check your [...] pairs
    '''
    if level == 20:
        raise Exception('Recurse too deep: %s' % level)

    for i in range(len(ctrl_order)):
        if '[' in ctrl_order[i] and ']' in ctrl_order[i + 1]:
            #log_cfg('delete pair: %s - %s' % (ctrl_order[i], ctrl_order[i + 1]))
            del ctrl_order[i + 1]
            del ctrl_order[i]
            return _remove_blank_pairs(ctrl_order, level + 1)
    #log_cfg(ctrl_order)
    return ctrl_order


def _get_order_key(order):
    return order.replace('[', '').replace(']', '')


def cfg_data_flow2(cfg_ks, ctrl_order):
    '''
    flatten the string (remove '\n' and dup whitespaces)
    move a long and remove keys which are not in the input (cfg_ks) and not a button (in/out)
    remove blank pairs (which just has in/out), ie. [search_tab None] and Nones
    create and return unique key list
    '''
    ctrl_order = copy.deepcopy(ctrl_order)
    order = re.sub('[ ]+', ' ', ctrl_order.replace('\n', ' ').strip()).split(' ')
    order_tmp = copy.deepcopy(order)

    for o in order_tmp:
        is_btn = True if '[' in o or ']' in o else False
        if not _get_order_key(o) in cfg_ks and not is_btn:
            order.remove(o) # this could raise problem! No, since keys are unique!
    del order_tmp
    #log_cfg(order)
    order = [_get_order_key(o) for o in _remove_blank_pairs(order)
                if _get_order_key(o).lower() != 'none']
    ret_order = []
    for o in order:
        if o not in ret_order:
            ret_order.append(o)
    #log_cfg(ret_order)
    return ret_order

