import re
import requests
import logging
import operator

from fabric.api import *
from git import *

from doula.util import dirify
from doula.util import is_number
from doula.models.audit import Audit
from doula.models.sites_dal import SiteDAL
from doula.models.package import Package

# Defines the Data Models for Doula and Bambino.
#
# sites
#   Site
#     nodes
#       services
#         Service
#           packages
#             Package
#     services
#       Service
#         packages
#           Package

log = logging.getLogger('doula')


class Service(object):
    def __init__(self, name, site_name, node_name, url,
        current_branch_app='', current_branch_config='',
        change_count_app='', change_count_config='',
        is_dirty_app=False, is_dirty_config=False,
        last_tag_app='', last_tag_config='', last_tag_message='',
        status='', remote='', repo='', packages=[], changed_files=[], tags=[]):
        self.name = name
        self.site_name = site_name
        self.node_name = node_name
        self.name_url = dirify(name)
        self.url = url

        self.current_branch_app = current_branch_app
        self.current_branch_config = current_branch_config

        self.change_count_app = change_count_app
        self.change_count_config = change_count_config

        self.is_dirty_app = is_dirty_app
        self.is_dirty_config = is_dirty_config

        self.last_tag_app = last_tag_app
        self.last_tag_config = last_tag_config
        self.last_tag_message = last_tag_message

        self.status = status
        self.remote = remote
        self.packages = packages
        self.changed_files = changed_files
        self.tags = tags

    @staticmethod
    def build_app(site_name, node_name, url, app):
        """Build an service object from the app dictionary"""

        a = Service(app['name'], site_name, node_name, url)
        a.current_branch_app = app['current_branch_app']
        a.change_count_app = app['change_count_app']
        a.change_count_config = app['change_count_config']
        a.is_dirty_config = app['is_dirty_config']
        a.last_tag_config = app['last_tag_config']
        a.status = app['status']
        a.remote = app['remote']
        a.last_tag_app = app['last_tag_app']
        a.last_tag_message = app['last_tag_message']
        a.current_branch_config = app['current_branch_config']
        a.changed_files = app['changed_files']
        a.tags = []
        a.packages = []
        a.add_packages(app['packages'])
        a.add_tags_from_dict(app['tags'])
        a.last_tag = a.get_last_tag()

        return a

    def add_packages(self, pckgs):
        for name, pckg in pckgs.iteritems():
            self.packages.append(Package(pckg['name'], pckg['version']))

    def add_tags_from_dict(self, tags_as_dicts):
        for tag in tags_as_dicts:
            self.tags.append(Tag(tag['name'], tag['date'], tag['message']))

        self._update_last_tag()

    def get_compare_url(self):
        """
        Use the remote url to return the Github Comapre view URL.
        The Github Compare URL has the format:
        http://<GITHUB_URL>/<USER>/<REPO>/compare/<START>...<END>
        For us this means
        http://code.corp.surveymonkey.com/DevOps/[name]/compare/[last_tag_app]...[current_branch_app]
        """
        if self.remote.startswith('http'):
            # parses http://code.corp.surveymonkey.com/tbone/anweb.git type remote
            m = re.search(r'http:\/\/([\w\.]+)\/([\w\d]+)\/([\w\d]+)', self.remote)
        else:
            # parses git@code.corp.surveymonkey.com:tbone/anweb-1.git type remote
            m = re.search(r'@([\w\.]+):([\w\d]+)\/([\w\d]+)', self.remote)

        compare_url = ''

        if m:
            compare_url = 'http://' + m.group(1) + '/' + m.group(2) + '/' + self.name
            compare_url += '/compare/' + self.last_tag.name + '...' + self.current_branch_app

        return compare_url

    def tag(self, tag, msg, user):
        """
        Tag the current service
        """
        payload = {'tag': tag, 'description': msg, 'apps': self.name}
        r = requests.post(self.url + '/tag', data=payload)
        # If the response is non 200, we raise an error
        r.raise_for_status()

        self.tag = tag
        self.msg = msg
        self.status = 'tagged'

        audit = Audit()
        audit.log_action(self.site_name, self.name, 'tag', user)

    def _update_last_tag(self):
        self.last_tag_app = self.get_last_tag()
        self.last_tag_config = self.get_last_tag()

    def get_last_tag(self):
        # Initialize an empty tag if it doesn't tag exist
        latest_tag = Tag('', '', '')
        latest_tag_date = 0

        for tag in self.tags:
            if tag.date > latest_tag_date:
                latest_tag = tag
                latest_tag_date = tag.date

        return latest_tag

    def get_status(self):
        if self.status == 'tagged' and SiteDAL.is_deployed(self, self.last_tag):
            return 'deployed'
        else:
            return self.status

    def mark_as_deployed(self, tag, user):
        """
        Mark an service as deployed
        """
        self.status = 'deployed'
        SiteDAL.save_service_as_deployed(self, tag)

        audit = Audit()
        audit.log_action(self.site_name, self.name, 'deploy', user)

    def get_logs(self):
        audit = Audit()
        app_logs = audit.get_app_logs(self.site_name, self.name)

        for log in app_logs:
            log['service'] = self.name

        return app_logs

    def next_version(self):
        """
        Get the next logical version.
        i.e. 0.2.4 -> 0.2.5
        """
        next_version = ''
        rslts = re.split(r'(\d+)', self.last_tag.name)
        rslts.reverse()
        found_digit = False

        for rslt in rslts:
            if found_digit is False and is_number(rslt):
                found_digit = True
                part = int(rslt) + 1
            else:
                part = rslt

            next_version = str(part) + next_version

        return next_version

    def get_tag_by_name(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag

        return False

    def freeze_requirements(self):
        reqs = ''

        self.packages.sort(key=operator.attrgetter('name'))

        for pckg in self.packages:
            reqs += pckg.name + '==' + pckg.version + "\n"

        return reqs
