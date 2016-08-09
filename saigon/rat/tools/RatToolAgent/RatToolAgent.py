import os
import re
import sys
import platform
import traceback
import time
import tempfile
import subprocess
import socket
try:
    import paramiko
except:
    pass
from SocketServer import TCPServer, StreamRequestHandler
from pywinauto import controls
from pywinauto import application
from win32gui import SetFocus, BringWindowToTop, SetForegroundWindow
from pywinauto.findwindows import find_windows
import SendKeys
import string
from process import createProcess
from RuckusAD import RuckusAD
import TsharkAgent as TA
import ZapAgent as ZA
from DialogHandler2 import DialogHandler2

IPV4 = 'ipv4'
IPV6 = 'ipv6'
DUAL_STACK = 'dualstack'

_adapter_name = ""
_adapter_guid = ""
_adapter_desc = ""
_is_wifi_card = True
_wlantool_cmd = "wlanman.exe"
_zap_cmd = "zap.exe"
_zap_cvs_file = "zap.csv"
_service_port = 10010 if not os.environ.has_key('_SERVICE_PORT') else int(os.environ['_SERVICE_PORT'])
_certmgr_cmd = "certmgr.exe -del -all -s -c my"
_zing_cmd = "zing.exe"
_zing_cvs_file = "zing.csv"
_windump_cmd = "Windump.exe"
_windump_process = ""

_tshark_cmd=r'C:\PROGRA~1\wireshark\tshark'
_pskill_cmd=r'C:\bin\win\pskill'
_tshark_process = ""
_tshark_capture_file = "tshark_capture.pcap"
            
_iperf_cmd = "iperf.exe"
_iperf_process = ""
_windump_capture_file = "windump_capture.pcap" if not os.environ.has_key('_WINDUMP_CAPTURE_FILE') else os.environ['_WINDUMP_CAPTURE_FILE']

_arping_tool = "hardping.exe"

##################################################################################
# For XP only; seems not working on Vista anyway
# During Wireless Card configuration; wireless card will be reseted
_devcon_cmd = "devcon.exe"
_adapter_vid = ''#You must provide for adapter_vid info when do testing in 802.1x ethernet
#
# Example vid name:
# _adapter_vid = "PCI\VEN_1814*DEV_0781*SUBSYS_27901814*"
#
# HOWTO find adapter's VID:
# Run this command to get your wireless card's VID
#
#   devcon.exe find *
#
# and looking for string "Wireless" that contain your wireless card's description
# and copy it to _adapter_vid, change non-alphnum to *
# To check wireless card name go to
#   Computer>Property>Hardware>Device Manager>Network adapters
#
_debug = False
def _dispmsg(_line):
    if _debug or os.path.exists('_DEBUG_ON'):
        print _line


def _exec_program(cmd_line):
    """
    [TAK@20081028]
    Use this method to execute an external program and get its output back.
    We need to change os.system() and os.pipe() to use this command.
    Some of them did not call close().
    @param cmd_line: the string to execute the command in command window.
    """
    _dispmsg("[EXEC PROGRAM] %s" % cmd_line)
    output = subprocess.Popen(cmd_line, stdout = subprocess.PIPE).communicate()[0]
    return output


def _get_adapter_description(adapter_name):
    output = os.popen("ipconfig /all")
    found_name = False
    desc = ""

    for line in output:
        line = line.strip()
        if not line:
            if found_name and desc: break
            continue
        if line.find(adapter_name) != -1:
            found_name = True
        elif found_name:
            x = line.split(':')
            tag = x[0].rstrip('. ')
            val = x[1].lstrip(' ')
            if tag == "Description":
                desc = val
    output.close()
    return desc


def _get_adapter_name(adapter_desc):
    output = os.popen("ipconfig /all")
    name = "UNKNOWN"
    for line in output:
        line = line.strip()
        if not line: continue
        x = line.split(":")
        if len(x) == 1: continue
        if not x[1]:
            y = x[0].split("adapter")
            if len(y) == 2:
                name = y[1].strip()
                continue
        tag = x[0].strip(". ").strip()
        val = x[1].strip()
        if tag == "Description":
            if val in adapter_desc: break
            else: name = "UNKNOWN"
    output.close()
    return name


def _update_guid(adapter_name = ""):
    """
    Update the friendly name (if specified) and the GUID of the wireless adapter
    Input:
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_name, _adapter_desc, _adapter_guid, _wlantool_cmd
    
    #Add by cwang@20130510, skip update while _adapter_guid which has been put by manual.
    if _adapter_guid:
        return

    if ((adapter_name and adapter_name == _adapter_name) or \
        (not adapter_name and _adapter_name)) and _adapter_desc:
        pass

    if adapter_name:
        _adapter_name = adapter_name
        _adapter_desc = _get_adapter_description(adapter_name)

    if _adapter_desc:
        desc_pattern = "%s.*" % re.escape(_adapter_desc)
    else:
        desc_pattern = ".*"

    cmd_line = "%s ei" % _wlantool_cmd
    _dispmsg("[EXEC CMD]: %s" % (cmd_line))
    output = os.popen(cmd_line)
    buffer = "".join(line for line in output)
    output.close()

    pattern = r"Interface \d+:\s+GUID: ([\da-fA-F-]+)\s+"
    pattern += r"(" + desc_pattern + r")\s+"
    pattern += "State: \"(connected|disconnecting|disconnected|associating|discovering|authenticating)\""

    obj = re.search(pattern, buffer)
    if not obj:
        raise Exception("Unable to get GUID of the wireless adapter: %s" % buffer)
    _adapter_guid = obj.group(1)
    _dispmsg("[INFO _adpater_guid]: %s" % (_adapter_guid))
    if not _adapter_desc:
        _adapter_desc = obj.group(2)
        _dispmsg("[INFO _adpater_desc]: %s" % (_adapter_desc))
    if not _adapter_name:
        _adapter_name = _get_adapter_name(_adapter_desc)
        _dispmsg("[INFO _adpater_name]: %s" % (_adapter_name))


def _make_wlan_profile_xml(ssid, auth_method, encrypt_method, key_type = "", key_material = "", key_index = "", use_onex = False):
    """
    Use this function to generate a WLAN profile using WLANProfile schema (Native Wifi)
    @param ssid: a string represents the SSID
    @param auth_method: one of the authentication methods including "open", "shared", "WPA", "WPAPSK",
                  "WPA2", and "WPA2PSK"
    @param encrypt_method: one of the encryption methods including "none", "WEP", "TKIP" and "AES"
    @param key_type: one of the key types including "passPhrase" or "networkKey"
    @param key_index: WEP key index, can be 1, 2, 3 or 4
    @param key_material: the key string
    @param use_onex: True if the profile includes 802.1x authentication configuration, otherwise use False

    @return: path to the XML file
    """

    # Try to generate a temporary file for storing the XML profile
    fd, path = tempfile.mkstemp(".xml")

    # Fill the content
    os.write(fd, '<?xml version="1.0"?>\n')
    os.write(fd, '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">\n')
    os.write(fd, '        <name>' + ssid + '</name>\n')
    os.write(fd, '        <SSIDConfig>\n')
    os.write(fd, '                <SSID>\n')
    os.write(fd, '                        <name>' + ssid + '</name>\n')
    os.write(fd, '                </SSID>\n')
    os.write(fd, '        </SSIDConfig>\n')
    os.write(fd, '        <connectionType>ESS</connectionType>\n')
    os.write(fd, '        <MSM>\n')
    os.write(fd, '                <security>\n')
    os.write(fd, '                        <authEncryption>\n')
    os.write(fd, '                                <authentication>' + auth_method + '</authentication>\n')
    os.write(fd, '                                <encryption>' + encrypt_method + '</encryption>\n')
    if use_onex:
        os.write(fd, '                                <useOneX>true</useOneX>\n')
    else:
        os.write(fd, '                                <useOneX>false</useOneX>\n')
    os.write(fd, '                        </authEncryption>\n')


    if not use_onex:
        # 802.1x is not applied
        if len(key_type) > 0:
            os.write(fd, '                        <sharedKey>\n')
            os.write(fd, '                                <keyType>' + key_type + '</keyType>\n')
            os.write(fd, '                                <protected>false</protected>\n')
            os.write(fd, '                                <keyMaterial>' + key_material + '</keyMaterial>\n')
            os.write(fd, '                        </sharedKey>\n')

        if key_index:
            os.write(fd, '                        <keyIndex>' + str(int(key_index) - 1) + '</keyIndex>\n')


    else:
        # 802.1x is applied
        os.write(fd, '                        <OneX xmlns="http://www.microsoft.com/networking/OneX/v1">\n')
        if get_win_version() in ['61']:
            os.write(fd, '                                <cacheUserData>true</cacheUserData>\n')
            os.write(fd, '                                <authMode>user</authMode>\n')

        os.write(fd, '                                <EAPConfig>\n')
        os.write(fd, '                                        <EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig" \n')
        os.write(fd, '                                                       xmlns:eapCommon="http://www.microsoft.com/provisioning/EapCommon" \n')
        os.write(fd, '                                                       xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapMethodConfig">\n')
        os.write(fd, '                                                <EapMethod>\n')
        os.write(fd, '                                                        <eapCommon:Type>25</eapCommon:Type>\n')
        os.write(fd, '                                                        <eapCommon:AuthorId>0</eapCommon:AuthorId>\n')
        os.write(fd, '                                                </EapMethod>\n')
        os.write(fd, '                                                <Config xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1" \n')
        os.write(fd, '                                                        xmlns:msPeap="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV1" \n')
        os.write(fd, '                                                        xmlns:msChapV2="http://www.microsoft.com/provisioning/MsChapV2ConnectionPropertiesV1">\n')
        os.write(fd, '                                                        <baseEap:Eap>\n')
        os.write(fd, '                                                                <baseEap:Type>25</baseEap:Type>\n')
        os.write(fd, '                                                                <msPeap:EapType>\n')
        os.write(fd, '                                                                        <msPeap:FastReconnect>false</msPeap:FastReconnect>\n')
        os.write(fd, '                                                                        <msPeap:InnerEapOptional>0</msPeap:InnerEapOptional>\n')
        os.write(fd, '                                                                        <baseEap:Eap>\n')
        os.write(fd, '                                                                                <baseEap:Type>26</baseEap:Type>\n')
        os.write(fd, '                                                                                <msChapV2:EapType>\n')
        os.write(fd, '                                                                                        <msChapV2:UseWinLogonCredentials>false</msChapV2:UseWinLogonCredentials>\n')
        os.write(fd, '                                                                                </msChapV2:EapType>\n')
        os.write(fd, '                                                                        </baseEap:Eap>\n')
        os.write(fd, '                                                                        <msPeap:EnableQuarantineChecks>false</msPeap:EnableQuarantineChecks>\n')
        os.write(fd, '                                                                        <msPeap:RequireCryptoBinding>false</msPeap:RequireCryptoBinding>\n')
        os.write(fd, '                                                                        <msPeap:PeapExtensions />\n')
        os.write(fd, '                                                                </msPeap:EapType>\n')
        os.write(fd, '                                                        </baseEap:Eap>\n')
        os.write(fd, '                                                </Config>\n')
        os.write(fd, '                                        </EapHostConfig>\n')
        os.write(fd, '                                </EAPConfig>\n')
        os.write(fd, '                        </OneX>\n')
        # End of if use_onex


    os.write(fd, '                </security>\n')
    os.write(fd, '        </MSM>\n')
    os.write(fd, '</WLANProfile>')

    os.close(fd)
    return path


def _make_user_credential_xml(username, password):
    """
    This function defines user credential in EAP schema
    @param username: EAP credential
    @param password: EAP credential
    @return: path to the XML file
    """
    fd, path = tempfile.mkstemp(".xml")

    os.write(fd, '<?xml version="1.0" ?>\n')
    os.write(fd, '    <EapHostUserCredentials xmlns="http://www.microsoft.com/provisioning/EapHostUserCredentials" \n')
    os.write(fd, '                            xmlns:eapCommon="http://www.microsoft.com/provisioning/EapCommon" \n')
    os.write(fd, '                            xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapMethodUserCredentials">\n')
    os.write(fd, '        <EapMethod>\n')
    os.write(fd, '            <eapCommon:Type>25</eapCommon:Type>\n')
    os.write(fd, '            <eapCommon:AuthorId>0</eapCommon:AuthorId>\n')
    os.write(fd, '        </EapMethod>\n')
    os.write(fd, '        <Credentials xmlns:eapUser="http://www.microsoft.com/provisioning/EapUserPropertiesV1" \n')
    os.write(fd, '                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n')
    os.write(fd, '                     xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1" \n')
    os.write(fd, '                     xmlns:MsPeap="http://www.microsoft.com/provisioning/MsPeapUserPropertiesV1" \n')
    os.write(fd, '                     xmlns:MsChapV2="http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1">\n')
    os.write(fd, '            <baseEap:Eap>\n')
    os.write(fd, '                <baseEap:Type>25</baseEap:Type>\n')
    os.write(fd, '                <MsPeap:EapType>\n')
    os.write(fd, '                    <MsPeap:RoutingIdentity>test</MsPeap:RoutingIdentity>\n')
    os.write(fd, '                    <baseEap:Eap>\n')
    os.write(fd, '                        <baseEap:Type>26</baseEap:Type>\n')
    os.write(fd, '                        <MsChapV2:EapType>\n')
    os.write(fd, '                            <MsChapV2:Username>' + username + '</MsChapV2:Username>\n')
    os.write(fd, '                            <MsChapV2:Password>' + password + '</MsChapV2:Password>\n')
    os.write(fd, '                        </MsChapV2:EapType>\n')
    os.write(fd, '                    </baseEap:Eap>\n')
    os.write(fd, '                </MsPeap:EapType>\n')
    os.write(fd, '            </baseEap:Eap>\n')
    os.write(fd, '        </Credentials>\n')
    os.write(fd, '    </EapHostUserCredentials>')

    os.close(fd)
    return path


def set_wlan_profile(ssid, auth_method, encrypt_method, key_type = "", key_material = "",
                   key_index = "", use_onex = False, username = "", password = "", adapter_name = ""):
    """
    Create and add the profile to a wireless adapter with provided security settings
    Input:
    @param ssid: a string represents the SSID
    @param auth_method: one of the authentication methods including "open", "shared", "WPA", "WPAPSK",
                  "WPA2", and "WPA2PSK"
    @param encrypt_method: one of the encryption methods including "none", "WEP", "TKIP" and "AES"
    @param key_type: one of the key types including "passPhrase" or "networkKey"
    @param key_index: WEP key index, can be 1, 2, 3 or 4
    @param key_material: the key string
    @param use_onex: True if the profile includes 802.1x authentication configuration, otherwise use False
    @param username: user credential
    @param password:
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)
    
    # Create the XML profile file with provided security setting
    profile_path = _make_wlan_profile_xml(ssid, auth_method, encrypt_method, key_type, key_material, key_index, use_onex)

    # Scan for wireless networks
    _exec_program("%s scan %s" % (_wlantool_cmd, _adapter_guid))
    time.sleep(1)

    # Set the wireless profile
    cmd_line = "%s sp %s \"%s\"" % (_wlantool_cmd, _adapter_guid, profile_path)
    _dispmsg("[EXEC SetWirelessProfile]: %s" % (cmd_line))
    output = os.popen(cmd_line)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("successfully") == -1:
        raise Exception("Unable to set the security setting to the wireless adapter")
    
    #@author: Jane.Guo @since: 2013-10 fix bug ZF-5823 if restart adapter, tshark will be closed
    #if _adapter_vid:
    #    # Restart the wireless adapter
    #    _exec_program("%s restart %s" % (_devcon_cmd, _adapter_vid))
    #    time.sleep(5)
    # Connect to the wireless network specified by the profile
    time.sleep(0.1)
    _exec_program("%s scan %s" % (_wlantool_cmd, _adapter_guid))
    time.sleep(0.2)
    _exec_program('%s conn %s "%s" i "%s"' % (_wlantool_cmd, _adapter_guid, ssid, ssid))

    # Set the user credential when .1x is used
    if use_onex:
        # Create the EAP user credential file
        user_credential_path = _make_user_credential_xml(username, password)

        # And pass to the wireless adapter
        cmd_line = '%s seuc %s "%s" "%s"' % (_wlantool_cmd, _adapter_guid, ssid, user_credential_path)
        _dispmsg("[EXEC Add pass to wireless adapter]: %s" % cmd_line)
        output = os.popen(cmd_line)
        buffer = "".join(line for line in output)
        output.close()
        if buffer.find("successfully") == -1:
            raise Exception("Unable to set the EAP user credential to the adapter \"%s\"" % adapter_name)

        if _adapter_vid:
            # Restart the wireless adapter
            _exec_program("%s restart %s" % (_devcon_cmd, _adapter_vid))
            time.sleep(5)
        # Force to connect to the wireless network specified by the profile
        time.sleep(0.2)
        _exec_program('%s conn %s "%s" i "%s"' % (_wlantool_cmd, _adapter_guid, ssid, ssid))


