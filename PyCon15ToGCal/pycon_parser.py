# -*- coding: utf-8 -*-
"""
PyCon Parser
------------

Parse the schedule of talks given at PyCon15.

:copyright: (c) 2015 by Samuel Masuy.
:license: GNU version 2.0, see LICENSE for more details.
"""
from datetime import datetime

from lxml import html
import requests


def parse(url):
    """
    Parse the schedule of PyCon talks.

    :param str url: The url of all the events.
    :return: A list of all PyCon talks events.
    """
    tree = make_tree(url)

    pycon_events = []

    pycon_days = tree.xpath("//table")[-3:]

    for table in pycon_days:
        date = table.getprevious().text
        thead, tbody = table.getchildren()
        rows = thead.iterchildren()
        headers = [col.text for col in next(rows) if col.text.startswith('Room')]

        tbody_rows = tbody.getchildren()

        event_times = [row.getchildren()[0].text for row in tbody_rows]

        for talk_time, row in enumerate(tbody_rows):
            talks = row.getchildren()[1:]
            # time_slot = []
            for talk_index, talk in enumerate(talks):
                if 'class' not in talk.attrib:
                    continue
                if talk.attrib['rowspan'] == '1':
                    end_time = event_times[talk_time + 1]
                elif talk.attrib['rowspan'] == '2':
                    end_time = event_times[talk_time + 2]

                start_datetime, end_datetime = get_event_time(date,
                                                              event_times[talk_time],
                                                              end_time)

                if talk.attrib['class'] == 'slot slot-lightning':
                    title = talk.text.strip()
                    speaker = ''
                    track = ''
                    if ' - ' in title:
                        split_title = title.split(' - ')
                        if len(split_title) > 2:
                            speaker = split_title[1]
                        else:
                            speaker = ''
                        track = split_title[-1]
                        title = split_title[0]
                    pycon_events.append(create_event(title, '',
                                                     start_datetime, end_datetime,
                                                     speaker, track))
                elif talk.attrib['class'] == 'slot slot-talk':
                    title = talk.xpath("span[@class='title']")[0].getchildren()[0]
                    description = title.attrib['title'].replace('\n', '')
                    title = title.text
                    speaker = talk.xpath("span[@class='speaker']")[0].text.strip()
                    pycon_events.append(create_event(title, description,
                                                     start_datetime, end_datetime,
                                                     speaker, headers[talk_index]))
            # if time_slot:
            #     pycon_events.append(time_slot)
    return pycon_events


def get_event_time(date, start_time, end_time):
    """
    Get both start and ending time for a talk.
    """
    start_date_time = convert_to_datetime(date, start_time)
    end_date_time = convert_to_datetime(date, end_time)
    return start_date_time, end_date_time


def convert_to_datetime(date_event, time_event):
    """
    Convert date and time ``datetime.datetime``.

    :param str date_event: Date of the event. Format: `January 01, 2000`
    :param str time_event: Time of the event. Format: `01:00PM`
    :return: ``datetime.datetime``.
    :rtype: str
    """
    return datetime.strptime(
        (date_event + time_event), '%B %d, %Y%I:%M%p')


def create_event(title, description, start_datetime, end_datetime,
                 speaker, track):
    """
    Create an event.

    :param str title: Title of the talk.
    :param str description: Description of the talk.
    :param str start_datetime: Start of the talk, must of type
                               ``datetime.datetime``
    :param str end_datetime: End of the talk, must of type
                               ``datetime.datetime``
    :param str speaker: The speaker who is giving the talk.
    :param track: Room in which the talk is given.
    :return: An event.
    :rtype: dict
    """
    return {'title': title,
            'description': description,
            'time_start': start_datetime,
            'time_end': end_datetime,
            'speaker': speaker,
            'track': track}


def make_tree(url):
    """
    Create a lxml tree from a url.

    :param str url: The URL of all the events.
    :return: A ``lxml.tree``
    """
    response = requests.get(url, verify=False).text
    tree = html.fromstring(response)
    return tree
