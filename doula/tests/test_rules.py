import os
import unittest
import commands
from mock import Mock
from doula.models.rules.git_rules import *
from mock import patch
import ipdb

class TestRules(unittest.TestCase):

    def test_git_branch(self):
        rule = ValidateGitBranch('collectweb', 
                                '/opt/webapp',
                                'localhost',
                                '~/.ssh/id_rsa',
                                True)

        _, u = commands.getstatusoutput('whoami')
        rule.fabric_user = Mock(return_value=u)
        self.assertFalse(rule.validate('mt3'))
        self.assertTrue(rule.validate('mt1'))

    def test_git_origin(self):
        rule = ValidateServiceOrigin('collectweb', 
                                '/opt/webapp',
                                'localhost',
                                '~/.ssh/id_rsa',
                                True)

        _, u = commands.getstatusoutput('whoami')
        rule.fabric_user = Mock(return_value=u)
        self.assertFalse(rule.validate('FakeAppEnv', 'collectweb'))

if __name__ == '__main__':
    unittest.main()