def remove_all_wlan(adapter_name = ""):
    """
    Remove all the existing wireless profiles on a wireless adapter (if specified)
    or the first available one
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)
    
    _exec_program('%s dc %s' % (_wlantool_cmd, _adapter_guid))
    time.sleep(2)

    # Get the list of the profiles created on the adapter
    pattern = '[\t ]+"([a-zA-Z0-9_\- ]+)"'
    profile_list = []
    cmd_line = "%s gpl %s" % (_wlantool_cmd, _adapter_guid)
    _dispmsg("[EXEC Get Profiles on adapter]: %s" % cmd_line)
    output = os.popen(cmd_line)
    done = False
    for line in output:
        match_obj = re.match(pattern, line)
        if match_obj:
            profile_list.append(match_obj.group(1))
        elif line.find("completed"):
            done = True
    if not done:
        raise Exception("Unable to get list of profiles")
    output.close()

    # And remove them all
    for profile in profile_list:
        cmd_line = "%s dp %s \"%s\"" % (_wlantool_cmd, _adapter_guid, profile)
        _dispmsg("[EXEC DEL Profiles]: %s" % cmd_line)
        output = os.popen(cmd_line)
        buffer = "".join(line for line in output)
        output.close()
        if buffer.find("successfully") == -1:
            raise Exception("Unable to remove the profile %s" % profile)

def do_release_wifi_ip_address(adapter_name = ""):
    """
    Release IP address of the wireless adapter after associating to the network
    This function is useful in Vista stations where IP address is cached from previous associations
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_name

    _update_guid(adapter_name)

    time.sleep(2)
    if _adapter_name:
        release_cmd = "ipconfig /release \"%s\"" % _adapter_name
    else:
        release_cmd = "ipconfig /release"

    time.sleep(1)
    os.system(release_cmd)
    
def do_renew_wifi_ip_address(adapter_name = ""):
    """
    Renew IP address of the wireless adapter after releasing
    This function is useful in Vista stations where IP address is cached from previous associations
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_name

    _update_guid(adapter_name)

    time.sleep(2)
    if _adapter_name:
        renew_cmd = "ipconfig /renew \"%s\"" % _adapter_name
    else:
        renew_cmd = "ipconfig /renew"

    time.sleep(1)
    os.system(renew_cmd)

def renew_wifi_ip_address(adapter_name = ""):
    """
    Release and renew IP address of the wireless adapter after associating to the network
    This function is useful in Vista stations where IP address is cached from previous associations
    @param adapter_name: Friendly name of the wireless adapter
    """
    global _adapter_name

    _update_guid(adapter_name)

    time.sleep(2)
    if _adapter_name:
        release_cmd = "ipconfig /release \"%s\"" % _adapter_name
        renew_cmd = "ipconfig /renew \"%s\"" % _adapter_name
    else:
        release_cmd = "ipconfig /release"
        renew_cmd = "ipconfig /renew"

    time.sleep(1)
    os.system(release_cmd)
    time.sleep(1)
    os.system(renew_cmd)

def set_eth_mtu(mtu, iptype, eth_inf):
    cmd_line = 'netsh interface %s set subinterface \"%s\" mtu=%s store=persistent' %(iptype, eth_inf, mtu)
    _dispmsg("[EXEC set_eth_mtu]: %s" % cmd_line)
    res_file = os.popen(cmd_line)
    res = (res_file.read()).split('\n')
    res_file.close()
    if 'ok' not in res[0].lower():
        msg = 'Set MTU of \'%s\' to \'%s\' failed' %(eth_inf, mtu)
        raise Exception(msg)
        
def get_current_status(adapter_name = ""):
    """
    Obtain current connectivity status of the first wireless adapter on the system
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: the output of the command "wlanman.exe qi"
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    pattern = 'Interface state: "([a-z ]+)"'
    output = os.popen("%s qi %s" % (_wlantool_cmd, _adapter_guid))
    buffer = "".join(line for line in output)
    output.close()
    match_obj = re.search(pattern, buffer)
    if match_obj:
        return match_obj.group(1)
    raise Exception("Unable to get current status")

def get_addresses(adapter_name = ""):
    """
    Return MAC and IP address (if existed) of the specified wireless adapter (or the
    first one listed if not specified)
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a tupple of MAC and IP addresses
    """
    global _adapter_desc

    _update_guid(adapter_name)

    output = os.popen("ipconfig /all")
    found_desc = False
    ip_addr = ""
    mac_addr = ""
    for line in output:
        line = line.strip()
        if not line:
            if found_desc and (ip_addr or mac_addr): break
            continue
        x = line.split(':')
        if len(x) < 2: continue
        tag = x[0].rstrip('. ')
        val = x[1].lstrip(' ')
        if tag == "Description" and val in _adapter_desc:
            found_desc = True
        elif found_desc:
            if tag == "IP Address" or tag == "IPv4 Address":
                #@author: Jane.Guo @since: 2013-6-5 adapt ipv6 address, return correct ipv4 address
                if re.search('\.',val):
                    ip_addr = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                mac_addr = ":".join(val.split("-"))
    output.close()
    return (ip_addr, mac_addr)


def get_8021x_address():
    """
    Return MAC and IP address (if existed) of the specified wireless adapter (or the
    first one listed if not specified)
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a tupple of MAC and IP addresses
    """
    global _adapter_desc
    output = os.popen("ipconfig /all")
    found_desc = False
    ip_addr = ""
    mac_addr = ""
    for line in output:
        line = line.strip()
        if not line:
            if found_desc and (ip_addr or mac_addr): break
            continue
        x = line.split(':')
        if len(x) < 2: continue
        tag = x[0].rstrip('. ')
        val = x[1].lstrip(' ')
        if tag == "Description" and val in _adapter_desc:
            found_desc = True
        elif found_desc:
            if tag == "IP Address" or tag == "IPv4 Address":
                ip_addr = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                mac_addr = ":".join(val.split("-"))
    output.close()
    return (ip_addr, mac_addr)


def get_addresses_ipv6(adapter_name = ""):
    """    
    Return MAC and IPV4 and IPV6 address (if existed) of the specified wireless adapter (or the
    first one listed if not specified), if there is multiple for ipv6, return the first one.
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a tupple of MAC and IP addresses
    """
    global _adapter_desc

    _update_guid(adapter_name)

    output = os.popen("ipconfig /all")
    found_desc = False
    ip_addr = ""
    ipv6_addr_list = []
    mac_addr = ""
    for line in output:
        line = line.strip()
        if not line:
            if found_desc and (ip_addr or mac_addr): break
            continue
        x = line.split(':')
        if len(x) < 2: continue
        tag = x[0].rstrip('. ')
        val = x[1].lstrip(' ')
        if tag == "Description" and val in _adapter_desc:
            found_desc = True
        elif found_desc:
            if tag == "IP Address" or tag == "IPv4 Address" \
               or tag == "IPv6 Address" or tag == 'Temporary IPv6 Address':                
                if val.find('.')>-1:
                    if not ip_addr:         
                        ip_addr = val.split("(Preferred)")[0]                        
                else:
                    ip_str = ":".join(x[1:]).strip()
                    ip_str = ip_str.split("(")[0]#Chico, 2015-6-2, handle prefereed and deprecated ipv6 address
                    if not 'fe80' in ip_str.lower():
                        ipv6_addr_list.append(ip_str)                          
            elif tag == "Physical Address":
                mac_addr = ":".join(val.split("-"))
    output.close()
    
    return (ip_addr, ipv6_addr_list, mac_addr)

def get_ip_cfg(adapter_name = ""):
    """
    Return a dictionary with all the information of the current adapter or the given adapter_name
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a dictionary with the keys are parsed from the output of the command IPCONFIG /all
    """
    global _adapter_name

    _update_guid(adapter_name)

    output = os.popen("ipconfig /all")
    found_name = False
    ip_info = {}
    for line in output:
        line = line.strip()
        if not line:
            if found_name and ip_info: break
            continue
        if line.find(_adapter_name) != -1:
            found_name = True
        elif found_name:
            if ' :' not in line:
                continue
            x = line.split(' :')
            tag = x[0].rstrip('. ')
            val = x[1].lstrip(' ')
            if tag == "IP Address" or tag == "IPv4 Address":
                ip_info['ip_addr'] = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                ip_info['mac_addr'] = ":".join(val.split("-"))
            elif tag == "Subnet Mask":
                ip_info['subnet_mask'] = val
            elif tag == "Lease Obtained":
                ip_info['lease_obtained'] = val
            elif tag == "Lease Expires":
                ip_info['lease_expires'] = val
            elif tag == "DHCP Server":
                ip_info['dhcp_server'] = val
            #@author: Jane.Guo Add for get gateway info and dhcp info
            elif tag == "Default Gateway":
                ip_info['gateway'] = val
            #@author: Jane.Guo @since: 2013-06-13 Add to adapt different output format
            #Win7: DHCP Enabled. . . . . . . . . . . : Yes
            #WinXP: Dhcp Enabled. . . . . . . . . . . : Yes
            elif tag.lower() == "dhcp enabled":
                ip_info['dhcp_enabled'] = val

    output.close()
    return ip_info


