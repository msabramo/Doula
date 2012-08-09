from fabric.api import *
from fabric.contrib.files import exists

env.user = 'doula'
env.key_filename = '~/.ssh/id_rsa_doula'


def _validate(project):
    valid_projects = ['bambino', 'doula']
    if(not project in valid_projects):
        print 'this command takes one of the following arguments:'
        print valid_projects


def _make_jobs_log_dir(project):
    path = '/var/log/%s' % project

    if not exists(path):
        sudo('mkdir %s' % path)
        sudo('chown doula:root %s' % path)
        sudo('chmod 0775 %s' % path)


def _pull(project, path):
    with cd(path):
        if not exists('bin'):
            run('virtualenv .')
        with prefix('. bin/activate'):
            run('echo $VIRTUAL_ENV')
            run('pip install -e git+git://github.com/Doula/%s.git@master#egg=%s' % (project.title(), project))
        with cd('src/%s' % project):
            run('git submodule init')
            run('git submodule update')
        with cd('src/%s/etc' % project):
            run('git checkout master')
            run('git pull origin master')
            if(project == 'doula'):
                _restart(project, 6543)
            else:
                _restart(project, 6666)


def do_setup(project):
    path = '/opt/%s' % project
    if not exists(path):
        sudo('mkdir %s' % path)
        sudo('chown doula:root %s' % path)
        sudo('chmod 0775 %s' % path)

    _pull(project, path)

    supervisor_file = '/etc/supervisor/conf.d/%s.conf' % project
    sudo('rm %s' % supervisor_file)
    sudo('ln -s %s/src/%s/etc/supervisor.conf %s' % (path, project, supervisor_file))



def _restart(project, port):
    run('supervisorctl reread')
    run('supervisorctl load %s_%s' % (project, port))


def setup(project):
    _validate(project)
    do_setup(project)
