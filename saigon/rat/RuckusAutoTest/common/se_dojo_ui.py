import time
import logging
import re

from utils import try_times, try_interval, log_trace

OPTION_CONTAINER = "//div[contains(@class, 'dojoPopupContainer') and not(contains(@style, 'display: none'))]"

Locators = {
    # dojoComboBox is identified by the span tag as below
    #   span[contains(@class, 'dojoComboBoxOuter')]
    'DojoComboBox': {
        'Arrow'          : "/img[contains(@dojoattachevent, 'handleArrowClick')]",
        'OptionContainer': OPTION_CONTAINER,
        'NextPageSign'   : OPTION_CONTAINER + "/div[contains(@class,'dojoComboBoxItem')][contains(@resultname,'previous')]", # template
        'OptionTmpl'     : OPTION_CONTAINER + "/div[contains(@class,'dojoComboBoxItem')][%s][not(contains(@resultname,'previous'))]", # template
        'Textbox'        : "/input[contains(@class,'dojoComboBox body')]"
    },

    # usually this component is defined by <div> tag
    # but sometime, there is no boundary, it can be placed right inside <td> tag
    'DojoNavigator': {
        'DojoComboBox'  : "//span[contains(@class, 'dojoComboBoxOuter')]",
        'PrevBtnEnabled': "//img[contains(@src, '/intune/images/imgArrow_left.gif') and contains(@id, 'Enabled')]",
        'NextBtnEnabled': "//img[contains(@src, '/intune/images/img_Arrow_right.gif') and contains(@id, 'Enabled')]",

        # x-path of next/back button changed in 9.0.0.0.105.
        # Currently cannot use FeatureUpdater here.
        # So this is just a work around do make back compatible.
        'next_btn_enabled':"//img[contains(@src, 'next.gif')]", #new
        'back_btn_enabled':"//img[contains(@src, 'prev.gif')]", #new
    }
}


def get_cb_selected_option(obj, locator):
    '''
    Returning the currently selected option of a combobox
    NOTE: No need for check the locator, it is done on s.get_value()
    '''
    s, l = obj, Locators
    return s.get_value(locator + l['DojoComboBox']['Textbox'])


def get_cb_options(obj, locator, close_menu = True):
    '''
    - locator: locating the dojoComboBoxOuter, usually it is an 'span' tag
    Output:
    - a dictionary of options which has a list of [index and value]
    '''
    return dict([(k, v) for k, v in iter_cb_options(obj, locator, close_menu)])


def _open_and_wait_for_cb_option_list_stable(obj, locator):
    '''
    This function is to list arrow image and wait for elements of the dojo combobox displayed statbly
    '''
    s, l = obj, Locators
    CbArrow = locator + l['DojoComboBox']['Arrow']
    CbLastItem = l['DojoComboBox']['OptionTmpl'] % 'last()'

    # wait until the dropdown menu is displayed and stable enough
    # try re-opening the it a couple of times
    for t in try_times(5, .3):
        try:
            # open the selected menu
            # first time, wait a bit for data to populate
            s.mouse_up(CbArrow)
            time.sleep(1)
            s.check_element_present(CbLastItem, .1)

            time.sleep(1)
            s.check_element_present(CbLastItem, .1)
            return
        except:
            #log_trace()
            pass
    raise Exception('Could not open the list of combobox "%s"' % locator)


def _close_cb(obj, locator):
    '''
    This function is to wait for the combo box closed
    '''
    s, l = obj, Locators
    CbArrow = locator + l['DojoComboBox']['Arrow']
    CbOptionContainer = l['DojoComboBox']['OptionContainer']

    if not s.is_element_present(CbOptionContainer, .3):
        return

    for t in try_times(5, 0):
        s.mouse_up(CbArrow)
        for t2 in try_interval(12, 0):
            if s.is_element_present(CbOptionContainer, .3):
                time.sleep(.3)
            else:
                return
        logging.info('Trying to close element %s %d times' % (CbArrow, t))
    raise Exception('Time out while waiting for Combo Box to be closed')


def _open_cb_option_list(obj, locator):
    """
    Open the Combo box Option list for getting the list details
    """
    s, l = obj, Locators
    CbArrow = locator + l['DojoComboBox']['Arrow']
    CbOptionContainer = l['DojoComboBox']['OptionContainer']
    NextPage = l['DojoComboBox']['NextPageSign']

    s.check_element_present(locator)
    s.check_element_present(CbArrow)

    # make sure there is no menu left opening
    # if it is there, try to close it before opening the selected one
    _close_cb(obj, locator)
    _open_and_wait_for_cb_option_list_stable(obj, locator)

    if s.is_element_present(NextPage, 2):
        s.click_and_wait(NextPage, 3)
        # if found the dojo option has more than two page, need to re-open it again
        _open_and_wait_for_cb_option_list_stable(obj, locator)


def iter_cb_options(obj, locator, close_menu = True):
    """
    - locator: locating the dojoComboBoxOuter, usually it is an 'span' tag
    Output:
    - a dictionary of options which has a list of [index and value]
    """
    s, l = obj, Locators
    CbArrow = locator + l['DojoComboBox']['Arrow']
    CbOptionContainer = l['DojoComboBox']['OptionContainer']
    CbOptionTmpl = l['DojoComboBox']['OptionTmpl']

    _open_cb_option_list(obj, locator)

    # get all the options and return as a tuple: option name,
    # and a list [option index, option value]
    i = 1
    while True:
        CbOption = CbOptionTmpl % i

        # now read the content of each row
        if s.is_element_present(CbOption, 0.2): # optimized for bound checking
            k = s.get_attribute(CbOption + '@resultname')
            v = s.get_attribute(CbOption + '@resultvalue') # actually, not interested in now

            yield k, v # return the current option
        else:
            break
        i += 1

    if close_menu:
        s.mouse_up(CbArrow) # close the content div
        time.sleep(.4)