def check_ssid(ssid, adapter_name = ""):
    """
    Check if SSID is broadcasted on the air
    @param ssid: SSID of the WLAN needs to be verified
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: the SSID itself it is found, otherwise return ""
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    if _adapter_desc.find('Atheros AR9485') != -1:
        restart_adapter()
    time.sleep(10)
    cmd_line = "%s gvl %s" % (_wlantool_cmd, _adapter_guid)
    _dispmsg("[EXEC check_ssid]: %s" % cmd_line)
    output = os.popen(cmd_line)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("successfully") == -1:
        raise Exception("Unable to get list of visible WLANs")
    pattern = "SSID: (%s)[\\r\\n]" % ssid
    match_obj = re.search(pattern, buffer)
    if match_obj:
        return match_obj.group(1)
    return ""

def ping(target_ip, timeout_ms = 1000, echo_count = 2, echo_timeout = 10, pause = 0.05):
    cmd_line1 = "ping %s -n %s -w %s" % (target_ip, str(echo_count), str(echo_timeout))
    cmd_line2 = "ping -6 %s -n %s -w %s" % (target_ip, str(echo_count), str(echo_timeout))
    ofmt= r"Packets:\s*sent\s*=\s*(\d+),\s*received\s*=\s*(\d+),\s+lost\s*=\s*(\d+)\s*\((\d+)%\s*loss\)"
    good_reply_list = [r"reply\s+from\s+[0-9.]+:\s*bytes=\d+.*TTL=\d+", 
                       r"reply\s+from\s+[0-9a-f:]+:\s*time[=,<]\d+ms"]
    
    timeout_s = timeout_ms / 1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        data = _exec_program(cmd_line1)
        current_time = time.time()
        m = re.search(ofmt, data, re.M | re.I)
        if m and int(m.group(4)) == 0:
            #Cherry updated: add good reply ptn for ipv6 address.
            # bug in win32 ping program.
            # if gateway exist in target_ip; the loss rate is ZERO %
            for ptn in good_reply_list:
                if re.search(ptn, data, re.I):                    
                    return "%.1f" % (current_time - start_time)
        else:
            data = _exec_program(cmd_line2)
            current_time = time.time()
            m = re.search(ofmt, data, re.M | re.I)
            if m and int(m.group(4)) == 0:
                for ptn in good_reply_list:
                    if re.search(ptn, data, re.I):                    
                        return "%.1f" % (current_time - start_time) 
        time.sleep(int(pause))
    return "Timeout exceeded (%.1f seconds)" % timeout_s

def ping2(target_ip, timeout_ms = 1000, echo_count = 4, echo_timeout = 1000, pause = 0.05, size =32, disfragment=False, allow_loss = False):
    if disfragment:
        cmd_line = "ping %s -n %s -w %s -l %s -f" % (target_ip, echo_count, echo_timeout, size)
    else:
        cmd_line = "ping %s -n %s -w %s -l %s" % (target_ip, echo_count, echo_timeout, size)
    ofmt = r"Packets:\s*sent\s*=\s*(\d+),\s*received\s*=\s*(\d+),\s+lost\s*=\s*(\d+)\s*\((\d+)%\s*loss\)"
    good_reply_list = [r"reply\s+from\s+[0-9.]+:\s*bytes=\d+.*TTL=\d+", 
                       r"reply\s+from\s+[0-9a-f:]+:\s*time[=,<]\d+ms"]
    
    timeout_s = timeout_ms / 1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        data = _exec_program(cmd_line)
        current_time = time.time()
        m = re.search(ofmt, data, re.M | re.I)
        if m:
            if (allow_loss and (int(m.group(4))) < 100) or int(m.group(4)) == 0:
                #Cherry updated: add good reply ptn for ipv6 address.
                # bug in win32 ping program.
                # if gateway exist in target_ip; the loss rate is ZERO %
                for ptn in good_reply_list:
                    if re.search(ptn, data, re.I):                    
                        return "%.1f" % (current_time - start_time)
        time.sleep(int(pause))
    return "Timeout exceeded (%.1f seconds)" % timeout_s

def clean_arp():
    """
    Clean all arp info recorded on station.
    """
    cmd_line = "arp -d"
    _dispmsg("[EXEC clean_arp]: %s" % cmd_line)
    res = os.system(cmd_line)
    if res:
        msg = 'Clean arp info on station failed'
        raise Exception(msg)

def perform_web_auth(arg):
    """
    Call the zd_web_auth function in HttpClient module to perform the Web
    authentication process
    """
    _dispmsg("[EXEC perform_web_auth]: HttpClient.py zd_web_auth \"%(arg)s\"" % locals())
    output = os.popen("HttpClient.py zd_web_auth \"%(arg)s\"" % locals())
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Unable to do Web authentication: %s" % buffer)


def perform_guest_auth(arg):
    """
    Call the guest_auth function in HttpClient module to perform the Guest Pass
    authentication process
    @param guest_pass: a string or null if guest authentication is not used
    @param use_tou: a boolean value to enable/disable Term Of Use
    @param redirect_url: a string or null if URL redirection is not used
    """
    output = os.popen("HttpClient.py guest_auth \"%(arg)s\"" % locals())
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Unable to do Guest authentication: %s" % buffer)


def perform_hotspot_auth(arg):
    """
    Call the wispr_auth function in HttpClient module to perform the Hotspot
    authentication
    @param username: authentication credential
    @param password: authentication credential
    @param redirect_url: the URL configured on the Hotspot
    @param original_url: the URL that is used to trigger the authentication process
    """
    _dispmsg("[EXEC perform_hotspot_auth]: HttpClient.py wispr_auth \"%(arg)s\"" % locals())
    output = os.popen("HttpClient.py wispr_auth \"%(arg)s\"" % locals())
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Unable to do Hotspot authentication: %s" % buffer)


def perform_hotspot_deauth(**kwargs):
    """
    Call the wispr_deauth function in HttpClient module to perform the Hotspot logout process
    @param logout_url: the URL that is used to trigger the logout process
    """
    params = {'logout_url': ''}
    params.update(kwargs)
    output = os.popen("HttpClient.py wispr_deauth \"%s\"" % str(params))
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Unable to do Hotspot logout: %s" % buffer)

def collect_data(toolname, result_file):
    """
    collect_data is a function called after the traffic is run.
    This function reads the traffic result file and collects the statistics
    of the run.
    @param toolname: name of the traffic generator; only "zap" is supported
    @param result_file: name of the CVS file
    @return: a dictionary of the traffic performance results
    """
    # pull the results out of the test log file
    rf = open(result_file, "r")
    tags = rf.readline().split(',')
    res = rf.readlines()
    retvals = dict()
    try:
        thisres = res[-1].split(',')
    except:
        raise Exception("A problem occurred with parsing the data in test result file")

    rf.close()

    if toolname == "zap":
        lost_pkts_str = "Payloads Dropped"
    else:
        lost_pkts_str = "Packets Lost"

    # Make dictionary of test tags and corresponding test results
    try:
        for i in range(len(tags)):
            if tags[i].endswith('%'):
                # convert percentiles and throughput results to float
                tags[i] = tags[i].rstrip('%')
                retvals["%.1f" % float(tags[i])] = float(thisres[i])
            elif tags[i] == lost_pkts_str:
                # convert lost packets to int
                retvals[tags[i]] = int(thisres[i])
            else:
                # everything else stays as text
                retvals[tags[i]] = thisres[i]
    except:
        raise Exception("A problem occurred when converting the data from the result file")

    return retvals


def send_zap(sip, dip, invert_conn = False, payload_len = "", full_len_frms = "", test_tcp = False, sample_sz = "",
            period = "", qos = "", sample_num = "", outstd_sample = "", mdip = "", rate = "", time_run = ""):
    """
    Execute zap to transmit traffic with given configuration
    @param sip: source IP address
    @param dip: destination IP address
    @param invert_conn: a boolean value indicates Invert Connection Openning is used or not
    @param payload_len: an integer specifies a payload length
    @param full_len_frms: an integer specifies how many full-length frames is used for framelength
    @param test_tcp: a boolean value specifies TCP should be used instead of UDP
    @param sample_sz: an integer specifies the number of payloads sampled for performance measurement
    @param period: an integer specifies the period each sample lasts
    @param qos: 8bit DSCP (TOS bits) set in the frames
    @param sample_num: an integer specifies the number of samples in the test
    @param outstd_sample: an integer specifies the number of samples that may be outstanding
    @param mdip: specifies the destination multicast address to use for data communication
    @param rate: controls the rate in mbits/s for transmitting data
    @param time_run: runs the test for specified number of seconds

    @return: the dictionary returned by the function collect_data()
    """
    cmd = [_zap_cmd, "-s%s" % sip, "-d%s" % dip]
    if invert_conn: cmd.append("-i")
    if payload_len: cmd.append("-l%s" % payload_len)
    if full_len_frms: cmd.append("-f%s" % full_len_frms)
    if test_tcp: cmd.append("-t")
    if sample_sz: cmd.append("-a%s" % sample_sz)
    if period: cmd.append("-p%s" % period)
    else: cmd.append("-p50000")
    if qos: cmd.append("-q%s" % qos)
    if sample_num: cmd.append("-n%s" % sample_num)
    if mdip: cmd.append("-m%s" % mdip)
    if rate: cmd.append("-r%s" % rate)
    if time_run: cmd.append("-X%s" % time_run)
    cmd.append("-F%s" % _zap_cvs_file)

    # Make sure the result file is removed before running traffic
    try:
        os.remove(_zap_cvs_file)
    except:
        pass

    # Execute the command
    subprocess.call(cmd)

    # Verify that the test result file was created
    if not os.path.isfile(_zap_cvs_file):
        raise Exception("Test result file was not created")
    if not os.path.getsize(_zap_cvs_file):
        raise Exception("Test result file was not created properly (size zero)")

    return collect_data("zap", _zap_cvs_file)

def send_zing(host, delay = '', len_of_pkt = '', num_of_pkts = '', tos = '', udp = False, port = '', sending_time = ''):
    """
    """
    cmd = [_zing_cmd, '--client', '%s' % host]
    if delay: cmd.append('-d%d' % int(delay))
    if len_of_pkt: cmd.append('-l%d' % int(len_of_pkt))
    if num_of_pkts:
        cmd.append('-e%d' % int(num_of_pkts))
        cmd.append('-E1')
    if tos: cmd.append('-q%s' % tos)
    if udp or port: cmd.append('-u%s' % port)
    if sending_time: cmd.append('-S%s' % sending_time)
    cmd.append('-f%s' % _zing_cvs_file)

    # Make sure the result file is removed before running traffic
    try:
        os.remove(_zing_cvs_file)
    except:
        pass

    # Execute the command
    subprocess.call(cmd)

    # Verify that the test result file was created
    if not os.path.isfile(_zing_cvs_file):
        raise Exception("Test result file was not created")
    if not os.path.getsize(_zing_cvs_file):
        raise Exception("Test result file was not created properly (size zero)")

    return collect_data("zing", _zing_cvs_file)

def add_ip_if(if_name, addr, mask):
    """
    Add a new IP interface to the Ethernet NIC
    @if_name: Name of the interface (e.g: "Local Area Connection")
    @param addr: IP address
    @param mask: subnet mask
    """
    cmd = "netsh interface ip add address \"%s\" %s %s" % (if_name, addr, mask)
    _dispmsg("[EXEC addIpIf]: %s" % cmd)
    buf = [line.strip("\r").strip("\n") for line in os.popen(cmd)]
    ok = False
    for line in buf:
        if line == "Ok.":
            ok = True
            break
    if not ok and get_win_version() == "51":
        raise Exception("".join(buf))
    time.sleep(5)

def set_ip_if(source, addr="", mask="", gateway="", if_name=""):
    """
    Set IP interface to the Ethernet NIC
    @author: Jane.Guo
    @since: 2013-5-8
    
    @param source: The protocol of IP address, like Static, DHCP etc.
    @param addr: IP address
    @param mask: subnet mask
    @param gateway: Gateway
    @if_name: Name of the interface. (e.g: "Local Area Connection")
    netsh interface ip set address name="Wireless Network Connection 3" source="static" addr="192.168.0.112" mask="255.255.255.0" gateway="192.168.0.253"
    netsh interface ip set address name="Wireless Network Connection 3" source="dhcp"
    netsh interface ip set address "Wireless Network Connection 3" static 192.168.0.112 255.255.255.0 192.168.0.253
    netsh interface ip set address "Wireless Network Connection 3" dhcp
    """
    if if_name == "":
        global _adapter_name
        if_name = _adapter_name
    
    #@author: Jane.Guo @since: 2013-6-13 adapt to windows7 and windows xp, xp need gwmetric
    os_name = get_os_platform()
    if re.match('Windows,7',os_name):
        cmd = "netsh interface ip set address \"%s\" %s %s %s %s" % (if_name, source, addr, mask, gateway)
    elif re.match('Windows,XP',os_name):
        gwmetric = ""
        if source.lower() == "static":
            gwmetric = 1
        cmd = "netsh interface ip set address \"%s\" %s %s %s %s %s" % (if_name, source, addr, mask, gateway, gwmetric)
    
    _dispmsg("[EXEC setIpIf]: %s" % cmd)
    buf = [line.strip("\r").strip("\n") for line in os.popen(cmd)]
    ok = False
    for line in buf:
        if line == "Ok.":
            ok = True
            break
    if not ok and get_win_version() == "51":
        raise Exception("".join(buf))
    time.sleep(5)
    
def _remove_ip_if(if_name, addr):
    """
    Remove an IP interface from the Ethernet NIC
    @if_name: Name of the interface (e.g: "Local Area Connection")
    @param addr: IP address
    """
    cmd = "netsh interface ip del address \"%s\" %s" % (if_name, addr)
    _dispmsg("[EXEC removeIpIf]: %s" % cmd)
    buf = [line.strip("\r").strip("\n") for line in os.popen(cmd)]
    ok = False
    for line in buf:
        if line == "Ok.":
            ok = True
            break
    if not ok and get_win_version() == "51":
        raise Exception("".join(buf))
    time.sleep(5)

# this function is use for ap - temporary put it here.
# we will merge with version from ZD and FM later
def get_if_info():
    """
    Get information about the interface configured with static ip address
    @return: a dictionation in format
        {'name of the interface' : [{'addr':'IP address', 'mask':'Subnet mask'}, ...]}
        or None if not found
    """
    cmd = "netsh interface ip show address"
    buf = [line.strip("\r").strip("\n").strip() for line in os.popen(cmd)]
    buf = [line for line in buf if line]
    temp = {}
    ip_info = []
    if_name = ""
    res = {}
    for line in buf:
        if line.startswith("Configuration for interface"):
            if_name = line.split('"')[1]
            temp = {}
            ip_info = []
            continue
        if line.startswith("IP Address"):
            temp['addr'] = line.split(':')[1].strip()
        elif line.startswith("Subnet"):
            temp['mask'] = line.split(':')[1].strip().split(')')[0]
        if len(temp) == 2:
            ip_info.append(temp)
            temp = {}
        if ip_info:
            res['%s' % if_name] = ip_info

    return res

def _get_if_info(addr):
    """
    Get information about the interface with given IP address
    @param addr: IP address of the interface
    @return: a dictionation in format
        {'if_name': 'name of the interface',
         'ip_info': [{'addr':'IP address',
                     'mask':'Subnet mask'}, ...]}
        or None if not found
    """
    cmd = "netsh interface ip show address"
    _dispmsg("[EXEC get_ipInfo]: %s" % cmd)
    buf = [line.strip("\r").strip("\n").strip() for line in os.popen(cmd)]
    buf.append("")
    temp = {}
    ip_info = []
    found = False
    for line in buf:
        if not line:
            if found: return dict(if_name = if_name, ip_info = ip_info)
            else: continue
        l = line.split('"')
        if l[0] == "Configuration for interface ":
            if_name = l[1]
            ip_info = []
            temp = {}
            continue
        l = line.split(':')
        if l[0] == "IP Address":
            temp['addr'] = l[1].strip()
            if temp['addr'] == addr:
                found = True
        elif l[0].startswith("Subnet"):
            # The code below extracts subnet mask value from the output
            # on Vista:
            # Subnet Prefix:                        192.168.0.0/24 (mask 255.255.255.0)
            # or in XP:
            # SubnetMask:                           255.255.255.0
            temp['mask'] = l[1].split()[-1].split(")")[0]
            ip_info.append(temp)
            temp = {}
    return None

def verify_if(addr):
    """
    Ensure that there is only the given IP address is configured on the interface
    Remove other addresses
    @param addr: IP address of the interface needs to be verified
    """
    if_info = _get_if_info(addr)
    if not if_info:
        raise Exception("No interface with IP address %s exists" % addr)
    if len(if_info['ip_info']) > 1:
        for inf in if_info['ip_info']:
            if inf['addr'] != addr:
                _remove_ip_if(if_info['if_name'], inf['addr'])

def login_ap_web_ui(username, password, ip_addr):
    """
    Call the login_ap function in HttpClient module to perform login to AP WebUI
    @param username: username to login
    @param password: password to login
    @param ip_addr: ip address of AP
    """
    params = "{'username':'%s', 'password':'%s', 'ip_addr':'%s'}" % (username, password, ip_addr)
    output = os.popen("HttpClient.py login_ap \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def logout_ap_web_ui(ip_addr):
    """
    Call the logout_ap in HttpClient module to perform logout from the AP WebUI
    """
    param = "{'ip_addr':'%s'}" % ip_addr
    output = os.popen("HttpClient.py logout_ap \"%s\"" % param)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def login_ap_cli_send(text,username='super',password='sp-admin',port=22,ip_addr='169.254.1.1'):
    """
    """
    t = paramiko.Transport((ip_addr,port))  
    t.connect(username="",password="")
    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    _wait_for(chan, 'login')
    chan.send(username + "\n")
    _wait_for(chan, 'password')
    chan.send(password + "\n")
    _wait_for(chan, 'rkscli:')
    chan.send(text + "\n")
    time.sleep(1)
    for x in range(3):
        if chan.recv_ready():
            return_value = chan.recv(2048)
            chan.close()
            t.close()
            del chan,t
            return return_value
        time.sleep(0.02)
    raise Exception("SSH Send Failed")
    
    
def _wait_for(chan, text, recv_bufsize=1024, retry=200, pause=0.02):
    '''
    quick and dirty excpect substitute for paramiko channel;
    Raise exception if text not found.
    ssh=dict(pause=0.02, retry=200, recv_bufsize=1024, port=22),
    '''
    for x in range(retry):
        if chan.recv_ready():
            if text in chan.recv(recv_bufsize):
                return # success
        time.sleep(pause) # 100*.02 = approx 2 seconds total
    raise Exception("SSH expect")

def get_ap_wireless_status(ip_addr):
    """
    Call the get_ap_wireless_status function in HttpClient module to get wireless status from AP WebUI
    """
    param = "{'ip_addr':'%s'}" % ip_addr
    output = os.popen("HttpClient.py get_ap_wireless_status \"%s\"" % param)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)
    info = buffer.strip("\r").strip("\n").strip()
    return info

def verify_station_mgmt(ap_ip_addr, aid, sta_mac_addr):
    """
    Call the verify_station_mgmt function in HttpClient module to verify information of STA-Management on the AP WebUI
    """
    params = "{'ap_ip_addr':'%s', 'aid':%s, 'sta_mac_addr':'%s'}" % (ap_ip_addr, aid, sta_mac_addr)
    output = os.popen("HttpClient.py verify_station_mgmt \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)
    info = buffer.strip('\r').strip('\n').strip()
    return info

def login_ad_web_ui(ap_ip_addr, aid):
    """
    Call the login_ad function in HttpClient module to login to Adapter WebUI
    """
    params = "{'ap_ip_addr':'%s', 'aid':%s}" % (ap_ip_addr, aid)
    output = os.popen("HttpClient.py login_ad \"%s\"" % params)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("ERROR") != -1:
        raise Exception("Error message: %s" % buffer)

def get_ad_encryption(config, wlan_if):
    """
    Get wlan configuration information on the adapter on the specific interface
    Return a dictionary of wlan information
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_encryption(wlan_if)
    time.sleep(1)
    return res

