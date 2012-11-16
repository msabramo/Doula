from doula.models.package import Package

class PackageJava(Package):

    def __init__(self, name, version, remote=''):
        super(Package, self, name, version, remote).__init__()


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
        self.commit(repo, ['version.json'], msg)


    def upload(self, repo):
        logging.info('Releasing to cheeseprism.')

        with lcd(repo.working_dir):
            local('ant')
            url = Config.get('doula.cheeseprism_url').split(':')[0]
            pkg_index_path = os.path.join(Config.get('doula.cheeseprism_package_index_path'), 'java')
            local('scp dist/%s.war %:%/%.war_%' % (
                self.name,
                url,
                pkg_index_path,
                self.name,
                self.version)
            )


