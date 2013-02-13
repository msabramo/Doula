import os
import unittest
import commands
from mock import Mock
from doula.models.commands.appenv_commands import *
from doula.models.commands.install_commands import *
from doula.models.commands.command_factory import CommandFactory
from mock import patch
from doula.config import Config
import ipdb

class TestInstallCommands(unittest.TestCase):

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

    def test_install_package(self):
        _, u = commands.getstatusoutput('rm -rf /tmp/anonweb')
        _, u = commands.getstatusoutput('mkdir /tmp/anonweb')
        command = self.get_one(InitGitRepo)
        command.web_app_dir = '/tmp'
        command.service_name = 'anonweb'
        self.assertTrue(command.run())

        command = self.get_one(InitVirtualEnv)
        command.web_app_dir = '/tmp'
        command.service_name = 'anonweb'
        self.assertTrue(command.run())

        command = self.get_one(InstallPackage)
        command.web_app_dir = '/tmp'
        command.service_name = 'anonweb'
        self.assertTrue(command.run('http://yorick:9003/index/requests-0.12.1.tar.gz'))

if __name__ == '__main__':
    unittest.main()
