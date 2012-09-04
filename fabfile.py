from fabric.api import cd
from fabric.api import *
from fabric.contrib.files import exists

env.hosts = ['mt-99.corp.surveymonkey.com']
env.user = 'doula'
env.key_filename = ['~/.ssh/id_rsa_doula']
doula_dir = '/opt/doula'
supervisor_file = '/etc/supervisor/conf.d/doula.conf'

print env.key_filename


def update():
    with cd(doula_dir):
        if not exists('bin'):
            run('virtualenv .')
        with prefix('. bin/activate'):
            run('echo $VIRTUAL_ENV')
            run('pip install -e git+http://code.corp.surveymonkey.com/DevOps/velruse#egg=velruse')
            run('pip install -e git+git@github.com:Doula/Doula.git@stage#egg=doula')
        with cd('src/doula'):
            run('git submodule init')
            run('git submodule update')
        with cd('src/doula/etc'):
            run('git checkout stage')
            run('git pull origin stage')
        restart()


def restart():
    run('supervisorctl reread doula_6543')
    run('supervisorctl restart doula_6543')
    run('supervisorctl reread retools')
    run('supervisorctl restart retools')
