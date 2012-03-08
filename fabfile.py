from fabric import api as fab
from path import path
import os


@fab.task
def clone_develop(pkg):
    if not path(pkg).exists():
        fab.local('git clone git@github.com:SurveyMonkey/%s.git' %pkg)
    fab.local('pip install -r %s/develop.txt' %pkg)


@fab.task
def install_deps(version='zeromq-2.1.11'):
    venv = path(os.environ['VIRTUAL_ENV'])
    srcdir = venv / 'src'
    with fab.cd(srcdir):
        if not (srcdir / version).exists():
            fab.local('wget -O - "http://download.zeromq.org/%s.tar.gz" | tar -xvzf -' %version, shell=True)
        with fab.cd(srcdir / version):
            fab.local("./configure --prefix %s" %version)
            fab.local('make')
            fab.local('make install')
        fab.local("ZMQ_DIR=%s pip install pyzmq" %venv)
        fab.local('pip install distribute==0.6.14')
        fab.local('git clone git@github.com:whitmo/gevent-zeromq.git')
        with fab.cd('gevent-zeromq'):
            fab.local('pip install -e ./')
        fab.execute('Doula')
        fab.execute('Bambino')



