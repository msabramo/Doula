from pprint import pprint as pretty_print
import simplejson as json
import re
import requests
import time


def find_package_and_version_in_pip_freeze_text(text):
    """
    Parses the line like: 'smtemplates==0.27.38' or 'sqlalchemy-migrate==0.6.1'
    and returns the package name and version number, if it doesn't match
    we return an emtpy dict
    """
    package_and_version = {}

    if text:
        m = re.match(r'^([\S]+)==([\S]+)$', text.strip())

        if m:
            package_and_version[m.group(1)] = m.group(2)

    return package_and_version

def date_to_seconds_since_epoch(date):
    """
    Convert a date like 2012-11-13T18:24:21+00:00 to
    the seconds since the epoch.

    Other examples:
        2012-11-14T02:08:36+00:00
        2012-11-14T00:29:01+00:00
        2012-11-13T18:44:56+00:00
        2012-11-10T00:20:03+00:00
    """
    if not date:
        return 0

    date = remove_timezone(date)
    struct_time = time.strptime(date, "%Y-%m-%dT%H:%M:%S")

    return time.mktime(struct_time)


def remove_timezone(date):
    """Remove timezone from date"""
    date = date.split("+")[0]

    # If we still have a timezone, remove it
    if date.count('-') > 2:
        date = date[:date.rfind('-')]

    return date


def next_version(version):
    """
    Get the next logical version.
    i.e. 0.2.4 -> 0.2.5
    """
    next_version = ''
    rslts = re.split(r'(\d+)', version)
    rslts.reverse()
    found_digit = False

    for rslt in rslts:
        if found_digit is False and is_number(rslt):
            found_digit = True
            part = int(rslt) + 1
        else:
            part = rslt

        next_version = str(part) + next_version

    # Since we add the branch like this [version]-[branch]
    # we remove it for the next auto version, because we'll
    # tack it back on when we save it
    next_version = next_version.split('-')[0]

    return next_version


def comparable_name(name):
    """
    Make name that is easy to compare
    """
    name = name.lower()
    name = name.replace('.', '')
    name = name.replace('-', '')
    name = name.replace('_', '')

    return name


def pull_url(url, timeout=3.0):
    """
    Pull the URL text. Always raise the status error.
    """
    response = requests.get(url, timeout=timeout)
    # If the response is non 200, we raise an error
    response.raise_for_status()
    return response.text

def post_url(url, data, timeout=3.0):
    """
    Pull the URL text. Always raise the status error.
    """
    r = requests.post(url, data=data, timeout=timeout)
    # If the response is non 200, we raise an error
    r.raise_for_status()
    if obj_as_json:
        return json.loads(r.text)
    else:
        return {}


def pull_json_obj(url, timeout=3.0):
    """
    Pull the url and decode the JSON
    """
    obj_as_json = pull_url(url)

    if obj_as_json:
        return json.loads(obj_as_json)
    else:
        return {}

def dirify(url):
    url = url.lower()
    url = url.replace('<', '')
    url = url.replace('>', '')
    url = url.replace('&', '')
    url = url.replace('"', '')
    url = re.sub(r'\s+', '_', url)
    url = re.sub(r'[^\d\w\s]!', '', url)

    return url


def git_dirify(name):
    """
    Git has rules about naming a tag or a branch properly.
    This function cleans up a branch or a tag to make sure the name is valid.
    See this reference:
    http://schacon.github.com/git/git-check-ref-format.html
    """
    name = dirify(name)
    unsafe_chars = ['..', '@{', '\\']

    for char in unsafe_chars:
        name = name.replace(char, '')

    # cannot end with the /
    name = name.rstrip('/')
    # cannot end with the .lock
    name = name.rstrip('.lock')

    return name


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, object):
            return getattr(obj, '__dict__', {})

        raise TypeError(repr(obj) + " is not JSON serializable")


def dumps(obj):
    return ObjectEncoder().encode(obj)


def pprint(obj):
    pretty_print(dumps(obj))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def to_log_msg(log_vals):
    """
    Return a key=value pair style log msg. Makes our log msg easy to
    search in Splunk.
    """
    log_msg = ''
    for key, value in log_vals.iteritems():
        log_msg += str(key) + '=' + str(value) + ' '

    return log_msg.strip()


def groupfinder(user_id, request):
    if request.user is None:
        return None
    else:
        return []
