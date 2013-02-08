import os
import unittest
import commands
from mock import Mock
from doula.models.commands.appenv_commands import *
from doula.models.commands.command_factory import CommandFactory
from mock import patch
from doula.config import Config
import ipdb

class TestCommands(unittest.TestCase):

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

        Config.load_config(settings)

    def get_one(self, command_type):
        command =  CommandFactory('collectweb',
                                'localhost',
                                '/opt/webapp',
                                '~/.ssh/id_rsa').get_one(command_type)
        _, u = commands.getstatusoutput('whoami')
        command.fabric_user = Mock(return_value=u)
        return command

    def test_create_appenv_repo(self):
        command = self.get_one(CreateAppenvRepo)
        command.service_name = 'delete_me'
        self.assertFalse(command.run('appenv'))

    #def test_delete_appenv_repo(self):
        #command = self.get_one(DeleteAppenvRepo)
        #self.assertFalse(command.run(org='appenv', repo='delete_me'))

    def test_create_service_folder(self):
        _, u = commands.getstatusoutput('rm -rf /tmp/dookie')
        command = self.get_one(CreateServiceFolder)
        command.web_app_dir = '/tmp'
        command.service_name = 'dookie'
        self.assertTrue(command.run())

    def test_init_git_repo(self):
        _, u = commands.getstatusoutput('rm -rf /tmp/dookie')
        command = self.get_one(InitGitRepo)
        command.web_app_dir = '/tmp'
        command.service_name = ''
        self.assertTrue(command.run())

if __name__ == '__main__':
    unittest.main()
