"""
This module includes the library to collect the zone director logging with events, activities, alarms 
by access the pages Monitor->All Events/Activities and Monitor->All Alarms
"""

import logging
import time

LOCATOR_MONITOR = {
    # Monitor -> All Events/Activities
    'loc_mon_all_events_activities_span': r"//span[@id='monitor_events']",

    'loc_mon_allevents_clear_all_button': r"//input[@id='clearall-allevent']",
    'loc_mon_allevents_showmore_button': r"//input[@id='showmore-allevent']",
    'loc_mon_allevents_row': r"//table[@id='allevent']//tr[@idx='$_$']",
    'loc_mon_allevents_time_cell': r"//table[@id='allevent']//tr[@idx='$_$']/td[1]",
    'loc_mon_allevents_severity_cell': r"//table[@id='allevent']//tr[@idx='$_$']/td[2]",
    'loc_mon_allevents_user_cell': r"//table[@id='allevent']//tr[@idx='$_$']/td[3]",
    'loc_mon_allevents_activities_cell': r"//table[@id='allevent']//tr[@idx='$_$']/td[4]",
    'loc_mon_allevents_next_img': r"//img[@id='next-allevent']",

    }


def nav_to(zd):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_ALL_EVENTS_ACTIVITIES)
    time.sleep(3)



#
# PUBLIC FUNCTIONS
#

def get_events(zd, **kwargs):
    """
    Return the list of events/activities in the pages Monitor->All Events/Activities. 
    Each of events is presents as a dictionary as {'time': '', 'severity': '', 'user': '', 'activities': ''}
    """
    cfg = {'num_of_events': 100}
    cfg.update(kwargs)
    
    return _get_events(zd, cfg['num_of_events'])
    
#
# PRIVATE FUNCTIONS
#

def _get_events(zd, num_of_events = 100):
    """
    Return the list of events/activities in the pages Monitor->All Events/Activities. 
    Each of events is presents as a dictionary as {'time': '', 'severity': '', 'user': '', 'activities': ''}
    
    If num_of_events = 0 then get all the events else return the latest number of events; default is 100 latest events
    """
    locs = LOCATOR_MONITOR
     
    msg = 'Get %s events' % ('all' if num_of_events == 0 else 'first %s' % num_of_events)
    logging.info(msg)
    # go to the  Monitor->All Events/Activities page
    nav_to(zd)
    show_more_button = locs['loc_mon_allevents_showmore_button']
    next_button = locs['loc_mon_allevents_next_img']
     
    # click the show more button to view all max of events in the page
    
    while zd.s.is_element_present(show_more_button) and zd.s.is_visible(show_more_button):
        zd.s.click_and_wait(show_more_button, 3)
        
    # get the events base on the expected pages
    events = []
    row_idx = 0
    while True:
        if num_of_events and row_idx == num_of_events:
            break
        
        event_row = locs['loc_mon_allevents_row']
        event_row = event_row.replace("$_$", str(row_idx))
        is_event_exist = zd.s.is_element_present(event_row)
        
        if not is_event_exist:
            if zd.s.get_attribute("%s@class" % locs['loc_mon_allevents_next_img']) == 'ib':
                zd.s.click_and_wait(locs['loc_mon_allevents_next_img'], 3)                        
            else:
                break
        event = {}
        
        time_event = locs['loc_mon_allevents_time_cell']
        time_event = time_event.replace("$_$", str(row_idx))
        time_event = zd.s.get_text(time_event)
        event['time'] = time_event
        
        severity = locs['loc_mon_allevents_severity_cell']
        severity = severity.replace("$_$", str(row_idx))
        severity = zd.s.get_text(severity)
        event['severity'] = severity

        user = locs['loc_mon_allevents_user_cell']
        user = user.replace("$_$", str(row_idx))
        user = zd.s.get_text(user)
        event['user'] = user

        activities = locs['loc_mon_allevents_activities_cell']
        activities = activities.replace("$_$", str(row_idx))
        activities = zd.s.get_text(activities)
        event['activities'] = activities

        events.append(event)
        row_idx += 1
    
    return events