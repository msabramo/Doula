import datetime
from doula.util import comparable_name


def clean(text):
    return comparable_name(text)


def get_status_class(status):
    return get_class('status', status)


def get_stat_class(status):
    return get_class('stat', status)


def get_class(prefix, status):
    if status == 'deployed':
        return prefix + '-deployed'
    elif status == 'tagged':
        return prefix + '-tagged'
    elif status == 'uncommitted_changes':
        return prefix + '-error'
    elif status == 'unknown':
        return prefix + '-unknown'
    else:
        return prefix + '-changed'


def format_datetime(date):
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    hour = int(date[8:10])
    minute = int(date[10:12])
    second = int(date[12:14])

    d = datetime.datetime(year, month, day, hour, minute, second)
    format = '%m/%d/%Y %I:%M %p'
    return d.strftime(format)


def format_isodate(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like May 05, 2012 04:30 PM
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%B %d, %Y %I:%M %p')


def format_isodate_date(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like May 05, 2012
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%B %d, %Y')


def format_isodate_time(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like 04:30 PM
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%I:%M %p')


def get_pretty_status(status):
    """
    Return a print friendly status
    """
    statuses = {
        'tagged': 'Tagged',
        'deployed': 'Deployed',
        'change_to_config': 'Changes to Configuration',
        'change_to_app': 'Changes to Service Environment',
        'change_to_app_and_config': 'Changes to Configuration and Service Environment',
        'uncommitted_changes': 'Uncommitted Changes'
    }

    if status in statuses:
        return statuses[status]
    else:
        return 'Unknown'
