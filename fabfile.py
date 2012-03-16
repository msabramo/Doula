from contextlib import contextmanager
from fabric import api as fab
from path import path
import os
import subprocess

pushd = fab.lcd

GEVENT = 'git@github.com:whitmo/gevent.git'
GEVENT_ZMQ = 'git@github.com:whitmo/gevent-zeromq.git'
DOULA = 'git@github.com:SurveyMonkey/Doula.git'
BAMBINO = 'git@github.com:SurveyMonkey/Bambino.git'
ZMQ = 'zeromq-2.1.11'
venv = path(os.environ['VIRTUAL_ENV'])

def ppid():
    print os.getpid()


def sh(cmd, pre=ppid, **addenv):
    env = os.environ.copy()
    env.update(addenv)
    return subprocess.check_output(cmd, env=env, preexec_fn=pre, shell=True)


@fab.task
def clone_develop(pkg, repo):
    if not path(pkg).exists():
        fab.local('git clone %s %s' %(repo, pkg))
    fab.local('pip install -r %s/develop.txt' %pkg)


@fab.task
def install_doula(repo=DOULA):
    clone_develop('doula', repo)


@fab.task
def install_bambino(repo=BAMBINO):
    clone_develop('bambino', repo)


@fab.task
def install_zmq(version=ZMQ):

    srcdir = venv / 'src'
    if not (srcdir / version).exists():
        with pushd(srcdir):
            fab.local('wget -O - "http://download.zeromq.org/%s.tar.gz" | tar -xzf -' %(srcdir.abspath(), version))
        
    with pushd(srcdir / version):
        if not path('config.status').exists():
            fab.local("./configure --prefix %s" %venv)
        fab.local('make')
        fab.local('make install')


@fab.task
def install_deps():
    venv = path(os.environ['VIRTUAL_ENV'])
    srcdir = venv / 'src'
    with pushd(srcdir):
        fab.execute(install_zmq)
        fab.local('pip install Cython')
        fab.local('pip install -e git+%s#egg=gevent' %GEVENT)
        fab.local("pip install pyzmq --install-option='--zmq=%s'" %venv)
        fab.local('pip install distribute==0.6.14')
        fab.execute('install_gz')
        fab.execute('install_doula')
        fab.execute('install_bambino')

@fab.task
def install_gz():
    srcdir = venv / 'src'
    with pushd(srcdir):
        with fab.settings(warn_only=True):
            if not path('gevent=zeromq').exists():
                fab.local('git clone %s' %GEVENT_ZMQ)
        with pushd('gevent-zeromq'):
            print "<< distribute flail >>"
            fab.local("python setup.py build_ext -I$VIRTUAL_ENV/include install")

@contextmanager
def pushd(dir):
    old_dir = os.getcwd()
    os.chdir(dir)
    try:
        yield old_dir
    finally:
        os.chdir(old_dir)
