from fabric.api import *
from fabric.contrib.files import exists

env.user = 'doula'
env.key_filename = '~/.ssh/id_rsa'

def _validate(project):
    valid_projects = ['bambino', 'doula']
    if(not project in valid_projects):
        print 'this command takes one of the following arguments:'
        print valid_projects

def do_setup(project):
    path = '/opt/%s' % project
    if not exists(path):
        sudo('mkdir %s' % path)
        sudo('chown doula:root %s' % path)
        sudo('chmod 0775 %s' % path)

def setup(project):
    _validate(project)
    do_setup(project)
