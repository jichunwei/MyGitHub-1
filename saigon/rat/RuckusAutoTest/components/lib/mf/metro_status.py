
import time

#this function is unique to 7211
def get_system_status(mf_obj):
     content = mf_obj._get_status(mf_obj.STATUS_SYSTEM, -1, \
                               mf_obj.info['StatusDeviceTbl'])
     #no need to check because table always exists
     content.update(mf_obj._get_status(mf_obj.STATUS_SYSTEM, -1, \
                                    mf_obj.info['StatusInternetConnTbl'], False))
     return content

 #this function is unique to 7211
def get_wireless_status(mf_obj,iface):
     if (iface == 'wan'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WAN)
     elif (iface == 'wlan1'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WLAN_1)
     elif (iface == 'wlan2'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WLAN_2)
     content = []
     ItemTbl = mf_obj.info['StatusInternetGeneralTbl']
     ConnectedDevicesTbl = mf_obj.info['StatusInternetConnTbl']
     # get the general info of the wlan
     content.append(mf_obj.s.get_htable_content(ItemTbl))
     # get connected devices (if exists)
     if(mf_obj.s.is_element_present(ConnectedDevicesTbl)):
         content.append(mf_obj.s.get_htable_content(ConnectedDevicesTbl))
     return content

def get_statistic(mf_obj,iface,mac,quit=True):
     """
     if quit=False then stat page will remain there. Use with "reset_statistic()" or "enable_auto_update()"
     Could result in navigation error if access STATUS_WAN, STATUS_WLAN_1, STATUS_WLAN_2
     """
     if (iface == 'wan'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WAN)
     elif (iface == 'wlan1'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WLAN_1)
     elif (iface == 'wlan2'):
         mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WLAN_2)
     statistic = "//a[contains(@href,'/sWirelessStation.asp?mac=%s')]" %mac 
     mf_obj.s.safe_click(statistic)
     time.sleep(6)
     content = []
     content.append(mf_obj.s.get_htable_content(mf_obj.info['StatusDeviceTbl']))
     if quit == True:
          mf_obj.navigate_to(mf_obj.STATUS_DEVICE, -1)
     return content

def reset_statistic(mf_obj):#call this function only after successful "get_statistic"
     mf_obj.s.safe_click(mf_obj.info['stats'])
     
#this function override
def get_internet_status(mf_obj):
     content = mf_obj._get_status(mf_obj.STATUS_INTERNET, -1, \
                               mf_obj.info['StatusInternetGeneralTbl'])
     content.update(mf_obj._get_status(mf_obj.STATUS_INTERNET, -1, \
                                    mf_obj.info['StatusInternetConnTbl'], False))
     hdrs = ['Flag Mode','Last Flag Mode']  # to work around function _get_htable_row, since it requires unused parameter
     locator = mf_obj.info['StatusInternetConnTbl']
     # added more attributes unique to 7211
     # This is a hack since i'm strictly using ONLY functions AVAILABLE inside SeleniumClient
     contents = {}
     contents['Authenticated']= mf_obj.s._get_htable_row(locator,hdrs,2)
     contents['Associated']= mf_obj.s._get_htable_row(locator,hdrs,3)
     contents['Authorized']= mf_obj.s._get_htable_row(locator,hdrs,4)
     contents['Valid Ip Address']= mf_obj.s._get_htable_row(locator,hdrs,5)
     content['Flag Mode']= mf_obj.s._get_htable_row(locator,hdrs,7)
     content['Last Flag Mode']= mf_obj.s._get_htable_row(locator,hdrs,8)
     content.update(contents)
     return content

#this function override
def get_wireless_common_status(mf_obj):
     return mf_obj._get_status(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_COMMON, \
                            mf_obj.info['StatusDeviceTbl'])#update correct table to access status-wireless-common

 #this function is unique to 7211

def get_air_quality(mf_obj,main_page=True):
    """
    True: navigate to main_page which has air quality,
    False: navigate to wan_page which also has air quality
    """
    if main_page:
        mf_obj.navigate_to(mf_obj.MAIN_PAGE, -1, timeout = 20)
    elif not main_page:#another wan page that has air quality
        mf_obj.navigate_to(mf_obj.STATUS_WIRELESS, mf_obj.STATUS_WAN, timeout = 20)

    signal = mf_obj.s.get_attr('//img[@title="Air Quality"]','src')
    bar = 6
    if signal == "../images/level5.gif":
        bar = 5
    elif signal == "../images/level4.gif":
        bar = 4
    elif signal == "../images/level3.gif":
        bar = 3
    elif signal == "../images/level2.gif":
        bar = 2
    elif signal == "../images/level1.gif":
        bar = 1
    else:
        raise Exception ("No Air Quality")
    return bar

 #this function is unique to 7211
def dhcp_action_release(mf_obj):
     mf_obj.navigate_to(mf_obj.STATUS_INTERNET, -1, timeout = 20)
     mf_obj.s.safe_click(mf_obj.info['release'])
     time.sleep(2)

 #this function is unique to 7211
def dhcp_action_renew(mf_obj):
     mf_obj.navigate_to(mf_obj.STATUS_INTERNET, -1, timeout = 20)
     mf_obj.s.safe_click(mf_obj.info['renew'])
     time.sleep(2)


 #this function is unique to 7211
def enable_auto_update(mf_obj):
    """remember to navigate to intended page"""
    value = mf_obj.s.get_attr("//input[@type='submit']",'name')
    if value == 'enableautoupdate':
        mf_obj.s.safe_click(mf_obj.info['enable_auto_update'])
        mf_obj.s.wait_for_page_to_load()
        time.sleep(2)
    elif value != None:
        raise Exception('Cannot enable because it is '+ value)


 #this function is unique to 7211
def disable_auto_update(mf_obj):
    """remember to navigate to intended page"""
    value = mf_obj.s.get_attr("//input[@type='submit']",'name')
    if value == 'disableautoupdate':
        mf_obj.s.safe_click(mf_obj.info['disable_auto_update'])
        mf_obj.s.wait_for_page_to_load()
        time.sleep(2)
    elif value != None:
        raise Exception('Cannot enable because it is '+ value)