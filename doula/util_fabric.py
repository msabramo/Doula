from fabric.api import *
from contextlib import contextmanager
from fabric.context_managers import cd
from fabric.context_managers import hide
from fabric.context_managers import prefix
from fabric.context_managers import settings

@contextmanager
def debuggable(debug=False):
    if debug:
        yield
    else:
        with hide('warnings', 'running', 'stdout', 'stderr'):
            yield


@contextmanager
def workon(path, debug):
    with cd(path):
        if 'etc' in path:
            source = 'source %s/../bin/activate' % path
        else:
            source = 'source %s/bin/activate' % path
        with prefix(source):
            with debuggable(debug):
                with settings(warn_only=True):
                    yield


@contextmanager
def warn_only(path, debug=False):
    with debuggable(debug):
        with cd(path):
            with settings(warn_only=True):
                yield
