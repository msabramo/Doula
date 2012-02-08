from pyramid.util import DottedNameResolver
import logging
import re

resolve = DottedNameResolver(None).maybe_resolve

logger = logging.getLogger(__name__)
comment_re=re.compile(r'^\s*(?P<spec>[a-zA-Z0-9_\.]+)\s*(?P<comment>#.*)?$')


def cleaner(string, regex=comment_re, key='spec'):
    string = string.strip()
    if string.startswith('#'):
        return None
    match = regex.match(string)
    if match:
        return match.groupdict()[key].strip()
    
    raise ValueError("<%s> is a malformed string" %string)


def load(plugins, cleaner=cleaner):
    """
    if a string, assume following format::

    >>> plugins = '''blah.plugin
                     my.plugin  # I tell you what this is
                     some.pkg
                     # a comment
                     '''
    
    """
    if isinstance(plugins, basestring):
        plugins = (x for x in specs_from_str(plugins) if x)

    for plugin in plugins:
        try:
            yield resolve(plugin)
        except ImportError, e:
            yield PluginNotFoundError('%s not importable: %s' %(plugin, e))
        except Exception, e:
            logger.error(e)
            yield e


def specs_from_str(string):
    return (cleaner(p) for p in string.split('\n') if p.strip())


def modify_resources(app, plugins, settings):
    for plugin in plugins:
        mod = getattr(plugin, 'modify_resources', None)
        if mod is not None:
            mod(settings, app)


class PluginNotFoundError(ImportError):
    """
    A plugin is not found by the resolve
    """
    
