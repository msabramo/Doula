import os
import unittest
import commands
from mock import Mock
from doula.models.commands.etc_commands import *
from doula.models.commands.appenv_commands import *
from doula.models.commands.command_factory import CommandFactory
from mock import patch
from doula.config import Config
import ipdb

class TestCommandsEtc(unittest.TestCase):

    def setUp(self):
        settings = {
            'doula.github.api.domain': 'http://api.code.corp.surveymonkey.com',
            'doula.github.appenvs.org': 'config',
            'doula.github.doula.admins.org': 'DoulaAdmins',
            'doula.github.packages.org': 'devmonkeys',
            'doula.github.config.org': 'config',
            'doula.github.html.domain': 'http://code.corp.surveymonkey.com',
            'doula.github.token': '17e6642dca429043725ad6a98ce966e5a67eac69',
            'doula.github.webhook.url':'http://doula.corp.surveymonkey.com/webhook/callbacks'
        }
        self.config = testing.setUp()
        self.config.add_renderer('.html', renderer_factory)
        self.config.include('pyramid_jinja2')
        Config.load_config(settings)

    def get_one(self, command_type):
        command =  CommandFactory('collectweb',
                                'localhost',
                                '/opt/webapp',
                                '~/.ssh/id_rsa').get_one(command_type)
        _, u = commands.getstatusoutput('whoami')
        command.fabric_user = Mock(return_value=u)
        return command

    #def test_create_templates(self):
        #_, u = commands.getstatusoutput('rm -rf /tmp/anonweb')
        #_, u = commands.getstatusoutput('mkdir /tmp/anonweb')
        #_, u = commands.getstatusoutput('mkdir /tmp/anonweb/etc')
        #command = self.get_one(WriteTemplates)
        #command.web_app_dir = '/tmp'
        #command.service_name = 'anonweb'
        #command.run(numprocs=2, is_pserve=True, upstream_prefix='203', vip_port='6001')
        #result, u = commands.getstatusoutput('ls /tmp/anonweb/etc/supervisor.conf')
        #self.assertTrue(result == 0)
        #result, u = commands.getstatusoutput('ls /tmp/anonweb/etc/nginx.conf')
        #self.assertTrue(result == 0)

    def sd(self, command, web_app_dir, service_name):
        command.web_app_dir = '/tmp'
        command.service_name = 'empty'
        return command

    def test_commit_configs(self):
        _, u = commands.getstatusoutput('rm -rf /tmp/empty')
        _, u = commands.getstatusoutput('mkdir /tmp/empty')
        command = self.get_one(InitGitRepo)
        command = self.sd(command, '/tmp', 'empty')
        command.run()

        command = self.get_one(AddRemote)
        command = self.sd(command, '/tmp', 'empty')
        command.run('config')

        command = self.get_one(AddSubmodule)
        command = self.sd(command, '/tmp', 'empty')
        command.run(org='FakeAppEnvs')

        command = self.get_one(WriteTemplates)
        command = self.sd(command, '/tmp', 'empty')
        command.run(numprocs=2, is_pserve=True, upstream_prefix='203', vip_port='6001')

        command = self.get_one(CommitGitRepo)
        command = self.sd(command, '/tmp', 'empty')
        command.run(is_etc=True)

    def test_push_configs(self):
        _, u = commands.getstatusoutput('rm -rf /tmp/empty')
        _, u = commands.getstatusoutput('mkdir /tmp/empty')
        command = self.get_one(InitGitRepo)
        command = self.sd(command, '/tmp', 'empty')
        command.run()

        command = self.get_one(AddRemote)
        command = self.sd(command, '/tmp', 'empty')
        command.run('config')

        command = self.get_one(AddSubmodule)
        command = self.sd(command, '/tmp', 'empty')
        command.run(org='FakeAppEnvs')

        command = self.get_one(WriteTemplates)
        command = self.sd(command, '/tmp', 'empty')
        command.run(numprocs=2, is_pserve=True, upstream_prefix='203', vip_port='6001')

        command = self.get_one(CommitGitRepo)
        command = self.sd(command, '/tmp', 'empty')
        command.run(is_etc=True)

        command = self.get_one(PushGitRepo)
        command = self.sd(command, '/tmp', 'empty')
        command.run(is_etc=True)


if __name__ == '__main__':
    unittest.main()
