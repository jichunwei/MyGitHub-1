'''
2.6.1. Events foundation development
  + Support "Manage Event Views" by:
    + create new search
    + export as xls, cvs
    + save event as view
2.6.2.
  + a tea program to create a search
  + a tea program to save that search as view
  + a tea program to export to xls and cvs

'''


from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns

from RuckusAutoTest.common.utils import download_file
from RuckusAutoTest.components.lib.fm9 import _event_filter as ef


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_views(fm):
    return _get_views(fm)


def get_all_events_by_view_name(fm, view_name = ''):
    return _get_view_events(fm, view_name, {})


def get_all_events_by_filter(fm, options):
    nav_to(fm)
    _fill_in_search_options(fm, options, False)
    return _get_tbl(fm, 'tbl', {}, False)


def create_view(fm, view_name, options):
    nav_to(fm)
    return _create_view(fm, view_name, options)


def export_events_to_file(fm, view_name = '', filetype='xls'):
    '''
    input:
    . filetype: xls | csv are 2 options accepted
    '''
    _set_view(fm, view = view_name, force = False)
    _export_results_to_file(fm, filetype)


def delete_view(): pass


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
DEVICE_VIEW_LINK = "//table[@dojoattachpoint='tableArea']" \
                   "//tr[%s]//span[@class='deviceLink']" % '1'

INPUT_TMPL = "//input[@dojoattachpoint='%s']"
locators = dict(
    tbl = Ctrl(
        dict(tbl = "//table[@automationid='eventtablebody']",
             nav = "//table[@class='pageSelector']",
             search_box = "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
        ),
    ),

    # xport
    xls_export_btn = Ctrl("//input[@type='button'][@value='XLS File']", 'button'),
    csv_export_btn = Ctrl("//input[@type='button'][@value='CSV File']", 'button'),

    # saving
    view_name = Ctrl(INPUT_TMPL % 'viewNameTextField'),
    view_desc = Ctrl(INPUT_TMPL % 'viewDesTextField'),
    save_btn = Ctrl(INPUT_TMPL % 'saveViewButton', 'button'),

    # manage event views
    view_tbl = Ctrl(
        dict(tbl = "//table[@automationid='eventviewTablebody']",
             nav = "//table[@class='pageSelector']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            # link: Edit, Delete, Query
            link = dict(
                lnk_tmpl = "//span[@class='sb'][.='%s']",
                query = "//span[@class='sb'][.='Query']"
            ),
        ),
    ),
)


ctrl_order = '''
tbl xls_export_btn cvs_export_btn
[None view_name view_desc save_btn]
'''

save_view_co = '''
[None view_name view_desc save_btn]
'''

EVENT_FILE_NAME_TMPL = 'Event.%s'


def _get_loc(fm, page):
    return dict(
        event = fm.SYS_ALERTS_EVENTS,
        view = fm.SYS_ALERTS_MANAGE_EVENTS,
    )[page]


def nav_to(fm, page = 'event', force = False):
    fm.navigate_to(fm.SYS_ALERTS, _get_loc(fm, page), force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)


def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)

def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)

def _get_tbl(fm, tbl, cfg, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)


def _get_views(fm):
    nav_to(fm, 'view')
    return _get_tbl(fm, 'view_tbl', {})


def _set_view(fm, view = '', force = False):
    '''
    . if view is given
      . navigate to the manage page, find the view and click on it
    . else just go to the page
    '''
    if not view:
        nav_to(fm, 'event', force)
        return

    view_tbl_cfg = dict(get = '1st', match = dict(viewname = view,))
    nav_to(fm, 'view', force)
    lnk = _get(
        fm, dict(view_tbl = view_tbl_cfg), 'view_tbl'
    )['view_tbl']['links']['query']

    fm.s.safe_click(lnk)
    fm.s.wait_for_page_to_load()
    fm.current_menu = _get_loc(fm, 'event')


def _get_view_events(fm, view = '', match = {}):
    '''
    . set to a view and get all events belong to that view
    . filter by the first match criteria
    '''
    _set_view(fm, view)
    p = {}
    if match:
        p['match'] = match
    return _get_tbl(fm, 'tbl', p, False)


def _get_view_event(fm, match, view = ''):
    '''
    . filter by search_txt then get all table rows
    . if more than one row found then raise an exception
    '''
    evs = _get_view_events(fm, view, match)
    if len(evs) > 1:
        raise Exception('More than one event found')
    if len(evs) <= 0:
        raise Exception('No event found')

    return evs[0]


def _fill_in_search_options(fm, options, get_results = False):
    '''
    . fill in the search criteria on the new search page and search for result
    . after calling this, save_search_results_as_view can be called for saving
      the result
    input
    . a list of criteria, something likes
        options = [
            ['Device Name', 'Contains', 'al'],
            ['Serial Number', 'Starts with', '1008'],
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    nav_to(fm, 'event')
    ef.fill_in(fm, options)
#    if get_results:
        # click query first before getting result
#        return _get_tbl(fm, 'tbl', {}, False)


def _save_search_results_as_view(fm, view_name, description = ''):
    '''
    . save the searched result as a view
    NOTE: this function is called right after fill_in_search_options()
    '''
    p = dict(
        view_name = view_name,
        view_desc = description,
    )
    if not description:
        p['view_desc'] = p['view_name']
    return _set(fm, p, order = save_view_co)


def _create_view(fm, view_name, options):
    _fill_in_search_options(fm, options, False)
    _save_search_results_as_view(fm, view_name)
    nav_to(fm, 'event', True)


def _export_results_to_file(fm, filetype='xls'):
    '''
    . to save the events as an excel/csv file
    NOTE
    . before calling this, make sure you filter your events first
    '''
    filetype2btn_map = dict(
        xls = 'xls_export_btn',
        csv = 'csv_export_btn',
    )
    btn = filetype2btn_map[filetype]

    _get(fm, [btn], btn)
    return download_file(EVENT_FILE_NAME_TMPL % filetype)

