import os
import re
import sys
import time
import tempfile

from RuckusAutoTest.common import Ratutils as utils

# Define the location for the tools depending on where they are loaded
_wlantool_cmd = "wlanman.exe"
if not os.path.isfile(_wlantool_cmd):
    # This is when it is loaded on the station that holds the framework
    _wlantool_cmd = "rat\\common\\%s" % _wlantool_cmd

def _get_guid(adapter_name = ""):
    """
    Get GUID and friendly name (if not specified) of a wireless adapter
    Input:
    - adapter_name: Friendly name of the wireless adapter
    Output:
    - Guid: this value is used by other subcommands of the wireless tool
    - And friendly name: this value helps to identifiy an adapter in systems with multiple devices
    """
    cmd = "%s ei" % _wlantool_cmd
    output = os.popen(cmd)
    buffer = "".join(line for line in output)

    if adapter_name:
        name_pattern = adapter_name
    else:
        name_pattern = ".*"
    pattern = r"Interface [0-9]+:[\r\n\t]+GUID: ([0-9a-fA-F-]+)[\r\n\t]+HWID: [\\_&0-9a-zA-Z]+[\r\n\t]+Name: (%s)[\r\n]+" % name_pattern

    match = re.search(pattern, buffer)
    if not match:
        raise Exception("Unable to get information: %s" % buffer)

    return (match.group(1), match.group(2))

def _make_wlan_profile_xml(ssid, auth_method, encrypt_method, key_type = "", key_material = "", key_index = "", use_onex = False):
    """
    Use this function to generate a WLAN profile using WLANProfile schema
    Input:
    - ssid: a string represents the SSID
    - auth_method: one of the authentication methods including "open", "shared", "WPA", "WPAPSK",
                  "WPA2", and "WPA2PSK"
    - encrypt_method: one of the encryption methods including "none", "WEP", "TKIP" and "AES"
    - key_type: one of the key types including "passPhrase" or "networkKey"
    - key_index: WEP key index, can be 1, 2, 3 or 4
    - key_material: the key string
    - use_onex: True if the profile includes 802.1x authentication configuration, otherwise use False

    Output: path to the created XML file
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
    Input:
    - filename: name of the file
    - username: EAP credential
    - password: EAP credential
    Output: path to the created XML file
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
    - ssid: a string represents the SSID
    - auth_method: one of the authentication methods including "open", "shared", "WPA", "WPAPSK",
                  "WPA2", and "WPA2PSK"
    - encrypt_method: one of the encryption methods including "none", "WEP", "TKIP" and "AES"
    - key_type: one of the key types including "passPhrase" or "networkKey"
    - key_index: WEP key index, can be 1, 2, 3 or 4
    - key_material: the key string
    - use_onex: True if the profile includes 802.1x authentication configuration, otherwise use False
    - username: user credential
    - password:
    - adapter_name: Friendly name of the wireless adapter
    Output: none
    """

    # Obtain the IDs of the specified adapter
    guid, name = _get_guid(adapter_name)

    # Create the XML profile file with provided security setting
    profile_path = _make_wlan_profile_xml(ssid, auth_method, encrypt_method, key_type, key_material, key_index, use_onex)

    #Scan for wireless networks
    cmd = "%s scan %s" % (_wlantool_cmd, guid)
    os.popen(cmd)
    time.sleep(3)

    # Set the wireless profile
    cmd = "%s sp %s \"%s\"" % (_wlantool_cmd, guid, profile_path)
    output = os.popen(cmd)
    buffer = "".join(line for line in output)
    if buffer.find("completed successfully") == -1:
        raise Exception("Unable to set the security settings to the wireless adapter \"%s\"" % name)

    # Connect to the wireless network specified by the profile
    time.sleep(1)
    cmd = "%s conn %s %s i %s" % (_wlantool_cmd, guid, ssid, ssid)
    output = os.popen(cmd)
    buffer = "".join(line for line in output)
    if buffer.find("completed successfully") == -1:
        raise Exception("Unable to connect to the WLAN \"%s\" on the wireless adapter \"%s\"" % (ssid, name))

    # Set the user credential when .1x is used
    if use_onex:
        # Create the EAP user credential file
        user_credential_path = _make_user_credential_xml(username, password)

        # And pass to the wireless adapter
        cmd = "%s seuc %s %s \"%s\"" % (_wlantool_cmd, guid, ssid, user_credential_path)
        output = os.popen(cmd)
        buffer = "".join(line for line in output)
        if buffer.find("completed successfully") == -1:
            raise Exception("Unable to set the EAP user credential to the adapter \"%s\"" % name)

        time.sleep(0.5)

        # Connect to the wireless network specified by the profile
        cmd = "%s conn %s %s i %s" % (_wlantool_cmd, guid, ssid, ssid)
        output = os.popen(cmd)
        buffer = "".join(line for line in output)
        if buffer.find("completed successfully") == -1:
            raise Exception("Unable to connect to the WLAN \"%s\" on the wireless adapter \"%s\"" % (ssid, name))