def select_cb_option(obj, locator, option, exact = True):
    """
    Select a combo box option based on option exact text or regular expression.

    NOTE:
    If there are multiple matches then the first encounter option is selected.
    So make sure your 're' have one match only.

    Input:
    - locator: locating the dojoComboBoxOuter, usually it is an 'span' tag
    - option : an regular expression defining the option or an exact string
    - exact  : for the case there is '1' and '12' and we want to select '1'

    Output:
    - Boolean: True if it is successful, otherwise False
    """
    s, l = obj, Locators
    CbArrow = l['DojoComboBox']['Arrow']
    CbOptionTmpl = l['DojoComboBox']['OptionTmpl']

    if exact:
        # find the option in the options by constructing an absolute xpath
        _open_cb_option_list(obj, locator)
        CbOption = CbOptionTmpl % ("@resultname='%s'" % option)
        if s.is_element_present(CbOption):
            s.safe_click(CbOption)
            time.sleep(.3)
            return True
    else:
        index = -1
        # find the option in the options
        for k, v in iter_cb_options(obj, locator, False):
            if re.compile(option).search(k) != None:
                index = v[0]

            # if it's found, then click
            # the menu is close automatically
            if index != -1:
                CbOption = CbOptionTmpl % index

                s.safe_click(CbOption)
                time.sleep(.3)
                return True

    # close the menu
    _CbArrow = locator + CbArrow
    s.mouse_up(_CbArrow)
    time.sleep(.4)
    raise Exception('Not found option %s' % option)


def get_nav_selected_page(obj, locator):
    """
    deal with Page Navigator controls
    these functions are relied on the combobox inside it

    Returning the selected page of page navigator control
    """
    l = Locators
    return int(
        get_cb_selected_option(obj, locator + l['DojoNavigator']['DojoComboBox']).strip()
    )


def get_nav_total_pages(obj, locator):
    """
    Get the total pages of a page navigator
    """
    s, l = obj, Locators

    PrevBtnEnabled = locator + l['DojoNavigator']['PrevBtnEnabled']
    NextBtnEnabled = locator + l['DojoNavigator']['NextBtnEnabled']
    ComboBox = locator + l['DojoNavigator']['DojoComboBox']
    CbArrow = ComboBox + l['DojoComboBox']['Arrow']
    CbOptionContainer = l['DojoComboBox']['OptionContainer']
    CbOptionTmpl = l['DojoComboBox']['OptionTmpl']

    # is there only one page in this navigator?
    # detect this by checking the prev/next buttons: are they disabled?
    attr = '@class'
    attr_value = 'not-implemented'.strip().upper()

    try:
        if s.get_attribute(PrevBtnEnabled + attr, .2).strip().upper() == attr_value and \
           s.get_attribute(NextBtnEnabled + attr, .2).strip().upper() == attr_value:
            return 1
    except:
        # in the case, it is enabled then the '@class' is not defined
        # obviously, there will be an exception
        pass

    # there are more than 1 page in the navigator
    # open the dropdown list and get the last item
    _open_cb_option_list(obj, ComboBox)

    # get the last option and return as a dictionary with option name as key
    # and a list [option index, option value] as value
    CbOption = CbOptionTmpl % 'last()' # the last item
    s.check_element_present(CbOption)

    # NOTE:
    #   get the last option twice to make sure
    #   it is the real last option
    for t in try_times(5, 0):
        total_1st = s.get_attribute(CbOption + '@resultname')
        time.sleep(.2)
        total_2nd = s.get_attribute(CbOption + '@resultname')

        if total_1st == total_2nd:
            s.mouse_up(CbArrow)
            time.sleep(.4)
            return int(total_1st)
    raise Exception('The dropdown list takes too long to populate ("%s")' % locator)


def go_to_nav_page(obj, locator, page):
    """
    deal with Page Navigator controls
    these functions are relied on the combobox inside it

    Going to a definite page of the page navigator.
    No bound checking is implemented here
    """
    l = Locators
    # TODO: don't go if you are in the selected page now
    return select_cb_option(obj, locator + l['DojoNavigator']['DojoComboBox'],
                          str(page), exact = True)


def iter_nav_pages(se, locator):
    '''
    . iterate through each page on the page navigator
    '''
    next_btn_enable = locator + Locators['DojoNavigator']['next_btn_enabled']

    # assuming we are standing on the first page
    p = 1
    yield p

    while se.is_element_displayed(next_btn_enable, 5):
        p += 1
        se.safe_click(next_btn_enable, 1.5)
        yield p


def iter_nav_pages_reversed(se, locator):
    """
    iterate from the last page to the first page
    """
    l = Locators
    back_btn_enable = locator + l['DojoNavigator']['back_btn_enabled']

    # go to the last page to get total page first.
    for p in iter_nav_pages(se, locator):
        pass

    # assuming we are standing on the last page
    yield p

    while se.is_element_displayed(back_btn_enable, 5):
        p -=1
        se.safe_click(back_btn_enable, 1.5)
        yield p


