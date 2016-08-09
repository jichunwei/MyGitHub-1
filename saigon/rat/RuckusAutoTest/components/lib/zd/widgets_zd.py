import logging
import time
import re

from RuckusAutoTest.common import utils

map_row = utils.map_row
map_rows = utils.map_rows


# sel24 = "//table[@id='table-ap']//select[@id='wlangroup-11ng']"
# do_select_item(zd, sel24, 'wlan-24')
def do_select_item(zd, element, option, z_incrBy = 0.25, z_tries = 20, z_pause = 0.25):
    if not zd.s.is_element_present(element):
        raise Exception("Element %s not found" % element)

    while z_tries > 0:
        zd.s.select(element, "regexp:^" + option + "$")
        time.sleep(z_pause)
        r_label = "^" + option + "$"
        s_label = zd.s.get_selected_label(element)
        if re.match(r_label, s_label):
            return s_label
        z_tries -= 1
        z_pause += z_incrBy
        if z_tries % 5 == 0:
            logging.info("Select [element %s] failed; retry!" % element)
        time.sleep(z_pause)

def get_checkbox_boolean(zd, loc_checkbox):
    val = zd.s.get_value(loc_checkbox)
    if re.search('off|false|uncheck', val, re.I):
        return False
    else:
        return True

def get_system_version(zd):
    version = ''
    zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
    xpath_ver = "//div[@id='portlet-sysinfo']//td[@id='sysversion']"
    if zd.s.is_element_present(xpath_ver):
        time.sleep(2)
        data = zd.s.get_text(xpath_ver)
        m = re.match(r'([\d.]+)\s+[^\d]+(\d+)', data)
        if m:
            version = m.group(1) + '.' + m.group(2)

    return version

def is_enabled_to_click(zd, locator):
    """
    Support to check the link button object on ZD WebUI if they are enable to click or not
    by verify the 'class' attribute of the object.
    Example: Create New, Edit, Clone buttons ... on ZD WebUI are disable when their 'class'
             attribute is 'sb disabled'.

    SeleniumClient's is_element_disabled() is a duplicated method with this one.
    Consider removing is_element_disabled().
    """
    attributeLocator = '%s@class' % locator
    val = zd.s.get_attribute(attributeLocator)
    if val in ['sb disabled', ]:
        return False

    else:
        return True


def iter_tbl_rows_with_pages(se, tbl, nav, match = {}, op = 'in'):
    '''
    input
    . se: selenium client
    . tbl: table locator
    . nav: navigator locator
    '''
    ths = se.get_tbl_hdrs_by_attr(tbl)
    for p in se.iter_tbl_pages(nav):
        for x in se.iter_table_rows(tbl, ths, match, op = op):
            yield x

    try:
        _clear_search_txt(se, tbl)
    except:
        pass

def get_tbl_rows(se, tbl, nav):
    '''
    '''
    return [r['row'] for r in iter_tbl_rows_with_pages(se, tbl, nav)]


def _clear_search_txt(se, tbl):
    '''
    '''
    t_search_loc = tbl + "/tfoot/tr[@class='t_search']"
    tbl_filter_txt = t_search_loc + "//input[@type='text']"
    if se.is_element_present(t_search_loc, 0.2) and \
    se.is_element_displayed(t_search_loc, 0.2):
        try:
            # clear the text in the filter text
            se.type_text(tbl_filter_txt, '')
            # trigger the key event by 'Line Feed' control character (key code '10')
            # in selenium, the '.' key is not set in type_keys function
            # so we can also use: self.type_keys(tbl_filter_txt, '.')
            se.type_keys(tbl_filter_txt, '\10')

        except:
            pass


