import logging
import time
from pprint import pformat

from RuckusAutoTest.common.utils import try_times, try_interval
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import (
        map_summary_to_provisioning_cfg, map_cfg_value
)


# we ignore case and blank in the title
MAC_ADDRESS_TITLE = 'macaddress' # MAC Address
SERIAL_NUMBER_TITLE = 'serialnumber' # Serial Number

Locators = dict(
    SsidRefreshBtn = "//img[@id='refresh-ssid']",
#    SsidTbl = "//table[@id='tbody-ssid-1']",
    StationLinkTmpl = "//div[@id='tb-ssid-panel']//tr[%s]//img[contains(@title, 'associated stations')]",
    WlanCfgLinkTmpl = "//div[@id='tb-ssid-panel']//tr[%s]//img[contains(@title, 'wireless settings')]",
    StationPane = "//div[@id='wireless-association']",
    StationTbl = "//div[@id='wireless-association']//table",

    # Locators for summary of wireless common and detail
    DisabledImgTmpl = "//div[@id='tb-ssid-panel']//tr[%s]//img[contains(@title, 'disbled')]",
    EnabledImgTmpl = "//div[@id='tb-ssid-panel']//tr[%s]//img[contains(@title, 'disbled')]",
    WlanSettingLinkTmpl = "//div[@id='tb-ssid-panel']//tr[%s]//img[contains(@title, 'View wireless settings')]",
    WlanCommonTbl = "//div[@id='div-wireless-common']//table",
    WlanDetTbl = "//div[@id='wireless-setting']//table",
    # this is a locator for the encryption mode table
    EncryptInfoTbl = "//div[@id='wireless-setting']//table//fieldset/table",

    GeneralTab = "//span[contains(., 'General')]",
    EventTab = "//span[contains(., 'Event')]",
    GeneralRefreshBtn = "//img[contains(@title, 'Refresh')]",
    GeneralTbl = "//table[@class='displayDiv']",
    ErrorPane = "//td[@class='MsgWindowError']", # This pane will be present if cannot find a serial or MAC address

    SerialNumberTxt = "//input[@id='serialNumber']",
    MACAddressTxt = "//input[@id='MACAddress']",
    FindBtn = "//input[@id='cmdsearch']",
)


NoAssocStationMsg = 'Unable to find any associated stations'.lower()


def nav_to(dv, force = False):
    return dv.navigate_to(dv.SUMMARY, dv.NOMENU, force)


def _openWlanDetailPane(dv, wlan = 1, link = Locators['StationLinkTmpl']):
    '''
    . Open the detail pane of given SSID
    params:
    . wlan: starting from 1
    . pane: what pane to open?
    '''
    s, l = dv.selenium, Locators
    nav_to(dv)
    s.click_and_wait(l['SsidRefreshBtn'])
    s.click_and_wait(link % wlan)


def getAssocClients(dv, wlan = 1, timeout = 50):
    '''
    . get the list of associated stations based on given wireless
    . tries a couple times since this table is not updated instantly
    . return [], in case, there is no assoc stations
    NOTE:
    . in case, you want to get this once, set timeout = 0
    '''
    s, l = dv.selenium, Locators
    logging.info('Get the list of associated clients... trying within %s secs' % timeout)
    _openWlanDetailPane(dv, wlan)

    # a little hack here to make sure we can get the latest data
    for z in try_times(3, 2):
        s.click_and_wait(l['SsidRefreshBtn'])

    for z in try_interval(timeout, 2):
        s.click_and_wait(l['SsidRefreshBtn'])
        msg = s.get_text(l['StationPane'])
        if NoAssocStationMsg not in msg.lower():
            return s.get_vtable(l['StationTbl'])
    return []


#def getDeviceSummary(dv):
#    '''
#    This function is to get Device View Summary
#    Input:
#    - dv: Device View object.
#    Ouput:
#    - a dictionary of items on Device Summary page
#    Model Type:                                ZF2942
#    Customer ID:                            4bss
#    Device Name:                            RuckusAP
#    MAC Address:                        00:1D:2E:16:1C:A0
#    Serial Number:                        430701000477
#    Firmware Version:                    0.0.0.0.161
#    Service Provider Login Name:        super
#    Device Last Seen:                    May. 11 2009 10:08:40
#    IP Address:                            192.168.0.222
#    Server URL:                            https://192.168.0.124/intune/server
#    Periodic Inform Status:                Enabled
#    Periodic Inform Interval:            15 minutes
#    Uptime:    1d 18h 9m
#    Associated-Clients Monitoring Mode:    Disabled
#    '''
#    s, l = dv.selenium, Locators
#    nav_to(dv)
#    # go to expect tab
#    s.click_and_wait(l['GeneralTab'] % tab)
#    # click Refresh button
#    s.click_and_wait(l['GeneralRefreshBtn'] % tab)
#
#    return s.get_htable_content(l['GeneralTbl'])


def findDevice(dv, id, bySerial = True):
    '''
    This function is to find a device by serial or MAC address
    Input:
    - dv: Device View instance
    - id: a serial number or MAC address
    - bySerial: True if search a device by serial. Otherwise, search a device by MAC
    output:
    True/False: True if find the device esle False
    '''
    s, l = dv.selenium, Locators
    nav_to(dv)

    search_loc, title = (l['SerialNumberTxt'], SERIAL_NUMBER_TITLE) \
                        if bySerial else \
                        (l['MACAddressTxt'], MAC_ADDRESS_TITLE)


    s.type_text(search_loc, id)
    s.click_and_wait(l['FindBtn'])

    if not s.is_element_present(l['ErrorPane']) and \
        s.get_htable_value(l['GeneralTbl'], title, True).lower() == id.lower():
        return True

    return False

