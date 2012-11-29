from doula.models.package import Package
import logging
import json
import os
from fabric.api import *
from doula.config import Config

class PackageJava(Package):

    def __init__(self, name, version, remote=''):
        Package.__init__(self, name, version, remote)


    def update_version(self, repo, new_version):
        """
        Update the version.json with a new version
        """
        logging.info('Updating the version to %s' % new_version)
        version_file = None

        version_file_path = os.path.join(repo.working_dir, 'version.json')
        with open(version_file_path, 'w') as f:
            f.write(json.dumps({'version':new_version}))

        logging.info('Updated the version.')


    def commit(self, repo, files, msg):
        super(PackageJava, self).commit(repo, ['version.json'], msg)


    def upload(self, repo):
        logging.info('Releasing to cheeseprism.')

        with lcd(repo.working_dir):
            local('ant')
            url = Config.get('doula.cheeseprism_url')
            url = 'doula@'+url.split(':')[1].replace('//', '')
            pkg_index_path = Config.get('doula.cheeseprism_package_index_path')
            pkg_index_path = os.path.join(pkg_index_path, 'java')

            source_file = 'repos/%s/dist/%s.war' % (self.name, self.warfile_mapping())
            source_file = os.path.join(os.getcwd(), source_file)

            target_file = '%s:%s/%s.war_%s' % (
                url,
                pkg_index_path,
                self.warfile_mapping(),
                self.version)

            identity_file = '-i %s' % Config.get('doula.keyfile_path')
            command = 'scp %s %s %s' % (identity_file, source_file, target_file)
            local(command)

    def warfile_mapping(self):
        if self.name == 'userdal':
            return "UserAccount"
        elif self.name == 'billingdal':
            return "Billing"
        raise "Invalid War File Mappping: %s not in 'userdal' or 'billingdal'" % self.name

