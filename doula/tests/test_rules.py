import os
import unittest
import commands
from mock import Mock
from doula.models.rules.git_rules import *
from doula.models.rules.rule_factory import RuleFactory
from mock import patch
import ipdb

class TestRules(unittest.TestCase):

    def test_git_branch(self):
        rule = ValidateGitBranch('collectweb', 
                                'localhost',
                                '/opt/webapp',
                                '~/.ssh/id_rsa',
                                True)

        _, u = commands.getstatusoutput('whoami')
        rule.fabric_user = Mock(return_value=u)
        self.assertFalse(rule.validate('mt3'))
        self.assertTrue(rule.validate('mt1'))

    def test_git_origin(self):
        rule = ValidateServiceOrigin('collectweb', 
                                'localhost',
                                '/opt/webapp',
                                '~/.ssh/id_rsa',
                                True)

        _, u = commands.getstatusoutput('whoami')
        rule.fabric_user = Mock(return_value=u)
        self.assertFalse(rule.validate('FakeAppEnv', 'collectweb'))

    def test_rule_factory(self):
        factory = RuleFactory('collectweb', 'localhost')
        rules = factory.rules(
                code_org='FakeAppEnvss',
                branch='mt1')

        for rule in rules:
            print rule.description()
            if rule.is_valid:
                print "is valid"
            else:
                print rule.error_text()

if __name__ == '__main__':
    unittest.main()
