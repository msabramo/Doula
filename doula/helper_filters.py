from datetime import datetime
from doula.config import Config
from doula.util import comparable_name
from doula.util import dumps
from doula.util import remove_timezone
import math
import markdown
import os


def stringify(obj):
    return dumps(obj)


def version_number_to_git_tag(version):
    """
    Convert a version number to a git tag
    Git tags use underscores, while our version numbers sometimes use dashes.
    A typical version number is like so: [version number]-[git branch]
    Ex.
    2.6.93-server-throttling -> 2.6.93-server_throttling
    """
    version_list = version.split('-')
    version_number = version_list.pop(0)
    branch_name = ''

    for part in version_list:
        branch_name += part + '_'

    if branch_name:
        return version_number + '-' + branch_name.rstrip('_')
    else:
        return version_number


def formatted_github_day_and_time(date):
    """
    Returns a friendly date in the format: July 10, 2012 12:05 PM
    date - a github formatted date as a string (ex. "2012-05-08 14:15:31")
    """
    if not date:
        return date

    datetime_only = remove_timezone(date)
    datetime_only = datetime_only.replace(' ', 'T', 1).strip()

    dt = datetime.strptime(datetime_only, "%Y-%m-%dT%X")
    return dt.strftime("%B %d, %Y %I:%M %p")


def formatted_github_day(date):
    """
    Returns a friendly date in the format: July 10, 2012
    date - a github formatted date as a string (ex. "2012-05-08 14:15:31")
    """
    datetime_only = remove_timezone(date)
    datetime_only = datetime_only.replace(' ', 'T', 1).strip()

    dt = datetime.strptime(datetime_only, "%Y-%m-%dT%X")
    return dt.strftime("%B %d, %Y")


def formatted_day(date):
    """
    Returns a friendly date in the format: July 10, 2012
    date - a date formatted as a string (ex. "2012-02-15T10:12:01+02:00")
    """
    datetime_only = remove_timezone(date)
    dt = datetime.strptime(datetime_only, "%Y-%m-%dT%X")
    return dt.strftime("%B %d, %Y")


def relative_datetime_from_epoch_time(epoch_time):
    """
    Bring back relative_datetime using the epoch_time
    """
    timestamp = datetime.fromtimestamp(epoch_time)
    formatted_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
    return relative_datetime(formatted_timestamp)


def relative_datetime(date):
    """
    Brings back a friendly date time.

    For example dates returned will be:
        Yesterday at noon
        Today at 3:18pm
        2 days ago at 10:02 AM.

    date - a date formatted as a string (ex. "2012-02-15T10:12:01+02:00")
    """
    if not date:
        return ''

    datetime_only = remove_timezone(date)
    dt = datetime.strptime(datetime_only, "%Y-%m-%dT%X")
    delta = datetime.now() - dt

    if delta.days < 1:
        date_only = datetime.strptime(datetime_only.split('T')[0], "%Y-%m-%d")

        today_datetime_only = datetime.now().isoformat().split('T')[0]
        today_only = datetime.strptime(today_datetime_only, "%Y-%m-%d")

        if date_only == today_only:
            return 'Today at %s' % dt.strftime("%I:%M %p")
        else:
            return 'Yesterday at %s' % dt.strftime("%I:%M %p")
    elif delta.days == 1:
        return 'Yesterday at %s' % dt.strftime("%I:%M %p")
    elif delta.days > 1 and delta.days < 30:
        return '%s days ago at %s' % (delta.days, dt.strftime("%I:%M %p"))
    elif delta.days > 29 and delta.days < 365:
        months = delta.days / 30

        if months == 1:
            return '1 month ago'
        else:
            return str(months) + ' months ago'
    else:
        years = math.fabs(delta.days / 365)

        if years == 1:
            return '1 year ago'
        else:
            return str(int(years)) + ' years ago'


def branches_text(branches):
    """Return the branches text"""
    if len(branches) == 0:
        return ''
    elif len(branches) == 1:
        return 'branch ' + branches[0]['name']
    else:
        text = 'branches '

        for branch in branches:
            text += branch['name'] + ' and '

        return text.rstrip(' and ')


def clean(text):
    return comparable_name(text)


def format_datetime(date):
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    hour = int(date[8:10])
    minute = int(date[10:12])
    second = int(date[12:14])

    d = datetime(year, month, day, hour, minute, second)
    format = '%m/%d/%Y %I:%M %p'
    return d.strftime(format)


def format_isodate(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like May 05, 2012 04:30 PM
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%B %d, %Y %I:%M %p')


def format_isodate_date(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like May 05, 2012
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%B %d, %Y')


def format_isodate_time(isodate):
    """
    Formats an iso date like 2012-05-04T16:30:20.140762
    into a date like 04:30 PM
    """
    dt, _, us = isodate.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    return dt.strftime('%I:%M %p')


def show_sites_not_on_blacklist(site, user):
    """
    We only want Doula developers to see mtclone and mt99
    (our test accounts) for now
    """
    if site in ['mtclone', 'mt99']:
        if user in ['tbone', 'alexv']:
            return True
        else:
            return False

    return True


def doc_snippet(snippet):
    snippet = snippet + '.markdown'
    return markdown.markdown(_get_docs_text(snippet))


def _get_docs_text(filename):
    path = '/opt/doula/src/doula/doula/templates/docs/' + filename

    if Config.get('env') == 'dev':
        path = os.getcwd() + '/doula/templates/docs/' + filename

    index_file = open(path)
    text = unicode(index_file.read(), errors='ignore')
    index_file.close()

    return text