def config_wlan(config, wlan_cfg):
    """
    Create a wlan on the adapter
    @param wlan_cfg: a dictionary of wlan parameters
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.cfg_wlan(wlan_cfg)
    time.sleep(2)

def set_ruckus_ad_state(config, state, wlan_if):
    """
    Telnet to the Ruckus Adapter and set status for svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.set_state(wlan_if, state)
    time.sleep(2)

def get_ruckus_ad_state(config, wlan_if):
    """
    Telnet to the Ruckus Adapter and get status of svcp
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_state(wlan_if)
    time.sleep(1)
    return res

def get_ad_wireless_mac(config):
    """
    Telnet to the Adapter and get mac address of wlan0
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_wireless_mac()
    time.sleep(1)
    return res

def set_ad_ssid_web_ui(config, ssid, is_vf7111):
    """
    Login to Adapter WebUI and change SSID value
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_ssid_web_ui(ssid, is_vf7111)
    time.sleep(3)

def set_ad_encryption_web_ui(config, encryption_cfg, is_vf7111):
    """
    Login to Adapter WebUI and set encryption method for adapter
    Please refer to the set_encryption_web_ui on RuckusAD for detail of parameters
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_encryption_web_ui(encryption_cfg, is_vf7111)
    time.sleep(3)

def get_ad_device_status_web_ui(config):
    """
    Get status of adapter from WebUI
    @return a dictionary of device information
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_device_status_web_ui()
    time.sleep(2)
    return res

def set_ad_system_name_web_ui(config, system_name):
    """
    Set system name for adapter from its WebUI
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_system_name_web_ui(system_name)
    time.sleep(2)

def set_ad_home_protection_web_ui(config, enable):
    """
    Set Home Protection status for adapter from its WebUI
    """
    ad_obj = RuckusAD(config)
    ad_obj.set_home_protection(enable)
    time.sleep(2)

