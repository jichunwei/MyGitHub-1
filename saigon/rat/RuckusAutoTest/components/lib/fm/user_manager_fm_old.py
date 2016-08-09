from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *

Locators = dict(
    Tbl = "//table[@id='UserList']",
    DeleteLinkTmpl = "//table[@id='UserList']//tr[%s]/td/a[.='Delete']",
    EditLinkTmpl = "//table[@id='UserList']//tr[%s]/td/a[.='Edit']",

    Nav = "//td[@class='pageSelecter']",

    NewLink = "//div[@id='new-ap']//span[contains(.,'Create')]",

    UserNameTxt = "//input[@id='txtUserName']",
    PasswordTxt = "//input[@id='txtPass']",
    ConfirmPasswordTxt = "//input[@id='txtPass1']",
    RoleCb = "//select[@id='selUserRole']",
    OkBtn = "//input[@id='ok-ap']",
)


def add_user(fm, **kwa):
    '''
    kwa:
    - username
    - password
    - role
    '''
    s, l = fm.selenium, Locators

    fm.navigate_to(fm.ADMIN, fm.ADMIN_USERS)
    s.click_and_wait(l['NewLink'])
    s.type_text(l['UserNameTxt'], kwa['username'])
    s.type_text(l['PasswordTxt'], kwa['password'])
    s.type_text(l['ConfirmPasswordTxt'], kwa['password'])
    s.select_option(l['RoleCb'], kwa['role'])
    s.click_and_wait(l['OkBtn'])


def _delete_all_deletable_users(row):
    '''
    return:
    . isAdvance and isReturn as a tuple
    '''
    if 'delete' in row['Action'].lower():
        return False, True
    return True, False


def delete_all_users(fm):
    '''
    go through the list of users, delete them all
    '''
    s, l = fm.selenium, Locators

    fm.navigate_to(fm.ADMIN, fm.ADMIN_USERS, force = True)
    for r, i, tmpl in s.iter_vtable_rows(l['Tbl'], verbose = True,
                                       compare_method = _delete_all_deletable_users):
        s.safe_click(l['DeleteLinkTmpl'] % i)
    fm.navigate_to(fm.ADMIN, fm.ADMIN_USERS, force = True) # hack


def find_user(fm, **kwa):
    '''
    - Click on refresh button for getting latest data
    - Find and return the row
    kwa:
    - criteria: something likes
                {'User Name': 'a',}
    return:
    - the first matched row (and its index, template) or None, None, None
    '''
    s, l = fm.selenium, Locators

    fm.navigate_to(fm.ADMIN, fm.ADMIN_USERS)
    p = dict(table = l['Tbl'], navigator = l['Nav'])
    p.update(kwa)
    return fm.find_list_table_row(**p)


def get_all_users(fm):
    '''
    Get all user info from Users table
    '''
    s, l = fm.selenium, Locators

    fm.navigate_to(fm.ADMIN, fm.ADMIN_USERS)
    return fm.get_list_table(table = l['Tbl'], navigator = l['Nav'], ignore_case = True)