def _fill_search_txt(se, loc, txt, wait = 2, timeout = 60):
    # An Nguyen, Apr 2013
    # Added the step to wait for the search text box is present to handle the ajax loading
    se.wait_for_element_present(loc, timeout)
    time.sleep(wait)
    #se.type_text(loc, '') # clear content before type new text in
    #se.type_keys(loc, txt)
    #Chico, 2015-5-5, fix bug ZF-13013
    se.type_text(loc, txt)
    se.type_keys(loc,"\013")
    #Chico, 2015-5-5, fix bug ZF-13013
    time.sleep(wait)


def get_first_row_by(se, tbl, nav, match, filter = None, verbose = False, op = 'in'):
    '''
    get the first row by match criteria
    . filter before getting for fastest accessing
      the first one of match values is used for filtering
    input
    . match: looking up condition, sth likes dict(device_name='Ruckus AP')
    . verbose: only row content or details (row, idx, tmpl)
    '''
    if filter and len(match.values()) > 0:
        _fill_search_txt(se, filter, match.values()[0])

    for r in iter_tbl_rows_with_pages(se, tbl, nav, match, op = op):
        return r if verbose else r['row']

    raise Exception('No matched row found. Match=%s' % match)

def get_tbl_rows_by(se, tbl, nav, match, filter = None, verbose = False, op = 'in'):
    '''
    get the rows by match criteria
    . filter before getting for fastest accessing
      the rows of match values is used for filtering
    input
    . match: looking up condition, sth likes dict(device_name='Ruckus AP')
    . verbose: only row content or details (row, idx, tmpl)
    '''
    if filter and len(match.values()) > 0:
        _fill_search_txt(se, filter, match.values()[0])

    rows = []

    for r in iter_tbl_rows_with_pages(se, tbl, nav, match, op = op):
        if verbose:
            rows.append( r )
        else:
            rows.append( r['row'])
#        rows.append( r ) if verbose else r['row']

    return rows

def _set_tbl_col_to_sort(se, tbl, sort_context, wait = 2):
    sort_field_loc = tbl + "//th[@attr='%s']" % sort_context['field']
    sort_type = sort_context['type']
    cnt = 4

    while cnt:
        se.click(sort_field_loc)
        time.sleep(wait)
        if se.get_attr(sort_field_loc, "class").lower() == ("sortable-%s" % sort_type.lower()):
            return True
        cnt = cnt - 1

    raise Exception("sort function can't work correctly")


def sort_tbl_col_by(se, tbl, nav, match, sort, filter = None, verbose = False, wait = 2):
    '''
    sort the columns by match criteria
    . filter before getting for fastest accessing
      the rows of match values is used for filtering
    input
    . match: looking up condition, sth likes dict(device_name='Ruckus AP')
    . sort:  sort option, for example: dict(field='mac', type='asc')
    . verbose: only row content or details (row, idx, tmpl)
    '''
    sort_context = dict(field='mac', type='asc')
    sort_context.update(sort)
    _set_tbl_col_to_sort(se, tbl, sort_context, wait = wait)

    if filter and len(match.values()) > 0:
        return get_tbl_rows_by(se, tbl, nav, match, filter = filter, verbose = verbose)

    else:
        return get_tbl_rows(se, tbl, nav)

def _drag_the_widget_out_to_dashboard(zd, widget_title, target_location, **kwargs):
    """
    This function support to add a widget to the ZD Dashboard page.
    widget_title: is the title of the widget we want to drag out.
    target_location: the expected location to drop the widget.
    """
    conf = {'sleep_time': 2}
    if kwargs:
        conf.update(kwargs)

    add_widget = zd.info['loc_dashboard_add_widgets']
    finish_add_widget = zd.info['loc_dashboard_finish_add_widgets']
    wg_locator = zd.info['loc_dashboard_portlet'] % widget_title

    zd.s.click(add_widget)
    zd.s.drag_and_drop_to_object(wg_locator, target_location)
    time.sleep(conf['sleep_time'])

    zd.s.click(finish_add_widget)

def drag_the_widget_out_to_dashboard(zd, widget_title, target_location, **kwargs):
    _drag_the_widget_out_to_dashboard(zd, widget_title, target_location, **kwargs)