'''
'wmode': ['auto', '11g'], #version 8.0 has removed '11b'
'channel': ['0','1','2','3','4','5','6','7','8','9','10','11'], #0 to 11
'channel_width'
# David talked to me that, TDC FM team agree doesn't need to test country coe
# so I (Hieu Phan) commented it out.
# 'country_code': 'CA',#'AU, AT, ...',
'txpower': ['max', 'half', 'quarter', 'eighth', 'min'],
'prot_mode': ['Disabled', 'CTS-only', 'RTS-CTS'],
'''

# Keys of this dict are title of common table content. And Values of this
# dictionarys are keys of output and they will be used to compare
MAP_WLAN_COMMON_KEYS = dict(
    wirelessmode = 'wmode', #Wireless Mode
    channel = 'channel',
    countrycode = 'country_code',
    channelwidth = 'channel_width',
    transmitpower = 'txpower',
    protectionmode = 'prot_mode',
)
'''
'avail': ['Disabled','Enabled'],#Enabled, Disabled
'broadcast_ssid': ['Disabled','Enabled'], #Enabled, Disabled
'client_isolation': ['Disabled','Enabled'],#Enabled, Disabled
'wlan_name': 'fm_auto_test_%d',
'wlan_ssid': 'fm_auto_test_%d',
'dtim': ['200', '255'],
'rtscts_threshold': ['2000','2346'],
'''

'''
Total Packets Sent:        0

Total Packets Received:           0
  Total Bytes Sent:
                                  0
   Total Bytes Received:          0
   Total Associations:
'''
removed_list = ['bssid', ]

'''
encrypt_method': 'WPA',#'Disabled, WEP, WPA',
        'wpa_version': _kwa['version'],#'WPA version: WPA, WPA2, Auto',
        'wpa_algorithm': _kwa['algorithm'],#'WPA Algorithm: TKIP, AES, Auto',
        'auth': _kwa['auth'],
'''

def getWLANCommon(dv):
    '''
    This function is to get wlan common config on the Summary page.
    Input:
    - dv: device view object
    - wlan: wlan 1 to 8 to get info
    Output:
    - Return in FM format cfg as getting them from libFM_TestSuite
    '''
    s, l = dv.selenium, Locators
    nav_to(dv, True)
    logging.info('Getting summary cfg of WLAN Common')
    # click refresh button
    s.click_and_wait(l['SsidRefreshBtn'])
    # just click a wlan detail to get wlan common info
    s.click_and_wait(l['WlanSettingLinkTmpl'] % 1)
    # get encryption info
    summary_items = s.get_htable_content(l['WlanCommonTbl'], ignore_case = True)
    # Antenna
    # client_isolation: this item is not available on AP Web UI
    removed_items = ['antenna', ]
    # remove items which cannot be verified or don't need to verify
    for k in removed_items:
        # Some item only available on either 2942 or 7942 so we need to do check
        # before delete it
        if summary_items.has_key(k): del summary_items[k]

    # Convert the returned items to keys as they are in provisioning config.
    # The purpose is to compare the output
    provisioning_items = map_summary_to_provisioning_cfg(summary_items)
    logging.info('Summary cfg: %s' % pformat(provisioning_items))

    return map_cfg_value(provisioning_items, False)


def getWLAN(dv, wlan = 1):
    '''
    This function is to get wlan detail config on the Summary page.
    Input:
    - dv: device view object
    - wlan: wlan 1 to 8 to get info
    Output:
    - Return in FM format cfg as getting them from libFM_TestSuite
    '''
    s, l = dv.selenium, Locators
    nav_to(dv, True)
    logging.info('Getting summary cfg of wlan %s' % wlan)
    # click refresh button
    s.click_and_wait(l['SsidRefreshBtn'])

    # click a wlan to get the detail
    s.click_and_wait(l['WlanSettingLinkTmpl'] % wlan)
    # get encryption info
    summary_items = s.get_htable_content(l['WlanDetTbl'], ignore_case = True)

    # get encryption items if they are available
    if s.is_element_present(l['EncryptInfoTbl']):
        # NOTE: this table is a sub-table of summary table, the get_htable_content
        # cannot get sub-items of the sub-table so at this step the output will
        # have a key like " u'encryptionmodemode': u'WEPAuthentication Mode:OPENEncryption Strength:64bit 5 ascii keysWEP Key:12345Key Index:1',"
        # We need to remove this key and invoke get_htable_content again to get the sub-items.
        del summary_items['encryptionmodemode']
        summary_items.update(s.get_htable_content(l['EncryptInfoTbl'], ignore_case = True))

    # client_isolation: this item is not available on AP Web UI
    removed_items = ['clientisolation', 'bssid', 'totalassociations', 'totalbytesreceived',
                     'totalbytessent', 'totalpacketsreceived', 'totalpacketssent',
                     'noisefloor']
    # remove items which cannot be verified or don't need to verify
    for k in removed_items:
        # Some item only available on either 2942 or 7942 so we need to do check
        # before delete it
        if summary_items.has_key(k): del summary_items[k]

    # Convert the returned items to keys as they are in provisioning config.
    # The purpose is to compare the output
    provisioning_items = map_summary_to_provisioning_cfg(summary_items)
    logging.info('Summary cfg: %s' % pformat(provisioning_items))

    return map_cfg_value(provisioning_items, False)
