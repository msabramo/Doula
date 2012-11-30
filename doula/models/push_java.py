from contextlib import contextmanager
from doula.models.user import User
from fabric.api import *
from fabric.context_managers import cd
from fabric.context_managers import hide
from fabric.context_managers import prefix
from fabric.context_managers import settings
import os
from doula.models.push import Push
import re
import json

import logging

@contextmanager
def debuggable(debug=False):
    if debug:
        yield
    else:
        with hide('warnings', 'running', 'stdout', 'stderr'):
            yield


class PushJava(Push):

    def __init__(self, service_name, username, java_dir, cheeseprism_url,
                keyfile, site_name_or_node_ip, debug=False):

        Push.__init__(self, service_name, username, java_dir, cheeseprism_url, 
                keyfile, site_name_or_node_ip, '', debug);

        self.warfile_name = self.warfile_mapping()
        self.java_dir = java_dir
        self.cheeseprism_url = os.path.join(cheeseprism_url, 'index', 'java')

    def warfile_mapping(self):
        if self.service_name == 'userdal':
            return "UserAccount"
        elif self.service_name == 'billingdal':
            return "Billing"
        raise "Invalid War File Mappping: %s not in 'userdal' or 'billingdal'" % self.name


    def release_service(self, wars):
        self.wars = wars

        for war_name in wars:
            short_name = self.short_war_name(war_name)
            path = '%s/%s/etc' %(self.java_dir, self.service_name)
            with cd(path):
                run('git pull origin master')
            with cd('%s/%s/' %(self.java_dir, self.service_name)):
                run('rm -rf tmp')
                run('mkdir tmp')
                run('curl %s/%s > tmp/%s.war' % (self.cheeseprism_url, war_name, self.service_name))
            with cd('%s/%s/tmp' %(self.java_dir, self.service_name)):
                run('unzip %s.war -d %s' % (self.service_name, short_name))
                run('cp ../etc/META-INF/persistence.xml %s/WEB-INF/classes/META-INF/persistence.xml' % short_name)
                run('zip -r %s.war %s' % (short_name, short_name))
                run('sudo cp %s.war /var/lib/tomcat6/webapps/' % short_name)
                sudo('chown tomcat6:tomcat6 /var/lib/tomcat6/webapps/%s.war' % short_name)
            with cd('%s/%s/' %(self.java_dir, self.service_name)):
                json_file = json.dumps({'version': war_name})
                run("echo '%s' > version.json" % json_file)

        message = '%s installed %s package(s):\n' % (self.username, len(wars))
        message = '\n'.join(wars)
        self.commit(message)


    def commit(self, message):
        with cd('%s/%s/' %(self.java_dir, self.service_name)):
            result = run('git add -A .')
            if result.succeeded:
                changes = run("git status --porcelain 2> /dev/null | sed -e 's/ M etc//g' | sed '/^$/d'")
                if changes:
                    author = "%s <%s>" % (self.username, self.email)
                    result = run('git commit --author="%s" -am "%s"' % (author, message))
                    if result.succeeded:
                        result = run('git push origin %s' % self._branch())

            if result.failed:
                raise Exception(str(result))

    def short_war_name(self, war_name):
        short_name = re.search('^(\w+)[_.]', war_name)
        return short_name.group(1)

def get_test_obj(service):
    return PushJava(service, '', '/opt/java/', 'http://yorick:9003/index', '/Users/timsabat/.ssh/id_rsa_doula_user', '/opt/smassets', True)
