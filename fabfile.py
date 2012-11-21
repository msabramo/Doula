from fabric.api import cd
from fabric.api import *
from fabric.contrib.files import exists
import os

if "DOULA_STAGE" in os.environ:
    env.hosts = ['mt-99.corp.surveymonkey.com']
    branch = 'stage'
else:
    env.hosts = ['doula.corp.surveymonkey.com']
    branch = 'master'

env.user = 'doula'
env.key_filename = ['~/.ssh/id_rsa_doula']
doula_dir = '/opt/doula'
supervisor_file = '/etc/supervisor/conf.d/doula.conf'

def update():
    with cd(doula_dir):
        if not exists('bin'):
            run('virtualenv -p /usr/local/bin/python2.7 .')
        with prefix('. bin/activate'):
            run('echo $VIRTUAL_ENV')
            run('pip install -e git+http://code.corp.surveymonkey.com/DevOps/velruse#egg=velruse')
            run('pip install -e git+git@github.com:Doula/Doula.git@%s#egg=doula' % branch)
        with cd('src/doula'):
            run('git submodule init')
            run('git submodule update')
        with cd('src/doula/etc'):
            run('git checkout %s' % branch)
            run('git pull origin %s' % branch)
        restart()


def restart():
    run('supervisorctl reread doula_6543')
    run('supervisorctl restart doula_6543')
    run('supervisorctl reread retools')
    run('supervisorctl restart retools')
    run('supervisorctl reread retools-maintenance')
    run('supervisorctl restart retools-maintenance')
