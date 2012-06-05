import json
from pprint import pprint as pretty_print
import re

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
            return getattr(obj, '__dict__', { })
        
        raise TypeError(repr(obj) + " is not JSON serializable")
    

def dumps(obj):
    return ObjectEncoder().encode(obj)

def pprint(obj):
    pretty_print(dumps(obj))
