"""
Test troubleshooting on Zone Director Web UI using ping and trace route tools.  
"""
import time, re, logging, pdb

def select_ping_traceroute_window(zd):
    current_windows_list = zd.s.get_all_window_titles()
    for window in current_windows_list: 
        if "Network Connectivity" in window: 
            zd.s.select_window(window)
            return True
    return False

def close_ping_traceroute_windows(zd):
    current_windows_list = zd.s.get_all_window_titles()
    for window in current_windows_list: 
        if "Network Connectivity" in window: 
            zd.s.close()
            
    # select back to default window 
    zd.s.select_window(current_windows_list[0])

    
def get_current_ip_addr(zd):
    select_ping_traceroute_window(zd)
    return zd.s.get_value(locators['ip_addr_textbox'])

def perform_ping_test(zd, ip_addr = '', timeout = 30):
    select_ping_traceroute_window(zd)
    if ip_addr: 
        zd.s.type_text(locators['ip_addr_textbox'], ip_addr)

    zd.s.click_and_wait(locators['ping_btn'])
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        raise Exception(_alert)

    time.sleep(timeout)
    raw_result = zd.s.get_value(locators['result_box'])
    logging.info("Ping Result: %s" % raw_result)
    result = _parse_ping_result(raw_result)
    return result

def perform_traceroute_test(zd, ip_addr = '', timeout = 30):
    select_ping_traceroute_window(zd)
    if ip_addr: 
        zd.s.type_text(locators['ip_addr_textbox'], ip_addr)

    zd.s.click_and_wait(locators['traceroute_btn'])

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        raise Exception(_alert)

    raw_result = zd.s.get_value(locators['result_box'])
    logging.info("Trace Route Result: %s" % raw_result)
    result = _parse_trace_route_result(raw_result)
    return result

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locators = dict(
    ip_addr_textbox = "//input[@id='ip']",
    ping_btn = "//input[@id='ping']",
    traceroute_btn = "//input[@id='traceroute']",
    result_box = "//textarea[@id='result']",
)

def _parse_ping_result(data):
    ofmt = r".*(\d+) packets transmitted, (\d+) packets received, (\d+)% packet loss.*"
    goodreply = r".*(\d+) bytes\s+from\s+[0-9.]+:\s*icmp_seq=(\d+).*ttl=(\d+).*time=(\d+.\d+).*ms.*"
    m = re.search(ofmt, data, re.M|re.I)
    
    if m and int(m.group(3)) == 0:
        m = re.search(goodreply, data, re.I)
        if m:
            return "%s" % (m.group(4))

    if m and int(m.group(3)) > 0: 
        return "Timeout exceeded (%d\% packets loss)" % m.group(3)
    
    return "Timeout or unknown format result" 

def _parse_trace_route_result(data):
    goodreply = r".*[0-9]\s+[0-9.]+ \([0-9.]+\)\s+[\d+.\d+\s+ms]{3}.*"
    m = re.search(goodreply, data, re.M|re.I)
    
    if m:
        return "%s" % (m.group())
    else:
        return "Timeout or no route to host"
