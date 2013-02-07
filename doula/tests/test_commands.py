import os
import unittest
import commands
from mock import Mock
from doula.models.commands.commands import *
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

    def test_git_branch(self):
        command = self.get_one(ConfigRepoExists)
        self.assertTrue(command.run(org='config', repo='createweb'))
        self.assertFalse(command.run(org='config', repo='createwebb'))

    def test_config_absent(self):
        command = self.get_one(ConfigFilesAbsent)
        result = command.run(org='config', repo='createweb')
        self.assertFalse(result)
        command = self.get_one(ConfigFilesAbsent)
        result = command.run(org='FakeAppEnvs', repo='empty')
        self.assertTrue(result)

    def test_service_root_absent(self):
        command = self.get_one(ServiceRootDirectoryAbsent)
        result = command.run()
        self.assertFalse(result)

    def test_appenv_absent(self):
        command = self.get_one(AppEnvRepoAbsent)
        result = command.run(org='FakeAppEnvs', repo='nothing')
        self.assertTrue(result)
        command = self.get_one(AppEnvRepoAbsent)
        result = command.run(org='appenv', repo='anonweb')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