def set_ad_ssid(config, wlan_if, ssid):
    """
    Set SSID value for the specific interface on the adapter
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.set_ssid(wlan_if, ssid)
    time.sleep(2)

def get_ad_home_login_info(config):
    """
    Get Home login information from WebUI
    """
    ad_obj = RuckusAD(config)
    res = ad_obj.get_home_login_info()
    time.sleep(2)
    return res

	
def download_zero_it_via_web_portal(url, data):
    """
    Download ZeroIT tool via Northbound Interface and return the path.
    @param url: web portal interface. -- https://192.168.0.2/admin/_portalintf.jsp
    @data: XML request format. -- <ruckus>
                                    <req-password>123456</req-password>
                                    <version>1.0</version>
                                    <command cmd="get-prov-file" 
                                            ipaddr="" 
                                            macaddr="00:00:00:00:00:00" 
                                            username="" 
                                            user-agent="Mozilla/4.0">
                                        <wlansvc name="anbchris" expiration="4380" key-length="8" vlan-id=""/>
                                    </command>
                                  </ruckus>
    """
    TOOLPATH = "prov.exe"
    if os.path.exists(TOOLPATH):
        os.remove(TOOLPATH)
    import urllib
    req = urllib.urlopen(url, data)
    f = open(TOOLPATH, "wb")
    f.write(req.read())
    f.close()
    
    return TOOLPATH


def execute_zero_it(tool_path, ssid, auth_method, use_radius, adapter_name = ""):
    '''
    '''
    timeout = 2

    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    # Scan for wireless networks
    _exec_program("%s scan %s" % (_wlantool_cmd, _adapter_guid))
    time.sleep(timeout)

    # Remove all personal certificates on the station
    pattern = 'CertMgr Succeeded'
    _dispmsg("[EXEC remove cert]: %s" % _certmgr_cmd)
    output = os.popen("%s" % _certmgr_cmd)
    buffer = "".join(line for line in output)
    output.close()
    match_obj = re.search(pattern, buffer)
    if not match_obj:
        raise Exception("Unable to remove all personal certificates on the station")

    # Kill ZeroIT process
    _kill_zero_it_process()
    time.sleep(timeout)

    zero_it_by_os = {
        '51': execute_zero_it_xp,
        '60': execute_zero_it_old, #for Vista. Haven't tested
        '61': execute_zero_it_win7,
    }

    zero_it_by_os[get_win_version()](tool_path, ssid, auth_method, use_radius)

    # Force to connect to the wireless network specified by the profile
    time.sleep(timeout)
    if ssid:
        os.popen('"%s conn %s "%s" i "%s"' % (_wlantool_cmd, _adapter_guid, ssid, ssid))


def execute_zero_it_xp(tool_path, ssid, auth_method, use_radius, adapter_name = ""):
    '''
    '''
    print 'Execute ZeroIT on Windows XP client'
    handler2 = DialogHandler2()
    handler2.app.start_(tool_path)

    handler2.install_cert()
    handler2.select_cert_xp()


def execute_zero_it_win7(tool_path, ssid, auth_method, use_radius, adapter_name = ""):
    '''
    '''
    print 'Execute ZeroIT on Windows 7 client'
    handler2 = DialogHandler2()
    handler2.app.start_(tool_path)

    handler2.install_cert()
    handler2.select_cert_win7()


def execute_zero_it_old(tool_path, ssid, auth_method, use_radius, adapter_name = ""):
    """
    Execute the ZeroIT tool stored at the given path
    @param tool_path: Full path to the tool
    @param ssid: SSID of the WLAN
    @param auth_method: Authentication method
    @param use_radius: a boolean value indicates radius is used or not
    """
    timeout = 2

    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    # Scan for wireless networks
    _exec_program("%s scan %s" % (_wlantool_cmd, _adapter_guid))
    time.sleep(timeout)

    # Remove all personal certificates on the station
    pattern = 'CertMgr Succeeded'
    _dispmsg("[EXEC remove cert]: %s" % _certmgr_cmd)
    output = os.popen("%s" % _certmgr_cmd)
    buffer = "".join(line for line in output)
    output.close()
    match_obj = re.search(pattern, buffer)
    if not match_obj:
        raise Exception("Unable to remove all personal certificates on the station")

    # Kill ZeroIT process
    _kill_zero_it_process()
    time.sleep(timeout)

    # Close "Set Network Location" dialog
    zero_it_dlg_handler = {}
    zero_it_dlg_handler['title_dialog_list'] = ["Set Network Location"]
    zero_it_dlg_handler['class_name_dialog_list'] = []
    zero_it_dlg_handler['button_list'] = ["Cancel"]
    zero_it_dlg_handler['static_text_list'] = ["Windows will automatically apply the correct network settings for the location"]
    _dialog_handler(**zero_it_dlg_handler)
    time.sleep(3 * timeout)

    # Execute file prov.exe to install wlan profile on the station
    application.Application().Start_(tool_path)

    if auth_method != "EAP":
        zero_it_dlg_handler['title_dialog_list'] = ""
        zero_it_dlg_handler['class_name_dialog_list'] = ["#32770"]
        zero_it_dlg_handler['button_list'] = ["Close"]
        zero_it_dlg_handler['static_text_list'] = ["Configuration completed. Click 'Close' to finish"]
        _dialog_handler(**zero_it_dlg_handler)
        time.sleep(3 * timeout)

    else:
        # If using 802.1x with Local Database
        if not use_radius:
            # Handle dialog "Security Warning"
            zero_it_dlg_handler['title_dialog_list'] = ["Security Warning"]
            zero_it_dlg_handler['static_text_list'] = ["Do you want to install this certificate?"]
            zero_it_dlg_handler['button_list'] = ["&Yes"]
            zero_it_dlg_handler['class_name_dialog_list'] = []
            _dialog_handler(**zero_it_dlg_handler)
            time.sleep(6 * timeout)

            # Handle a dialog with specific title and text
            #(title, static text, button)
            cert_mgr = \
                ("Info", "Your personal certificate has been created", "OK"), \
                ("Certificate Import Wizard", "Welcome to the Certificate Import Wizard", "&Next >"), \
                ("Certificate Import Wizard", "Specify the file you want to import", "&Next >"), \
                ("Certificate Import Wizard", "To maintain security, the private key was protected with a password", "&Next >"), \
                ("Certificate Import Wizard", "Certificate Store", "&Next >"), \
                ("Certificate Import Wizard", "Completing the Certificate Import Wizard", "Finish"), \
                ("Certificate Import Wizard", "The import was successful", "OK"), \
                ("Security Warning", "Do you want to install this certificate?", "&Yes"),

            zero_it_dlg_handler['title_dialog_list'] = []
            zero_it_dlg_handler['static_text_list'] = []
            zero_it_dlg_handler['button_list']
            for title, text, button in cert_mgr:
                zero_it_dlg_handler['title_dialog_list'].append(title)
                zero_it_dlg_handler['static_text_list'].append(text)
                zero_it_dlg_handler['button_list'].append(button)

            zero_it_dlg_handler['class_name_dialog_list'] = []
            _dialog_handler(**zero_it_dlg_handler)
            time.sleep(20 * timeout)


            # Handle a dialog with specific class name and text
            zero_it_dlg_handler['class_name_dialog_list'] = ["#32770"]
            zero_it_dlg_handler['static_text_list'] = ["Configuration completed. Click 'Close' to finish"]
            zero_it_dlg_handler['button_list'] = ["Close"]
            zero_it_dlg_handler['title_dialog_list'] = []
            _dialog_handler(**zero_it_dlg_handler)
            time.sleep(3 * timeout)

            # Force to connect to the wireless network specified by the profile
            if ssid:
                os.popen('%s conn %s "%s" i "%s"' % (_wlantool_cmd, _adapter_guid, ssid, ssid))

            zero_it_dlg_handler['class_name_dialog_list'] = ["tooltips_class32"]
            zero_it_dlg_handler['static_text_list'] = []
            zero_it_dlg_handler['button_list'] = []
            zero_it_dlg_handler['title_dialog_list'] = []
            _dialog_handler(**zero_it_dlg_handler)
            time.sleep(8 * timeout)

            # Handle dialog Validate Server Certificate
            zero_it_dlg_handler['title_dialog_list'] = ["Validate Server Certificate"]
            zero_it_dlg_handler['static_text_list'] = ""
            zero_it_dlg_handler['button_list'] = ["OK"]
            zero_it_dlg_handler['class_name_dialog_list'] = []
            _dialog_handler(**zero_it_dlg_handler)
            time.sleep(5 * timeout)

    # Force to connect to the wireless network specified by the profile
    time.sleep(timeout)
    if ssid:
        os.popen('"%s conn %s "%s" i "%s"' % (_wlantool_cmd, _adapter_guid, ssid, ssid))


def _kill_zero_it_process():
    """
    This function kills process of Zero-IT before executing it
    """
    # Close dialog titled "Error" with static "prov.exe is already running
    while True:
        error_txt = "prov.exe is already running"
        dlg_handle_list = application.findwindows.find_windows(title = "Error")

        if dlg_handle_list:
            for handle_id in dlg_handle_list:
                hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
                child_ctrls_list = hwnd.Children()

                button_ok = False
                for child in child_ctrls_list:
                    if child.Class() == "Static" and error_txt in child.WindowText():
                        button_ok = True
                        break
                if button_ok:
                    for child in child_ctrls_list:
                        if child.Class() == "Button" and child.WindowText() == "OK":
                            child.Click()
                time.sleep(4)
        else:
            break
        time.sleep(4)

    time.sleep(2)
    static_txt = "Configuration completed. Click 'Close' to finish"
    dlg_handle_list = application.findwindows.find_windows(class_name = "#32770")
    if dlg_handle_list:
        for handle_id in dlg_handle_list:
            hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
            child_ctrls_list = hwnd.Children()

            button_close = False
            if child_ctrls_list:
                for child_obj in child_ctrls_list:
                    if child_obj.Class() == "Static" and static_txt in child_obj.WindowText():
                        button_close = True
                        break
        if button_close:
            for child_obj in child_ctrls_list:
                if child_obj.Class() == "Button" and child_obj.WindowText() == "Close":
                    time.sleep(2)
                    child_obj.Click()
                    break

        time.sleep(3)

def _dialog_handler(title_dialog_list = "", class_name_dialog_list = "", button_list = "", static_text_list = ""):
    """
    This function handles popup dialog
    Input:
    - title_dialog_list:
    - class_name_dialog_list:
    - button_list:
    - static_text_list:
    """
    # Finding dialog based on the dialog title names
    if title_dialog_list:
        i = 0
        for searched_dialog in title_dialog_list:
            start_time = time.time()
            search_dialog_title_timeout = 10
            while time.time() - start_time < search_dialog_title_timeout:
                dlg_handle_list = application.findwindows.find_windows(title = searched_dialog)
                if dlg_handle_list:
                    break

            if dlg_handle_list:
                found_hwnd = None
                for handle_id in dlg_handle_list:
                    # Get the handles of the controls
                    hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
                    child_ctrls_list = hwnd.Children()

                    for child_obj in child_ctrls_list:
                        if child_obj.Class() == "Static" and static_text_list[i] in child_obj.WindowText():
                            found_hwnd = child_ctrls_list
                            break
                        elif child_obj.Class() == "Edit":
                            if child_obj.ControlID() == 15510 or child_obj.ControlID() == 1003:
                                found_hwnd = child_ctrls_list
                                break
                    if found_hwnd: break

                if not found_hwnd:
                    raise Exception("Can not find exactly dialog with text \"%s\"" % static_text_list[i])

                found_button = False
                for child_obj in found_hwnd:
                    if child_obj.Class() == "Button" and button_list[i] == child_obj.WindowText():
                        time.sleep(1)
                        child_obj.Click()
                        found_button = True
                        break
                if not found_button:
                    raise Exception("Button %s not found" % button_list[i])

            time.sleep(5)
            i += 1

    # Finding dialog based on the dialog's class name
    else:
        i = 0
        for searched_class_name in class_name_dialog_list:
            start_time = time.time()
            timeout = 180
            found_hwnd = None
            found_dlg = False
            while True:
                if time.time() - start_time > timeout:
                    if searched_class_name == "tooltips_class32":
                        raise Exception("Can not find tooltip to process logon information")
                    else:
                        raise Exception("Can not find any dialog with text %s" % static_text_list[i])

                found_handle_id = False
                found_tooltips = False
                dlg_handle_list = application.findwindows.find_windows(class_name = searched_class_name)
                if dlg_handle_list:
                    for handle_id in dlg_handle_list:
                        hwnd = controls.HwndWrapper.HwndWrapper(handle_id)
                        child_ctrls_list = hwnd.Children()

                        if child_ctrls_list:
                            for child_obj in child_ctrls_list:
                                if child_obj.Class() == "Static" and static_text_list[i] in child_obj.WindowText():
                                    found_hwnd = hwnd
                                    found_handle_id = True
                                    break
                            if found_handle_id:
                                found_dlg = True
                                break
                        else:
                            for count in range(hwnd.ToolCount()):
                                tooltip_text_vista = "Click to provide additional information and connect"
                                tooltip_text_xp = "Click here to process your logon information"

                                if tooltip_text_vista in hwnd.GetTipText(count) or tooltip_text_xp in hwnd.GetTipText(count):
                                    found_handle_id = True
                                    found_hwnd = hwnd
                                    break
                            if found_handle_id:
                                found_dlg = True
                                break
                    if found_dlg:
                        break

            if found_hwnd.Children():
                found_button = False
                for child_obj in found_hwnd.Children():
                    if child_obj.Class() == "Button" and button_list[i] == child_obj.WindowText():
                        time.sleep(1.5)
                        child_obj.Click()
                        found_button = True
                        break
                if not found_button:
                    raise Exception("Button %s not found" % button_list[i])
            else:
                found_hwnd.Click()

            time.sleep(3)
            i = i + 1

def download_zero_it(eth_if_ip_addr, ip_addr, net_mask, activate_url, username, password, ip_type = IPV4):
    """
    Download ZeroIT tool and return the path to it.
    @param eth_if_ip_addr: IP address of the Ethernet interface
    @param ip_addr: Temporary IP address assigned to the interface
    @param net_mask: Network mask assigned to the interface
    @param activate_url: URL of the activation page on Zone Director
    @param username: credentials to download zero-it tool
    @param password: credentials to download zero-it tool
    @param version: ip version, it is 4 or 6.
    """
    #For ipv6, associate the station via a wlan, so don't need to set ethernet interface.
    #For device register if eth_if_ip_addr = None, system will connect to guest access wlan to download ZeroIT.
    if ip_type == IPV4 and eth_if_ip_addr:
        # Add the network of the ZD to the Ethernet interface
        verify_if(eth_if_ip_addr)
        add_ip_if(_get_if_info(eth_if_ip_addr)['if_name'], ip_addr, net_mask)
        m_obj = re.match(r"\w+://([0-9.]+)/\w+", activate_url)
        zd_ip_network = get_network_address(m_obj.group(1))
        # Add routing if zd and ip_addr are in different network
        if get_network_address(ip_addr) != zd_ip_network:
            gate_way = ".".join(ip_addr.split('.')[:-1]) + ".253"
            add_route(zd_ip_network, net_mask, gate_way)
            
    # Download Zero IT tool from ZD by accessing given URL
    param = {'activate_url': activate_url, 'username':username, 'password':password}
    output = os.popen("HttpClient.py download_zero_it \"%s\"" % str(param))
    buffer = "".join(line for line in output)
    output.close()
    
    if buffer.find("ERROR") != -1:
        if ip_type == IPV4:
            verify_if(eth_if_ip_addr)
            
        raise Exception(buffer)
    
    tool_path = buffer.strip("\r").strip("\n").strip()
    
    if ip_type == IPV4 and eth_if_ip_addr:
        if get_network_address(ip_addr) != zd_ip_network:
            delete_route(zd_ip_network)
        # Remove the new network on the Ethernet interface
        verify_if(eth_if_ip_addr)

    # And return the path to the downloaded file
    return tool_path

def download_speedflex(speedflex_url):
    """
    Download SpeedFlex tool and return the path to it.
    """
    # Download SpeedFlex from ZD by accessing given URL
    param = {'speedflex_url': speedflex_url}
    output = os.popen("HttpClient.py download_speedflex \"%s\"" % str(param))
    buffer = "".join(line for line in output)
    output.close()
    speedflex_path = buffer.strip("\r").strip("\n").strip()
    print speedflex_path

    # And return the path to the downloaded file
    return speedflex_path

def cfg_wlan_with_zero_it(
        eth_if_ip_addr, ip_addr, net_mask, auth_method, use_radius, activate_url,
        username, password, ssid):
    """
    Download zero-it tool and run it. Some extra steps are performed if use_onex and/or
    use_radius are enabled.
    @param ip_addr: IP address of the Ethernet interface
    @param mask: Network mask of the Ethernet interface
    @param ssid: SSID of the WLAN
    @param use_onex: a boolean value indicates EAP is used or not
    @param use_radius: a boolean value indicates radius is used or not
    @param activate_url: URL of the activation page on Zone Director
    @param username: credentials to download zero-it tool
    @param password: credentials to download zero-it tool
    """
    # Download the tool
    tool_path = download_zero_it(eth_if_ip_addr, ip_addr, net_mask, activate_url, username, password)
    print "The ZeroIT tool is saved at %s" % tool_path

    # Execute the Zero IT tool after downloading
    time.sleep(2)
    print "Execute the ZeroIT tool"
    return execute_zero_it(tool_path, ssid, auth_method, use_radius)


def get_win_version():
    """
    @return: Version of Windows on the system. "51" is Windows XP and "60" is Vista
    """
    win_ver_major, win_ver_minor, win_ver_build, win_ver_platform, win_ver_text = sys.getwindowsversion()
    return "%s%s" % (win_ver_major, win_ver_minor)

def get_os_platform():
    """
    @return: a string such as "Windows,XP,tb32-sta1"
    """
    sta_os, sta_hostname, sta_release, sta_version, sta_machine, sta_processor = platform.uname()
    return "%s,%s,%s" % (sta_os, sta_release, sta_hostname)

def get_wlan_profile_list(adapter_name = ""):
    """
    This function returns the list of the existing wireless profiles on a wireless adapter
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    # Get the list of the profiles created on the adapter
    pattern = '[\t ]+"([a-zA-Z0-9_\- ]+)"'
    profile_list = []
    cmd_line = "%s gpl %s" % (_wlantool_cmd, _adapter_guid)
    _dispmsg("[EXEC get_wlan_profile_list]: %s" % cmd_line)
    output = os.popen(cmd_line)
    done = False
    for line in output:
        match_obj = re.match(pattern, line)
        if match_obj:
            profile_list.append(match_obj.group(1))
        elif line.find("completed"):
            done = True
    if not done:
        raise Exception("Can not get list of profiles")
    return profile_list

def connect_to_wlan(ssid, adapter_name = "", bssid = ""):
    """
    This function forces a station to connect to the specified wlan
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    _exec_program('%s conn %s "%s" i "%s" %s' % (_wlantool_cmd, _adapter_guid, ssid, ssid, bssid))

def disconnect_from_wlan(adapter_name = ""):
    """
    This function forces a station to disconnect to the current associated WLAN
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    _exec_program('%s dc %s' % (_wlantool_cmd, _adapter_guid))

def transmit_traffic(dst_addr, protocol, dst_port):
    sock_type = {'6': socket.SOCK_STREAM, '17': socket.SOCK_DGRAM}
    if protocol == '1':
        ping(dst_addr)
    else:
        if protocol in ['6', '17']:
            protocols = [protocol]
        elif protocol.lower() == 'any':
            protocols = ['6', '17']
        for proto in protocols:
            try:
                s = socket.socket(socket.AF_INET, sock_type[proto])
                s.connect((dst_addr, int(dst_port)))
                s.send('abcdef')
            except:
                pass

def start_console_application(path, pause = "1.0"):
    '''
    '''
    try:
        SendKeys.key_down(SendKeys.CODES['LWIN'])
        SendKeys.key_down(82)
        SendKeys.key_up(SendKeys.CODES['LWIN'])
        SendKeys.key_up(82)

        time.sleep(float(pause))
        run_window = application.Application()
        run_window.connect_(title_re = "Run", class_name = "#32770")
        run_window_handle = run_window.window_(title_re = "Run").handle
        SetForegroundWindow(run_window_handle)
        BringWindowToTop(run_window_handle)
        path = string.replace(path, " ", "{SPACE}")
        path = string.replace(path, "~", "+`")
        SendKeys.SendKeys("{HOME}^+{END}{DELETE}%s{ENTER}" % path)
    except Exception, e:
        print e.message
        return e.message

def stop_console_application(title = ""):
    path = ""
    try:
        app = application.Application()
        app.connect_(title_re = title, class_name = "ConsoleWindowClass")
        path = app.window_(title_re = title).WrapperObject().WindowText()
        app.Kill_()
    except Exception, e :
        print e.message

    return path

def start_zapd(path, pause = "1.0"):
    return start_console_application(path, pause)

def stop_zapd():
    return stop_console_application(".*zapd.exe.*")

def start_speedflex(path, pause = "1.0"):
    return start_console_application(path, pause)

def stop_speedflex(filename):
    return stop_console_application(".*%s.*" % filename)
    

def start_tshark(infname = "Wireless", params = ""):
    """
    Start tshark to capture traffic on the specific interface with given configuration.
    - ip_addr: used to find exactly interface to capture.
    - params: for filter, size etc. like: -c 1500 -V -p -f "udp port 67 and udp port 68"
    """
    global _tshark_process, _tshark_capture_file
    #@author: Jane.Guo add to fix the bug if infname isn't the same with adapter name, use guid to match
    global _adapter_guid
    inf_guid = _adapter_guid.upper()
    
    stop_tshark()
    # Find interface's name to capture
    infindex = ""
    cmd = "%s -D" % _tshark_cmd
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    if not output:
        output = subprocess.Popen(cmd, stderr=subprocess.PIPE).communicate()[1]
    if not output:
        return "error, cannot get wireless interface"
#    if_list = os.popen("%s -D" % _tshark_cmd).readlines()
    for inf in output.split('\r\n'):
        pattern=r"([\d]+)\.\s*[\.\\]*([^\s]*)"
        m = re.match(pattern, inf, re.I)
        if m:
            if re.search(infname, inf) or re.search(inf_guid, inf):
                infindex = m.group(1)
                break
    
    if os.path.exists(_tshark_capture_file):
        os.remove(_tshark_capture_file)
        print 'Remove file %s' % _tshark_capture_file
        
    print "Found interface for capture is: %s " % infindex
    cmd = "%s -i %s -V" % (_tshark_cmd, infindex)
    cmd = "%s -c 1500 -w %s %s" % (cmd, _tshark_capture_file, params)
    print cmd
    stop_tshark()
    _tshark_process = createProcess(cmd)    


