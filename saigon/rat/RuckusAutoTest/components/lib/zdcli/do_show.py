"""
@copyright: Ruckus Wireless Inc.
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: Nov 2012

This module includes the functions to support the show command in the privileges mode:
show
  aaa                  Contains commands that can be executed from within the context.
  dhcp                 Contains commands that can be executed from within the context.
  ap                   Contains commands that can be executed from within the context.
  ap-group             Contains commands that can be executed from within the context.
  ap-policy            Displays the ap policy settings.
  config               Displays current system options.
  performance          Displays AP or station performance.
  sysinfo              Displays current system status.
  techsupport          Displays current system options and status.
  mgmt-acl             Contains commands that can be executed from within the context.
  mgmt-acl-ipv6        Contains commands that can be executed from within the context.
  static-route         Contains commands that can be executed from within the context.
  static-route-ipv6    Contains commands that can be executed from within the context.
  wlan                 Contains commands that can be executed from within the context.
  wlan-group           Contains commands that can be executed from within the context.
  l2acl                Contains commands that can be executed from within the context.
  l3acl                Contains commands that can be executed from within the context.
  l3acl-ipv6           Contains commands that can be executed from within the context.
  hotspot              Contains commands that can be executed from within the context.
  hs20op               Contains commands that can be executed from within the context.
  hs20sp               Contains commands that can be executed from within the context.
  role                 Contains commands that can be executed from within the context.
  user                 Contains commands that can be executed from within the context.
  current-active-clients
                       Contains commands that can be executed from within the context.
  mesh                 Contains commands that can be executed from within the context.
  dynamic-psks         Displays generated dynamic PSK.
  dynamic-certs        Displays generated dynamic Certs.
  guest-passes         Displays generated guest passes.
  rogue-devices        Displays all rogue devices.
  events-activities    Displays last 300 events/activities information.
  alarm                Displays last 300 alarm information.
  license              Displays license.
  session-timeout      Displays CLI session timeout interval.
  active-wired-client  Displays a list of active wired clients.
"""

from RuckusAutoTest.components.lib.zdcli import output_as_dict

#=============================================#
#             Public functions        
#=============================================#

def show_events_activities(zdcli):
    """
    Return the result of command "show events-activities"
        events-activities    Displays last 300 events/activities information.
    """
    top_key = 'Last 300 Events/Activities'
    act_key = 'Activity'
    info = _show_events_activities(zdcli)
    activities = info[top_key][act_key]
    
    return activities 

#=============================================#
#             Private functions        
#=============================================#

def _show_events_activities(zdcli):
    cmd = 'events-activities'
    res = zdcli.do_show(cmd)
    info = output_as_dict.parse(res)
    
    return info




