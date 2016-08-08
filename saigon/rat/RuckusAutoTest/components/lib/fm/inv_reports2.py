'''
TODO: cover the old inv_reports library
'''
#import logging
#from pprint import pformat, pprint
#from RuckusAutoTest.common.utils import download_file

from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib.fm import _device_filter_fm as df
#from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def generate_report(fm, report_options, get_results = True):
    '''
    . can either use get_results = True for getting the results
      or call fill_in_search_options() for further filtering the results
    input
    . report_options: a list of options, something likes
        ['Historical Connectivity', '7811 Devices', 'Disconnected']
      or
        ['Event Timeline', 'All Standalone APs', 'Connectivity problem',
         '2010-01-10', '10:20:00 AM', '2010-03-22', '11:30:00 PM']
      the additional 4 texts are for starting/ending date and time
    '''
    # map inputs to controls
    cfg = {}
    regular_opts = report_options[:3]
    datetime_opts = report_options[3:]

    for i in range(len(regular_opts)):
        cfg['report_opt' + str(i + 1)] = regular_opts[i]

    if datetime_opts: # additional
        cfg['start_date'] = datetime_opts[0]
        cfg['start_time'] = datetime_opts[1]
        cfg['end_date'] = datetime_opts[2]
        cfg['end_time'] = datetime_opts[3]

    _set(fm, cfg, is_nav = True)

    if get_results:
        return _get_tbl(fm, 'tbl', {}, False)


def fill_in_search_options(fm, options, get_results = False):
    '''
    . fill in the search criteria on the new search page and search for result
    input
    . a list of options, something likes
        options = [
            ['Device Name', 'Contains', 'al'], 'and',
            ['Serial Number', 'Starts with', '1008'], 'or',
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    p = {}
    p.update(df.map_where_conditions(options))
    _set(fm, p, is_nav = True)
    if get_results:
        return _get_tbl(fm, 'tbl', {}, False)


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
DOJO_CB = "/span[contains(@class,'dojoComboBoxOuter')]"
DATE_CTRL_TMPL = "//tr[@dojoattachpoint='%s']/td" + \
    "/span[img[contains(@alt,'%s')]]/input[@type='text']"
TBL = "//div[@dojoattachpoint='dataAreaFirstLayer']"


locators = dict(
    # options ---
    report_opt1 = Ctrl("//tr[@class='RuckusReportOptionRow'][1]/td" + DOJO_CB,
                       'dojo_select'),
    report_opt2 = Ctrl("//tr[@class='RuckusReportOptionRow'][2]/td" + DOJO_CB,
                       'dojo_select'),
    report_opt3 = Ctrl("//tr[@class='RuckusReportOptionRow'][3]/td" + DOJO_CB,
                       'dojo_select'),

    start_date = Ctrl(DATE_CTRL_TMPL % ('startTimeRow', 'date')),
    start_time = Ctrl(DATE_CTRL_TMPL % ('startTimeRow', 'time')),
    end_date = Ctrl(DATE_CTRL_TMPL % ('endTimeRow', 'date')),
    end_time = Ctrl(DATE_CTRL_TMPL % ('endTimeRow', 'time')),

    generate_btn = Ctrl("//input[@dojoattachpoint='generateButton']",
                        'button'),

    # options --- Filters' place-holder
    search_tmpl = None,
    filter_btn = Ctrl("//input[@dojoattachpoint='filterButton']", 'button'),
    delete_filter_btn = Ctrl("//input[@dojoattachpoint='deleteAllButton']",
                             'button'),

    # report table ---
    tbl = Ctrl(
        dict(tbl = TBL + "//table[@dojoattachpoint='tableArea']",
             nav = TBL + "//table[@class='pageSelector']",
             search_box = TBL + "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        dict(attr = 'class') # WARNING: changed based on search
    ),
)


ctrl_order = '''
[None
  report_opt1 report_opt2 report_opt3 start_date start_time end_date end_time
generate_btn]
[None
  search_tmpl
filter_btn]
[generate_btn tbl None]
'''

locators, (ctrl_order,) = df.fmt_ctrls(
    locators, [ctrl_order], tmpl = 'reports',
    tmpl_k = 'search_tmpl', space_shift = 6, k_prefix = ''
)


def _nav_to(obj, force = False):
    obj.navigate_to(obj.INVENTORY, obj.INVENTORY_REPORTS, force = force)


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = _nav_to,
)

def _set(obj, cfg, is_nav = True, order = 'default'):
    return fns.set(m, obj, cfg, is_nav, order)

def _get(obj, cfg, is_nav = True, order = 'default'):
    return fns.get(m, obj, cfg, is_nav, order)

def _get_tbl(obj, tbl, cfg, is_nav = False, order = None):
    return fns.get_tbl(m, obj, tbl, cfg, is_nav, order)

def _delete_all(obj, tbl = 'tbl'):
    return fns._delete_all(m, obj, tbl)

def _delete(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._delete(m, obj, mcfg, tbl = 'tbl', op = 'eq')

def _find(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._find(m, obj, mcfg, tbl = 'tbl', op = 'eq')



