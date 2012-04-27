from fabric.api import local
from fabric.api import cd
from fabric.api import *
from fabric.contrib.files import exists

env.hosts = ['doula.corp.surveymonkey.com']
env.user = 'doula'
env.key_filename = '~/.ssh/id_rsa'
doula_dir = '/opt/doula'
supervisor_file = '/etc/supervisor/conf.d/doula.conf'

def update():
    with cd(doula_dir):
        if not exists('bin'):
            run('virtualenv .')
        with prefix('. bin/activate'):
            run('echo $VIRTUAL_ENV')
            run('pip install -e git+git@github.com:Doula/Doula.git#egg=doula')
        with cd('src/doula'):
            run('git submodule init')
            run('git submodule update')
        with cd('src/doula/etc'):
            run('git checkout master')
            run('git pull origin master')
            if exists(supervisor_file):
                sudo('rm %s' % supervisor_file)
            sudo('ln -s $(pwd)/supervisor.conf %s' % supervisor_file)
        restart()

def restart():
    sudo('supervisorctl reread doula_6543')
    sudo('supervisorctl restart doula_6543')