def analyze_tshark_traffic(params = "", expr = None):
    """
    Read captured file in tshark command.
    params: anaysis command.
    return_as_list: True/False
    """
    global _tshark_capture_file 

    #@author: Jane.Guo @since: 2013-10 adapt to windows7
    os_name = get_os_platform()
    if re.match('Windows,7',os_name):
        #chen.tao @2013-11-18 to fix ZF-6172
        #cmd = "%s -R '%s' -2 -V -r %s" % (_tshark_cmd, params, _tshark_capture_file)
        cmd = '%s -R "%s" -2 -V -r %s' % (_tshark_cmd, params, _tshark_capture_file)
        #chen.tao @2013-11-18 to fix ZF-6172
    elif re.match('Windows,XP',os_name):
        cmd = "%s %s -V -r %s" % (_tshark_cmd, params, _tshark_capture_file)
    
    print cmd
    traffic = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    if not traffic:
        return (-1, "Haven't any traffic that been filter.")
    if not expr:
        print traffic
        return (0, "Haven't do any filter.")
    
    if re.search(expr, traffic, re.MULTILINE | re.DOTALL):
        return (1, "Okay.")
    else:
        return (2, "Doesn't match.")


def stop_tshark():
    """ Stop Windump by killing process """
    global _tshark_process
    if _tshark_process:
        _tshark_process.kill()        
        _tshark_process = ""
    

# Tu Bui: this function is use for ap
# will merge with zd later
def start_windump_for_ap(ip_addr = "", count = "", proto = "", file_path = "", host = ""):
    """
    Start tcpdump to capture traffic on the specific interface with given configuration
    - ip_addr: used to find exactly interface to capture
    - count: the maximum packets that satisfy requirement are captured
    - file_path: path of file that saves capturing information
    - host: specify ip address (destination or source) to capture
    """
    global _windump_process
    # Find interface's name to capture
    inf = ""
    if_list = os.popen("%s -D" % _windump_cmd).readlines()
    for inf in if_list:
        if ip_addr in inf:
            inf = inf.split(".")[0]
            break
    print "Found interface for capture is: %s " % inf

    cmd = "%s -i %s -vv -nn" % (_windump_cmd, inf)
    cmd = "%s -w %s" % (cmd, file_path)
    if count: cmd = "%s -c %s" % (cmd, count)
    if proto: cmd = "%s %s" % (cmd, proto)
    if host: cmd = "%s host %s" % (cmd, host)

    print cmd
    stop_windump()
    _windump_process = createProcess(cmd)


def start_windump(ip_addr = "", params = ""):
    """
    Start tcpdump to capture traffic on the specific interface with given configuration
    - ip_addr: used to find exactly interface to capture
    - count: the maximum packets that satisfy requirement are captured
    - file_path: path of file that saves capturing information
    - host: specify ip address (destination or source) to capture
    """
    global _windump_process, _windump_capture_file
    # Find interface's name to capture
    inf = ""
    if_list = os.popen("%s -D" % _windump_cmd).readlines()
    for inf in if_list:
        if ip_addr in inf:
            inf = inf.split(".")[0]
            break
    print "Found interface for capture is: %s " % inf

    cmd = "%s -i %s -vv -nn" % (_windump_cmd, inf)
    cmd = "%s -s 1500 -w %s %s" % (cmd, _windump_capture_file, params)
    stop_windump()
    _windump_process = createProcess(cmd)

def stop_windump():
    """ Stop Windump by killing process """
    global _windump_process
    if _windump_process:
        _windump_process.kill()
        _windump_process = ""

