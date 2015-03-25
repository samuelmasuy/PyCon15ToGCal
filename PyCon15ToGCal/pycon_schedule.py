# -*- coding: utf-8 -*-
"""
PyCon Schedule
--------------

Command line application to port PyCon talks and keynotes events to
Google calendar.

.. code::

    usage: pycon_schedule.py [-h] [-c CALENDAR] [-a] clientid clientsecret

    Port PyCon talks and keynotes to Google calendar.

    positional arguments:
      clientid         Get your client ID from Google developer console.
      clientsecret     Get your client secret from Google developer console.

    optional arguments:
      -h, --help       show this help message and exit
      -c CALENDAR, --calendar CALENDAR
                       Name of the secondary calendar you would like to port
                       the event to. If you would like it to be your primary
                       calendar, insert `primary`. (Default: `PyCon15`)
      -a, --all        Add all the events to your google calendar. The
                       default is to provide an interface to select talks and
                       keynotes. (Pick one talk per session.)

:copyright: (c) 2015 by Samuel Masuy.
:license: GNU version 2.0, see LICENSE for more details.
"""
import argparse
import itertools

import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import pprint

from pycon_parser import parse
from pycon_pick import pick_events


def create_service(http):
    """
    Create a Google calendar service using API V3.

    :param http: *Authentication and Authorization* for Google calendar.
    :return: A Resource object with methods for interacting with the service.
    :note: Takes ``HTTP`` as a global variable, it is generated at runtime
           using :func:`authentication_authorization`.
    """
    return build(serviceName='calendar', version='v3', http=http)


def authentication_authorization(client_id, client_secret):
    """
    Allow the application to authenticate itself as an application belonging
    to Google Developers Console project.

    :param str client_id: Identification of the application
    :param str client_secret: Identification of the application
    :return: ``httplib2.Http``, An instance of httplib2.Http
    """
    flow = OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/calendar')

    storage = Storage('calendar.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    http = httplib2.Http()
    return credentials.authorize(http)



def cal_lookup_id(service, name_of_calendar):
    """
    Finds the id, if existent, of a specific calendar.

    :param service: A Resource object with methods for interacting with the service.
    :param str name_of_calendar: Literal name of calendar
    :return: calendar ID, if ``name_of_calendar`` was found, ``None`` otherwise
    """
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == name_of_calendar:
            return calendar_list_entry['id']
    return None


def insert_calendar(service, name_of_calendar):
    """
    Insert a secondary calendar in the user's calendar repository.

    :param service: A Resource object with methods for interacting with the service.
    :param str name_of_calendar: Name of calendar to be inserted.
    :return: The calendar ID of the calendar that was created.
    """
    calendar = {
        'summary': name_of_calendar,
        'timeZone': 'America/Montreal'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']


def insert_event(http, url, name_of_calendar, add_all=False):
    """
    Insert events in the user calendar
    This function will create a secondary calendar if ``name_of_calendar``
    does not match any calendar in the user's Google calendar.

    :param http: *Authentication and Authorization* for Google calendar.
    :param str url: URL to be parsed.
    :param name_of_calendar: The name of the calendar in which events
                             should be inserted.
    :param bool add_all: Add all events at once or pick them one by one.
    :return: A tuple containing the calendar ID, and the event ID that
             were just created.
    """
    service = create_service(http)

    events = parse(url)

    if not add_all:
        events = pick_events([list(g) for _, g in itertools.groupby(events,
                                                                    lambda k: k['time_start'])])
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(events)

    print "\n===================================================="
    print "Please wait while we upload the events to calendar..."

    gcal_events = to_gcal(events)

    calendar_id = cal_lookup_id(service, name_of_calendar)

    if calendar_id is None:
        calendar_id = insert_calendar(service, name_of_calendar)
    # Create all the events and get their ids.
    created_events_id = [service.events().insert(calendarId=calendar_id,
                                                 body=event).execute()['id']
                         for event in gcal_events]

    return calendar_id, created_events_id


def to_gcal(events):
    """
    This function takes all the data parsed and returns a dictionary
    with all formated data needed to transmit to Google calendar.

    :param list events: A list of events.
    :return: A list of events specifically formatted for Google calendar.
    """
    gcal = []
    for event in events:
        entry = dict()
        entry['summary'] = event['title'] + ' in ' + event['track'] + ' by ' + event['speaker']
        entry['description'] = event['description']
        entry['location'] = u'201 Avenue Viger Ouest, Montréal, QC H2Z 1X7, Canada'
        start_dic = dict()
        entry['start'] = start_dic
        start_dic['dateTime'] = event['time_start'].isoformat()
        start_dic['timeZone'] = 'America/Montreal'
        end_dic = dict()
        entry['end'] = end_dic
        end_dic['dateTime'] = event['time_end'].isoformat()
        end_dic['timeZone'] = 'America/Montreal'
        gcal.append(entry)
    return gcal

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Port PyCon talks and keynotes to Google calendar.')
    parser.add_argument('-c', '--calendar', dest='calendar', default='PyCon15',
                        help='Name of the secondary calendar you would like to \
        port the event to. If you would like it to be your primary calendar, \
        insert `primary`. (Default: `PyCon15`)')
    parser.add_argument('clientid',
                        help='Get your client ID from Google developer console.')
    parser.add_argument('clientsecret',
                        help='Get your client secret from Google developer console.')
    parser.add_argument('-a', '--all', dest='add_all', action='store_true',
                        help='Add all the events to your google calendar. The \
        default is to provide an interface to select talks and keynotes. \
        (Pick one talk per session.)')
    parser.set_defaults(add_all=False)
    args = parser.parse_args()

    url = 'https://us.pycon.org/2015/schedule/talks/'
    http = authentication_authorization(args.clientid, args.clientsecret)
    calendar_id, _ = insert_event(http, url, args.calendar, add_all=args.add_all)
    print "\n====================================================\n"
    print "All the events have been added to: {0}".format(calendar_id)
    print "You can check you calendar at: https://www.google.com/calendar/render"