def remove_all_wlan(adapter_name = ""):
    """
    Remove all the existing wireless profiles on a wireless adapter (if specified)
    or the first available one
    Input:
    - adapter_name: Friendly name of the wireless adapter
    Output: none
    """

    # Obtain the IDs of the specified adapter
    guid, name = _get_guid(adapter_name)

    # Get the list of the profiles created on the adapter
    cmd = "%s gpl %s" % (_wlantool_cmd, guid)
    pattern = '[\t ]+"([a-zA-Z0-9_-]+)"'
    profile_list = []
    output = os.popen(cmd)
    buffer = ""
    for line in output:
        match_obj = re.match(pattern, line)
        if match_obj:
            profile_list.append(match_obj.group(1))
        buffer += line
    if buffer.find("completed successfully") == -1:
        raise Exception("Unable to get list of profiles on the adapter \"%s\"" % name)

    # And remove them all
    for profile in profile_list:
        cmd = "%s dp %s %s" % (_wlantool_cmd, guid, profile)
        output = os.popen(cmd)
        buffer = "".join(line for line in output)
        if buffer.find("completed successfully") == -1:
            raise Exception("Unable to remove the profile %s from wireless adapter \"%s\"" % (profile, name))

def get_current_status(adapter_name = ""):
    """
    Obtain current connectivity status of the first wireless adapter on the system
    Input:
    - adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    Output: the string extracted from the output of the command wlanman.exe
    """
    # Obtain the IDs of the specified adapter
    guid, name = _get_guid(adapter_name)

    pattern = 'Interface state: "([a-z ]+)"'
    cmd = "%s qi %s" % (_wlantool_cmd, guid)
    output = os.popen(cmd)
    buffer = "".join(line for line in output)
    match_obj = re.search(pattern, buffer)
    if match_obj:
        return match_obj.group(1)
    raise Exception("Unable to get current status of wireless adapter \"%s\"" % name)

def get_addresses(adapter_name = ""):
    """
    Return MAC and IP address (if existed) of the specified wireless adapter (or the
    first one listed if not specified)
    Input:
    - adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    Output: a tupple of MAC and IP addresses
    """
    # Obtain the IDs of the specified adapter
    guid, name = _get_guid(adapter_name)

    output = os.popen("ipconfig /all")
    flag = False
    ip_addr = ""
    mac_addr = ""
    for line in output:
        line = line.lstrip().rstrip()
        if not line:
            if flag and (ip_addr or mac_addr): break
            continue
        if line.find(name) != -1:
            flag = True
        elif flag:
            x = line.split(':')
            tag = x[0].rstrip('. ')
            val = x[1].lstrip(' ')
            if tag in ["IP Address", "IPv4 Address"]:
                ip_addr = val.split("(Preferred)")[0]
            elif tag == "Physical Address":
                mac_addr = val
    return (ip_addr, mac_addr)

def check_ssid(ssid, adapter_name = ""):
    """
    Check if SSID is broadcasted on the air
    Input:
    - ssid: SSID of the WLAN needs to be verified
    - adapter_name: Name of the adapter in friendly format (e.g: Wireless Network Connection, ..."
    Output: the SSID itself it is found, otherwise return ""
    """
    # Obtain the IDs of the specified adapter
    guid, name = _get_guid(adapter_name)

    buffer = "".join(line for line in os.popen("%s gvl %s" % (_wlantool_cmd, guid)))
    if buffer.find("completed successfully") == -1:
        raise Exception("Unable to get list of visible WLANs on wireless adapter \"%s\"" % name)
    pattern = "SSID: (%s)[\\r\\n]" % ssid
    match_obj = re.search(pattern, buffer)
    if match_obj:
        return match_obj.group(1)
    return ""

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise Exception("Not enough parameter")
        if sys.argv[1] == "removeallwlan":
            remove_all_wlan()
            print "\n[[removeallwlan][DONE]]\n"
            exit()
        if sys.argv[1] == "configwlan":
            if len(sys.argv) < 3:
                raise Exception("Not enough parameter to perform subcommand 'configwlan'")
            param = eval(sys.argv[2])
            set_wlan_profile(**param)
            print "\n[[configwlan][DONE]]\n"
            exit()
        if sys.argv[1] == "ping":
            if len(sys.argv) < 3:
                raise Exception("Not enough parameter to perform subcommand 'ping'")
            param = eval(sys.argv[2])
            print "\n[[ping][%s]]\n" % utils.ping(**param)
            exit()
        if sys.argv[1] == "getstatus":
            print "\n[[getstatus][%s]]\n" % get_current_status()
            exit()
        if sys.argv[1] == "getaddresses":
            ip, mac = get_addresses()
            print "\n[[getaddresses][%s,%s]]" % (ip, mac.replace('-', ':'))
            exit()
        if sys.argv[1] == "checkssid":
            if len(sys.argv) < 3:
                raise Exception("Not enough parameter to perform subcommand 'checkssid'")
            param = eval(sys.argv[2])
            print "\n[[checkssid][%s]]\n" % check_ssid(**param)
            exit()
    except Exception, e:
        print "\n[[ERROR][%s]]\n" % e.message