def analyze_traffic(file_path, proto = "UDP", get_qos = True):
    """
    Analyze traffic that captured by tcpdump
    Return a list of dictionaries, in there each dictionary contains source ip address, destination ipaddress
    and tos value of each packet.
    """
    traffic = os.popen("%s -vv -nn -r %s" % (_windump_cmd, file_path)).readlines()
    buf = [line.strip('\r').strip('\n') for line in traffic]
    traffic_info = []
    for item in buf:
        temp = {}
        src_ip_pat = ".*\) ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+) >.*"
        mobj = re.match(src_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            temp['src_ip'] = ".".join(txt.split('.')[:-1])

        dst_ip_pat = ".* > ([\w]+\.[\w]+\.[\w]+\.[\w]+\.[\w]+): %s.*" % proto
        mobj = re.match(dst_ip_pat, item)
        if mobj:
            txt = mobj.group(1)
            temp['dst_ip'] = ".".join(txt.split('.')[:-1])

        tos_pat = ".*\(tos (0x[\w]+).*$"
        mobj = re.match(tos_pat, item)
        if mobj:
            temp['tos'] = mobj.group(1)

        if len(temp) > 1:
            traffic_info.append(temp)

        if len(traffic_info) == 20:
            break

    return traffic_info

def parse_traffic():
    """
    Analyze traffic that captured by tcpdump
    Return a list of dictionaries, in there each dictionary contains source ip address, destination ipaddress
    and tos value of each packet.
    """
    global _windump_capture_file
    file_path = _windump_capture_file
    return analyze_traffic(file_path)

def start_iperf(serv_addr = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = "", multicast_srv = False, port =0):
    """
    Execute iperf to send traffic with the given configuration
    - serv_addr: ip_address of iperf server
    - test_udp: This is the bool value. If it's True, sent traffic is udp. Otherwise, sent traffic is tcp
    - packet_len: number of bytes of each packet
    - bw: bandwidth
    - timeout: maximum time to send traffic
    - tos: send traffic with ToS value
    - multicast_srv: option to bind multicast address to igmp table in the AP
    """
    global _iperf_process
    cmd = "%s -C" % _iperf_cmd
    if multicast_srv:
        cmd = "%s -s -B %s" % (cmd, serv_addr)
    else:
        if serv_addr: cmd = "%s -c %s" % (cmd, serv_addr)
        else: cmd = "%s -s" % cmd
    if test_udp: cmd = "%s -u" % cmd
    if packet_len: cmd = "%s -l %s" % (cmd, packet_len)
    if bw: cmd = "%s -b %s" % (cmd, bw)
    if timeout: cmd = "%s -t %s" % (cmd, timeout)
    if tos: cmd = "%s -S %s" % (cmd, tos)
    if port: cmd = "%s -p %s" % (cmd, port)
    # Execute the command
    stop_iperf()
    _iperf_process = createProcess(cmd)

def start_iperf_server(serv_addr = "", test_udp = True):
    if serv_addr:
        start_iperf(serv_addr = serv_addr, test_udp = test_udp, multicast_srv = True)
    else:
        start_iperf(serv_addr = "", test_udp = test_udp, multicast_srv = False)

def start_iperf_client(stream_srv = "", test_udp = True, packet_len = "", bw = "", timeout = "", tos = ""):
    start_iperf(serv_addr = stream_srv, test_udp = test_udp, packet_len = packet_len, bw = bw, timeout = timeout, tos = tos)

def stop_iperf():
    """
    Stop iperf on the windows by killing its process
    """
    global _iperf_process
    if _iperf_process:
        _iperf_process.kill()
        _iperf_process = ""

def add_route(route = "", net_mask = "", gateway = ""):
    """
    add multicast route which used to send multicast traffic with iperf
    - option: add or del
    """
    cmd = "route add %s mask %s %s" % (route, net_mask, gateway)
    os.system(cmd)
    time.sleep(1)

def delete_route(route):
    cmd = "route delete %s" % route
    os.system(cmd)
    time.sleep(2)

def reboot_station():
    cmd_line = "shutdown -r -t 3"
    _exec_program(cmd_line)

def restart_adapter():
    if _adapter_vid:
        # Restart adapter
        _exec_program("%s restart %s" % (_devcon_cmd, _adapter_vid))
        time.sleep(5)

def disable_adapter():
    if _adapter_vid:
        #Disable adapter
        if _is_wifi_card:
            cmd = "net stop Wlansvc"
        else:
            cmd = "net stop dot3svc"

        _exec_program(cmd)
        time.sleep(5)

def enable_adapter():
    if _adapter_vid:
        #Enable adapter
        if _is_wifi_card:
            cmd = "net start Wlansvc"
        else:
            cmd = "net start dot3svc"

        _exec_program(cmd)
        time.sleep(5)

def auth_wire_sta(username, password, domain = None):
    #Catch tooltips prompt and click.
    #disable_adapter()
    #enable_adapter()
    app = application.Application()
    num = 3
    while num:
        num = num - 1
        try:
            s_t = time.time()
            while time.time() - s_t < 60:
                try:
                    hndlist = find_windows(class_name="tooltips_class32", 
                            title_re="Click to provide additional information")
                    if not hndlist:
                        print "Not Found"
                        disable_adapter()                        
                        enable_adapter()
                        continue

                    #Catch tooltips prompt and click.
                    dlg = app.connect_(class_name = 'tooltips_class32')
                    title = 'ToolTips'
                    dlg[title].Click()
                    #Catch Credentials Dialog
                    dlg2 = app.connect_(title_re = "Enter Credentials|Windows Security")
                    app.dlg.Edit1.SetFocus()
                    app.dlg.Edit1.TypeKeys(username)
                    app.dlg.Edit2.SetFocus()
                    app.dlg.Edit2.TypeKeys(password)
                    if domain:
                        app.dlg.Edit3.SetFocus()
                        app.dlg.Edit3.TypeKeys(domain)
                    app.dlg.OK.Click()                    
                    time.sleep(1)
                    break
                except Exception, e:
                    time.sleep(1)
            
            time.sleep(1)
            s_t = time.time()
            while time.time() - s_t < 10:
                (ip, mac) = get_8021x_address()
                if ip:
                    return             
                else:
                    time.sleep(1)

        except Exception, e:
            print e.message
            _kill_tooltips()
            disable_adapter()
            enable_adapter()
        else:
            _kill_tooltips()
            disable_adapter()
            enable_adapter()

    raise Exception("Authentication FAIL")
    
 
def _kill_tooltips():
    hndlist = find_windows(class_name="tooltips_class32", 
            title_re="Click to provide additional information")
    if hndlist:
        app2 = application.Application()
        dlg = app2.connect_(class_name = "tooltips_class32", 
                title_re="Click to provide additional information")
        dlg.kill_()



def get_subnet_mask(ip_addr, use_short_form = True):
    """ Return the default subnet mask of a given IP address
    Input:
    - ip_addr: the subject address
    - use_short_form: if True, the mask is in format /N; otherwise it is /N.N.N.N
    Output: the subnet mask value
    """
    ip_addr_pattern = "([0-9]+)\.[0-9]+\.[0-9]+\.[0-9]+"
    match = re.match(ip_addr_pattern, ip_addr)
    if not match:
        raise Exception("Invalid IP address %s" % ip_addr)
    first_octet = int(match.group(1))
    if first_octet < 128:
        if use_short_form: return "8"
        else: return "255.0.0.0"
    elif first_octet < 192:
        if use_short_form: return "16"
        else: return "255.255.0.0"
    elif first_octet < 224:
        if use_short_form: return "24"
        else: return "255.255.255.0"
    else:
        raise Exception("The address is not configurable to hosts (%s)" % ip_addr)



def get_ip_config(adapter_name = ""):
    """
    Return a dictionary with all the information of the current adapter or the given adapter_name
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: a dictionary with the keys are parsed from the output of the command IPCONFIG /all
    """
    output = os.popen("ipconfig /all")
    found_name = False
    ip_info = {}
    for line in output:
        line = line.strip()
        if not line:
            if found_name and ip_info: break
            continue
        if line.find(adapter_name) != -1:
            found_name = True
        elif found_name:
            x = line.split(' :')
            if len(x) < 2:
                continue
            tag = x[0].rstrip('. ')
            val = x[1].lstrip(' ')
            if tag == "IP Address" or tag == "IPv4 Address":
                ip_info['ip_addr'] = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                ip_info['mac_addr'] = ":".join(val.split("-"))
            elif tag == "Subnet Mask":
                ip_info['subnet_mask'] = val
            elif tag == "Lease Obtained":
                ip_info['lease_obtained'] = val
            elif tag == "Lease Expires":
                ip_info['lease_expires'] = val
            elif tag == "DHCP Server":
                ip_info['dhcp_server'] = val

    output.close()

    return ip_info

def get_network_address(ip_addr, mask = ""):
    """ Return the default network address of a given IP address
    Input:
    @param ip_addr: the subject address
    @param mask: mask of the given address; if not given, default mask will be used
                 mask can also given as the bit length
    Output: the network address value
    """
    ip_addr_pattern = "([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)"
    ip_addr_obj = re.match(ip_addr_pattern, ip_addr)
    if not ip_addr_obj:
        raise Exception("Invalid IP address %s given" % ip_addr)
    ip_octets = [int(ip_addr_obj.group(i)) for i in [1, 2, 3, 4]]

    if not mask:
        mask = get_subnet_mask(ip_addr)
    mask_obj = re.match(ip_addr_pattern, mask)
    if not mask_obj:
        try:
            l = int(mask)
            mask_octets = [0] * 4
            for i in range(l / 8):
                mask_octets[i] = 255
            if i < 3 and l % 8:
                mask_octets[i + 1] = 2 ** (8 - l % 8)
        except ValueError:
            raise Exception("Invalid mask %s given" % mask)
    else:
        mask_octets = [int(mask_obj.group(i)) for i in [1, 2, 3, 4]]

    network_octets = [str(mask_octets[i] & ip_octets[i]) for i in range(4)]
    return ".".join(network_octets)

def get_visible_ssid(adapter_name = ""):
    """
    get a list of  SSID is broadcasted on the air
    @param adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    @return: list of SSID found on the air ""
    """
    global _adapter_guid, _wlantool_cmd

    _update_guid(adapter_name)

    cmd_line = "%s gvl %s" % (_wlantool_cmd, _adapter_guid)
    _dispmsg("[EXEC check_ssid]: %s" % cmd_line)
    output = os.popen(cmd_line)
    buffer = "".join(line for line in output)
    output.close()
    if buffer.find("successfully") == -1:
        raise Exception("Unable to get list of visible WLANs")
    pattern = "SSID: (.*)[\\r\\n]"
    visible_ssid_list = re.findall(pattern, buffer)
    return visible_ssid_list



CONST_AUTH_METHODS = {
    0: "WebAuth",
    1: "HotspotAuth",
    2: "GuestAuth",
    3: "SelfServiceGuestAuth",
}

AUTH_PARAMS = {
    CONST_AUTH_METHODS[0]: {
        'dest_url': "",
        'username': "",
        'password': "",
        'expected_data': "",
    },
    CONST_AUTH_METHODS[1]: {
        'dest_url': "",
        'username': "",
        'password': "",
        'expected_data': "",
    },
    CONST_AUTH_METHODS[2]: {
        'dest_url': "",
        'redirect_url': "",
        'guestpass': "",
        'use_tou': None,
        'no_auth': None,
        'expected_data': "",
    },     
    CONST_AUTH_METHODS[3]: {
        'dest_url': "",
        'redirect_url': "",
        'guestpass': "",
        'use_tou': None,
        'use_tac':None,
        'tac_text':None,
        'no_auth': None,
        'expected_data': "",
        'username':"",
        'email':"",
        'countrycode':"",
        'mobile':"",
        'clear_mobile':"",
        'sta_mac':None,
        'mobile_exist_flag':True,
        
    },
}


def get_browser_agent():
    '''
    '''
    global browser_agent

    try:
        browser_agent

    except:
        BrowserAgent = __import__(
            "BrowserAgent", fromlist = ['']
        ).__dict__['BrowserAgent']

        browser_agent = BrowserAgent()

    return browser_agent


def init_browser(
        browser = "firefox", timeout = 30, **kwargs
    ):
    '''
    '''
    global browser_agent
    global browser_id

    try:
        browser_id

    except:
        browser_id = browser_agent.init_browser(
            browser, timeout, **kwargs
        )

    return browser_id


def launch_browser(browser_id, tries = 3, timeout = 15):
    '''
    '''
    global browser_agent
    global is_browser_started

    try:
        is_browser_started

    except:
        is_browser_started = False

    count = 0
    while not is_browser_started and count < tries:
        count += 1
        try:
            print "Trying to start the browser..."
            browser_agent.launch_browser(browser_id)
            is_browser_started = True

        except Exception:
            if count >= tries:
                raise

            print "Retry to start the browser %s time(s)" % count
            time.sleep(timeout)

    if is_browser_started:
        return browser_agent.get_browser(browser_id)


def init_and_start_browser(
        browser = "firefox", tries = 3, timeout = 15, **kwargs
    ):
    '''
    '''
    get_browser_agent()
    browser_id = init_browser(browser, timeout = timeout, **kwargs)
    browser_ins = launch_browser(browser_id, tries, timeout)

    if browser_ins:
        return browser_id


def close_browser(browser_id):
    '''
    '''
    global browser_agent
    global is_browser_started

    browser_agent.close_browser(browser_id)

    is_browser_started = False


def perform_client_auth_using_browser(
        browser_id, auth_method, auth_args, **kwargs
    ):
    '''
    '''
    global browser_agent
    global captive_portal

    browser = browser_agent.get_browser(browser_id)

    if auth_method not in CONST_AUTH_METHODS.values():
        raise Exception(
            "The %s method is invalid or currently not supported." %
            auth_method
        )

    CaptivePortal = __import__(
        "client_auth.%s" % auth_method,
        fromlist = ['']
    ).__dict__[auth_method]

    captive_portal = CaptivePortal()

    params = AUTH_PARAMS
    for k in params[auth_method]:
        if auth_args.has_key(k):
            params[auth_method].update({k: auth_args[k]})

    captive_portal.set_params(**params[auth_method])

    done_login = _client_auth_with_retries(
        browser, captive_portal, **kwargs
    )
    
    return done_login


def _client_auth_with_retries(
        browser, captive_portal, tries = 3, timeout = 15,
    ):
    '''
    '''
    count = 0
    done_login = False
    while not done_login and count < tries:
        count += 1
        try:
            print "Try to perform client authentication"
            captive_portal.set_browser(browser)
            done_login = captive_portal.auth()

        except Exception:
            if count >= tries:
                raise

            print "Retry to perform client authentication %s time(s)" % count
            time.sleep(timeout)
            
    return done_login


def download_file_on_web_server(
        browser_id, validation_url, download_loc, file_name, **kwargs
    ):
    '''
    '''
    global browser_agent
    global captive_portal

    try:
        captive_portal

    # no captive portal method was init'd,
    # but user wanted to download a file from the web server.
    # init the generic Captive Portal instead:
    except:
        CaptivePortal = __import__(
            "client_auth.CaptivePortal",
            fromlist = ['']
        ).__dict__['CaptivePortal']

        captive_portal = CaptivePortal()

    messages = {}
    args = {
        'validation_url': validation_url,
        'download_loc': download_loc,
        'file_name': file_name,
    }
    args.update(kwargs)

    browser = browser_agent.get_browser(browser_id)
    captive_portal.set_browser(browser)
    captive_portal.set_params(**args)

    try:
        status = captive_portal.download_file()
        messages.update({
            'download': {
                'status': status,
                'message': captive_portal.message,
            }
        })

    except Exception, ex:
        messages.update({
            'download': {
                'status': False,
                'message': ex.message,
            }
        })

    finally:
        return messages


def perform_web_auth_using_browser(browser_id, web_auth_arg, **kwargs):
    '''
    '''
    global captive_portal
    messages = {}

    try:
        auth_args = {
            'dest_url': web_auth_arg['target_url'],
            'username': web_auth_arg['user_login_auth']['username'],
            'password': web_auth_arg['user_login_auth']['password'],
            'expected_data': web_auth_arg['expected_data'],
        }
        perform_client_auth_using_browser(browser_id, "WebAuth", auth_args, **kwargs)

        login_done = captive_portal.is_login_successful()
        messages.update({
            'login': {
                'status': login_done,
                'message': captive_portal.message,
            }
        })

        if not login_done:
            return messages

    except Exception, ex:
        messages.update({
            'auth': {
                'status': False,
                'message': ex.message,
            }
        })

    finally:
        return messages


def perform_hotspot_auth_using_browser(browser_id, hotspot_auth_arg, **kwargs):
    '''
    '''
    global captive_portal
    messages = {}

    try:
        auth_args = {
            'dest_url': hotspot_auth_arg['original_url'],
            'username': hotspot_auth_arg['user_login_auth']['username'],
            'password': hotspot_auth_arg['user_login_auth']['password'],
            'expected_data': hotspot_auth_arg['expected_data'],
        }
        perform_client_auth_using_browser(browser_id, "HotspotAuth", auth_args, **kwargs)

        time.sleep(10)

        login_done = captive_portal.is_login_successful()
        messages.update({
            'login': {
                'status': login_done,
                'message': captive_portal.message,
            }
        })

        if not login_done:
            return messages

    except Exception, ex:
        messages.update({
            'auth': {
                'status': False,
                'message': ex.message,
            }
        })

    finally:
        return messages


def perform_guest_auth_using_browser(browser_id, guest_auth_arg, **kwargs):
    '''
    '''
    global captive_portal
    messages = {}

    try:
        auth_args = {
            'dest_url': guest_auth_arg['target_url'],
            'guestpass': guest_auth_arg['guest_login']['key'],
            'redirect_url': guest_auth_arg['redirect_url'],
            'use_tou': guest_auth_arg['guest_auth_cfg']['use_tou'],
            'no_auth': guest_auth_arg['no_auth'],
            'expected_data': guest_auth_arg['expected_data'],
        }
        if not auth_args.get('redirect_url'):
            auth_args.update({
                'redirect_url': auth_args['dest_url']
            })
        perform_client_auth_using_browser(browser_id, "GuestAuth", auth_args, **kwargs)

        time.sleep(10)

        login_done = captive_portal.is_login_successful()
        messages.update({
            'login': {
                'status': login_done,
                'message': captive_portal.message,
            }
        })

        if not login_done:
            return messages

        done_tou = captive_portal.check_and_accept_tou_if_found()
        messages.update({
            'tou': {
                'status': done_tou,
                'message': captive_portal.message,
            }
        })

        if not auth_args['no_auth']:
            captive_portal.click_to_follow_redirect_url()
            #@author: Jane.Guo @since: 2013-10 fix bug check redirector isn't done if no auth.
            done_redir = captive_portal.is_redirect_url_correct()
            messages.update({
                'redirect': {
                    'status': done_redir,
                    'message': captive_portal.message,
                }
            })

    except Exception, ex:
        messages.update({
            'auth': {
                'status': False,
                'message': ex.message,
            }
        })

    finally:
        return messages

#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service 
def get_captive_portal_ins(browser_id, guest_auth_arg):
    
    global browser_agent
  
    messages = {}
   
    try:
        auth_args = {
            'dest_url': guest_auth_arg['target_url'],
            'redirect_url': guest_auth_arg['redirect_url'],          
            'username': guest_auth_arg['user_register_infor']['username'],
            'email': guest_auth_arg['user_register_infor']['email'],
            'countrycode':guest_auth_arg['user_register_infor']['countrycode'],
            'mobile': guest_auth_arg['user_register_infor']['mobile'],
            'clear_mobile':guest_auth_arg['clear_mobile'],
            'guestpass': guest_auth_arg.get('guest_pass'),
            'use_tac':guest_auth_arg.get('use_tac'),
            'tac_text':guest_auth_arg.get('tac_text'),
            'mobile_exist_flag':guest_auth_arg.get('mobile_exist_flag'),#@author: yuyanan @change: 9.12.1 behavior change,remove mobile textbox when select screen on zd
            }
        if not auth_args.get('redirect_url'):
            auth_args.update({
                'redirect_url': auth_args['dest_url']
            })
        
        browser = browser_agent.get_browser(browser_id)
        CaptivePortal = __import__("client_auth.SelfServiceGuestAuth",fromlist = ['']).__dict__[CONST_AUTH_METHODS[3]]
        captive_portal_ins = CaptivePortal()

        params = AUTH_PARAMS
        for k in params[CONST_AUTH_METHODS[3]]:
            if auth_args.has_key(k):
                params[CONST_AUTH_METHODS[3]].update({k: auth_args[k]})

        captive_portal_ins.set_params(**params[CONST_AUTH_METHODS[3]])
        
        captive_portal_ins.set_browser(browser)
        messages.update({
            'intcaptive': {
                'status': True,
                'captive_ins': captive_portal_ins,
            }
        })  
    except Exception, ex:
        messages.update({
            'intcaptive': {
                'status': False,
                'message': ex.message,
            }
        })
        
    return messages

#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service 
def get_selfservice_contact_using_browser(browser_id, guest_auth_arg):
    
    messages = get_captive_portal_ins(browser_id, guest_auth_arg)
    if messages.get('intcaptive').get('status'):
        captive_portal_ins = messages.get('intcaptive').get('captive_ins')
        messages = captive_portal_ins.get_contact_detail()
    
    return messages

#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service 
def update_selfservice_contact_using_browser(browser_id, guest_auth_arg):
    
    messages = get_captive_portal_ins(browser_id, guest_auth_arg)
    if messages.get('intcaptive').get('status'):
        captive_portal_ins = messages.get('intcaptive').get('captive_ins')
        messages = captive_portal_ins.update_contact_detail()
       
    return messages

#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service 
def generate_guestpass_with_selfservice_using_browser(browser_id, guest_auth_arg):
     
    messages = get_captive_portal_ins(browser_id, guest_auth_arg)
    
    if messages.get('intcaptive').get('status'):
        captive_portal_ins = messages.get('intcaptive').get('captive_ins')
        messages = captive_portal_ins.generate_guestpass_on_web()

    return messages

#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service 
def generate_multi_guestpass_with_selfservice_using_command(guest_auth_arg):
    
    message = {}
    CaptivePortal = __import__("client_auth.SelfServiceGuestAuth",fromlist = ['']).__dict__[CONST_AUTH_METHODS[3]]
    captive_portal_ins = CaptivePortal()
   
    zd_ip = guest_auth_arg.get('zd_ip')
    target_num = guest_auth_arg.get('expect_guestpass_count')
    timeout = guest_auth_arg.get('multi_guestpass_time_out')
    start_num = 1
    start_time = time.time()
  
    while True:
        res = captive_portal_ins.generate_multiple_guestpass(start_time,start_num=start_num,zd_ip=zd_ip,target_num = target_num)
        if res == 'Success':
            print "Success"
            print "time used: %s seconds"%(time.time() - start_time)
            message.update({'status':True,
                            'message':'success,time used:%s seconds'%(time.time()- start_time)})
            return message
        
        elif res == "MAX":
            print "time used: %s seconds"%(time.time() - start_time)
            print "Reached MAX,quit"
            
            message.update({'status':True,
                            'message':'success,Reached MAX,quit,time used:%s seconds'%(time.time()- start_time)})
            return message
        else:
            if time.time() - start_time> timeout:
                print "timed out, %s guest passes are generated!"%(res-1)
                message.update({'status':False,
                            'message':'timed out, %s guest passes are generated!'%(res-1)})
                return message
            else:
                print "Process failed, continue from %s"%res
                start_num = res
    
#@author:yuyanan @since:2015-4-15 @change:;adapt to 9.10 self service     
def perform_self_service_guest_auth_using_browser(browser_id, guest_auth_arg, **kwargs):  
    
    global captive_portal
    messages = {}
   
    try:
        auth_args = {
            'dest_url': guest_auth_arg['target_url'],
            'redirect_url': guest_auth_arg['redirect_url'],
            'use_tou':guest_auth_arg['use_tou'],
            'username': guest_auth_arg['user_register_infor']['username'],
            'email': guest_auth_arg['user_register_infor']['email'],
            'countrycode':guest_auth_arg['user_register_infor']['countrycode'],
            'mobile': guest_auth_arg['user_register_infor']['mobile'],
            'expected_data': guest_auth_arg['expected_data'],
            'no_auth': guest_auth_arg['no_auth'],
            'guestpass': guest_auth_arg['guest_pass'],
            'generate_guestpass_flag':guest_auth_arg.get('generate_guestpass_flag',True),
            'sta_mac':guest_auth_arg['sta_mac'],
            }
        if not auth_args.get('redirect_url'):
            auth_args.update({
                'redirect_url': auth_args['dest_url']
            })
            
        auth_ok = perform_client_auth_using_browser(browser_id, "SelfServiceGuestAuth", auth_args, **kwargs)
        
        if not auth_ok:
            messages.update({
                              'login': {
                                        'status': auth_ok,
                                        'message': captive_portal.message,
                                        }
                              })
            return messages

        time.sleep(10)
        
        login_done = captive_portal.self_service_is_login_successful()
        messages.update({
            'login': {
                'status': login_done,
                'message': captive_portal.message,
            }
        })

        if not login_done:
            return messages
        
        
        done_tou = captive_portal.check_and_accept_tou_if_found()
        messages.update({
            'tou': {
                'status': done_tou,
                'message': captive_portal.message,
            }
        })

        if not auth_args['no_auth']:
            captive_portal.click_to_follow_redirect_url()
            #@author: Jane.Guo @since: 2013-10 fix bug check redirector isn't done if no auth.
            done_redir = captive_portal.is_redirect_url_correct()
            messages.update({
                'redirect': {
                    'status': done_redir,
                    'message': captive_portal.message,
                }
            })
    except Exception, ex:
        messages.update({
            'auth': {
                'status': False,
                'message': ex.message,
            }
        })

    finally:
        return messages


def send_arping(**kwargs):
    """
    @author: An Nguyen, an.nguyen@ruckuswireless.com
    The hardping.exe is used to generate the broadcast arp packet 
    """
    params = {'dest_ip': ''}
    params.update(kwargs)
    
    cmd_line = "%s %s" % (_arping_tool, params['dest_ip'])
    _dispmsg("[EXEC CMD]: %s" % (cmd_line))
    output = os.popen(cmd_line)
    
    res = {'raw_output': ''}
    pattern = '[R|r]eply from ([0-9.]+) \[([a-fA-F0-9:]{17})\]'
    
    for line in output:
        res['raw_output'] += line 
        mat = re.match(pattern, line)
        if mat:
            res[mat.group(1)] = mat.group(2)        
            
    output.close()
    return res

def browse_bonjour_service(serv_type):
    """
    Browsing for _airplay._tcp
    Timestamp     A/R Flags if Domain                    Service Type              Instance Name
    16:39:48.346  Add     3 13 local.                    _airplay._tcp.            t5
    16:39:48.346  Add     3 13 local.                    _airplay._tcp.            t6

    output:
    [{'name': 't5', 'type': '_airplay._tcp.'},
    {'name': 't6', 'type': '_airplay._tcp.'}]
    
    ---ye.songnan
    """
    cmd = "dns-sd -B %s > bonjour_records.txt" % serv_type
    p = subprocess.Popen(cmd,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)

    time.sleep(10)
    #kill_pid(p.pid)
    kill_proc("dns-sd")
    #subprocess.call(r'c:\bin\win\pskill -t %s' % str(p.pid))
    time.sleep(2)
    
    bonjour_record_list = []
    pattern = re.compile(r'(.*)\s+(Add|Rmv)\s+(\d+)\s+(\d*)\s*(local\.)\s+(_.*\._tcp\.)\s+(.*)')
    with open("bonjour_records.txt") as fp:
        for line in fp:
            m = pattern.match(line)
            if m:
                bonjour_item = dict(type=m.group(6), name=m.group(7).strip())
                #bonjour_item = dict(type=m.group(2), name=m.group(3))
                bonjour_record_list.append(bonjour_item)
                
    return bonjour_record_list                   
    
def register_bonjour_service(serv_name, serv_type, port):
    """
    Use this function to register a bonjour service ,and return PID.
    
    ---ye.songnan
    """
    cmd = "dns-sd -R %s %s . %s" % (serv_name, serv_type, port)
    p = subprocess.Popen(cmd,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
#    pid = p.pid 
    
#    return pid

def kill_proc(proc_name):
    """
    Use this function to kill subprocess's process by process name.
    
    ---ye.songnan
    """
#    subprocess.Popen(r'c:\bin\win\pskill -t %s' % proc_name, shell=True, stdout=subprocess.PIPE)
    output = os.popen(r'c:\bin\win\pskill -t %s' % proc_name)
    return output.read()
def connect_to_server_port(server_ip,port):
    """
    To test if station could connect to the server's port.
    """
    result = 'successful'
    try:
        print 'Trying to connect to %s on port %s'%(server_ip,port)
        #Need to try many times, because not all packets will be inspected by AP.
        #This is the application visibility limitation.
        if int(port) == 80:
            import urllib
            urllib.urlopen(r"http://%s"%server_ip)
        else:
            i = 0
            while i<100:
                i += 1
                sta_socket = None
                sta_socket=socket.socket()
                sta_socket.connect((server_ip,int(port)))
                time.sleep(.2)
        print 'Connecting succeeded!'
    except Exception, e:
        result = 'Connecting to %s on port %s failed!%s'%(server_ip,port,e.message)
        print result
    finally:
        if int(port) == 80:return result
        print 'Deleting socket instance!'
        if sta_socket:
            del sta_socket
        return result

#@author: yin.wenling zf-7875   
#def ping6(target_ip, timeout_ms = 1000, echo_count = 2, echo_timeout = 10, pause = 0.05):
#    pattarn = "(^(([0-9A-Fa-f]{1,4}:){7}(([0-9A-Fa-f]{1,4})|:))|(([0-9A-Fa-f]{1,4}:){6}(:|(:[0-9A-Fa-f]{1,4})))|(([0-9A-Fa-f]{1,4}:){5}(:|(:[0-9A-Fa-f]{1,4}){1,2}))|(([0-9A-Fa-f]{1,4}:){4}(:|(:[0-9A-Fa-f]{1,4}){1,3}))|(([0-9A-Fa-f]{1,4}:){3}(:|(:[0-9A-Fa-f]{1,4}){1,4}))|(([0-9A-Fa-f]{1,4}:){2}(:|(:[0-9A-Fa-f]{1,4}){1,5}))|(([0-9A-Fa-f]{1,4}:){1}(:|(:[0-9A-Fa-f]{1,4}){1,6}))|(:(:|(:[0-9A-Fa-f]{1,4}){1,7}))$)"
#    m = re.match(pattarn,target_ip)
#    if m is not None:
#        cmd_line = "ping %s -n %s -w %s" % (target_ip, str(echo_count), str(echo_timeout))
#    else:
#        cmd_line = "ping -6 %s -n %s -w %s" % (target_ip, str(echo_count), str(echo_timeout))
#    
#    ofmt = r"Packets:\s*sent\s*=\s*(\d+),\s*received\s*=\s*(\d+),\s+lost\s*=\s*(\d+)\s*\((\d+)%\s*loss\)"
#    good_reply_list = [r"reply\s+from\s+[0-9.]+:\s*bytes=\d+.*TTL=\d+",
#                       r"reply\s+from\s+[0-9a-f:]+:\s*time[=,<]\d+ms"]
#    
#    timeout_s = timeout_ms / 1000.0
#    start_time = time.time()
#    current_time = start_time
#    while current_time - start_time < timeout_s:
#        data = _exec_program(cmd_line)
#        current_time = time.time()
#        m = re.search(ofmt, data, re.M | re.I)
#        if m and int(m.group(4)) == 0:
#            for ptn in good_reply_list:
#                if re.search(ptn, data, re.I):                    
#                    return "%.1f" % (current_time - start_time)
#        time.sleep(int(pause))
#    return "Timeout exceeded (%.1f seconds)" % timeout_s

class RatToolAgentHandler(StreamRequestHandler):
    """
    This class implements the command dispatcher. Its main duty is to receive commands from the client,
    execute them and return the result
    """
    def handle(self):
        print "Serving the client from " + str(self.client_address) + "\n"

        self.wfile.write("ok;;Welcome to RAT Tool Agent\r\n")

        cmd_pattern = '([a-zA-Z0-9_.]+);(.*)'

        while True:
            time.sleep(1)
            try:
                data = self.rfile.readline().strip()
                if len(data) == 0: continue
                print "---> Received command: %s" % data

                obj = re.match(cmd_pattern, data)
                if obj:
                    cmd = obj.group(1)
                    param_str = obj.group(2).strip()
                else:
                    raise Exception("Invalid format")

                param_obj = {}
                if param_str:                    
                    param_obj = eval(param_str)

                if cmd == "quit":
                    self.wfile.write("ok;;bye bye !!!\r\n")
                    break

                res = None

                #### This is a hack!!! ####
                # 'perform_web_auth'. 'perform_guest_auth' and perform_hotspot_auth
                # are newly revised and they do not accept kwa as arguments
                # When all methods are modified, we will only use:
                #     exec("res = %(cmd)s(param_obj)" % locals())

                if cmd in ('perform_web_auth', 'perform_guest_auth', 'perform_hotspot_auth',
                           ):
                    exec("res = %(cmd)s(param_obj)" % locals())

                else:
                    exec("res = %(cmd)s(**param_obj)" % locals())

                print "---> Result: %s\n" % str(res)
                self.wfile.write("ok;;%s\r\n" % str(res))

            except Exception, e:
                emsg = '\n%s\n%s\n%s' % ('-- Traceback ' + '-' * 60,
                                         traceback.format_exc(),
                                         '-- Traceback End ' + '-' * (60 - 4))
                #print emsg # uncomment me for debugging
                try:
                    self.wfile.write("error;;%s;;%s\r\n" % (e.message, emsg))

                except Exception, ex:
                    print "ERROR: %s" % ex.message
                    break
        
        global browser_agent
        global is_browser_started
        if 'browser_agent' in globals():
            try:        
                if browser_agent and browser_agent.browsers:
                        for browser_id in browser_agent.browsers.keys():
                            if browser_agent.browsers[browser_id]:
                                 close_browser(browser_id)                             
                print "all of the browser are closed completly!"
            except Exception, e:
                    print e.message
        if 'is_browser_started' in globals(): 
            is_browser_started = False
        
        print "Closed the connection\n"

def get_cmd_output_as_list(cmd,_debug=False):
    if _debug: pdb.set_trace()
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    if '\r\n\t' in output: output = output.replace('\r\n\t','\r\n')
    if '\r\r\n' in output: output = output.replace('\r\r\n','\r\n')
    output = output.split('\r\n')
    return output

def get_adapter_name_and_desc():
    try:
        output = get_cmd_output_as_list('ipconfig -all')
        adapter_name = ''
        adapter_desc = ''
        found = False
        adapter_name_list = []
        adapter_desc_list = []
        for line in output:
            if 'adapter Wireless' in line: 
                adapter_name_list.append(line)
                found = True
            if found and 'Description' in line:
                adapter_desc_list.append(line)
                found = False
        adapter_num = len(adapter_name_list)
        if adapter_num > 1:
            for adapter in adapter_name_list: print adapter
            raise Exception("%s wireless adapters found, please only enable one!" % adapter_num)
        if adapter_num:
            adapter_name = adapter_name_list[0].split('adapter ')[1].split(':')[0]
            adapter_desc = adapter_desc_list[0].split(': ')[1]

        return adapter_name,adapter_desc
    except Exception, e:
        print e.message
        return '',''

def get_adapter_guid(adapter_desc,_debug=False):

    try:
        if _debug: pdb.set_trace()
        output = get_cmd_output_as_list('wlanman.exe ei')
        buffer = "".join([line+' ' for line in output])

        if '(' in adapter_desc: adapter_desc = adapter_desc.replace('(','\(')
        if ')' in adapter_desc: adapter_desc = adapter_desc.replace(')','\)')

        desc_list=[]
        desc_list.append(adapter_desc)
        
        while 1:
            res = adapter_desc.find(' ')
            if  res != -1:
                desc_list.append(adapter_desc[res+1:])
                adapter_desc = adapter_desc[res+1:]
            else: break

        for desc in desc_list:
            pattern = r"Interface\s*\d+:\s*GUID:\s*([\da-fA-F-]+).*"
            pattern += desc
            obj = re.search(pattern, buffer)
            if obj: break

        if not obj:
            raise Exception("Unable to get GUID of the wireless adapter: %s" % buffer)
        adapter_guid = obj.group(1)
        return adapter_guid
    except Exception, e:
        print e.message
        return ''
    
def get_adapter_vid(adapter_name,_debug=False):
    try:
        if _debug: pdb.set_trace()
        adapter_vid = ''
        output = get_cmd_output_as_list('devcon.exe find *')
        for line in output:
            if adapter_name in line and (line.startswith('USB') or line.startswith('PCI')):
                adapter_vid = line.split(':')[0]
                break

        pattern = r'.+\\[0-9]'
        m = re.search(pattern,adapter_vid)
        if m : 
            adapter_vid = m.group(0)
            adapter_vid = adapter_vid[:len(adapter_vid)-2]
        adapter_vid = adapter_vid.replace('&','*')
    
        output1 = os.popen('devcon.exe find %s'%adapter_vid)
        buffer1 = "".join(line for line in output1)
        output1.close()
        if '1 matching' in buffer1: return adapter_vid
        else: return ''
    except Exception, e:
        print e.message
        return ''

if __name__ == "__main__":
    _adapter_name, _adapter_desc = get_adapter_name_and_desc()
    if not _adapter_name or not _adapter_desc:
        err_info = 'Fail to get :'
        if not _adapter_name: err_info += ' Adapter name'
        if not _adapter_desc: err_info += ' Adapter desc'
        print err_info
        os.system('PAUSE')
        sys.exit(0)
    _adapter_guid = get_adapter_guid(_adapter_desc)
    _adapter_vid  = get_adapter_vid(_adapter_desc)
    if not _adapter_guid or not _adapter_vid:
        err_info = 'Fail to get :'
        if not _adapter_guid: err_info += ' Adapter guid'
        if not _adapter_vid: err_info += ' Adapter vid'
        print err_info
        os.system('PAUSE')
        sys.exit(0)
    print 'Starting RatToolAgent with the following info:\n'
    print 'Adapter name: %s'%(_adapter_name)
    print 'Adapter desc: %s'%(_adapter_desc)
    print 'Adapter guid: %s'%(_adapter_guid)
    print 'Adapter vid : %s\n'%(_adapter_vid)
    try:
        server = TCPServer(("", _service_port), RatToolAgentHandler)
        print "RAT Tool Agent is listening on port %d ..." % _service_port
        server.serve_forever()
    except Exception, e:
        print "Error occurred!Please check!"
        print e.message
        os.system('PAUSE')
        sys.exit(0)

