import json
import unittest
from doula.models.sites import Application
from doula.models.sites import Package

class ApplicationTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_compare_url(self):
        app = Application('test_app', 'site_name', 'test_node', 'http://test.com')
        app.remote = 'git@code.corp.surveymonkey.com:DevOps/WebApp1.git'
        app.last_tag_app = '1.0.3'
        app.current_branch_app = 'master'
        
        compare_url = 'http://code.corp.surveymonkey.com'
        compare_url+= '/DevOps/test_app/compare/1.0.3...master'
        
        self.assertEqual(app.get_compare_url(), compare_url)
    
    def test_freeze_requirements(self):
        app = Application('test_app', 'site_name', 'test_node', 'http://test.com')
        packages = [ ]
        
        packages.append(Package('mnn', '1'))
        packages.append(Package('ebd', '2'))
        packages.append(Package('dbc', '2'))
        packages.append(Package('abc', '1'))
        app.packages = packages
        
        expected = "abc==1\n"
        expected+= "dbc==2\n"
        expected+= "ebd==2\n"
        expected+= "mnn==1\n"
        
        self.assertEqual(app.freeze_requirements(), expected)
    

if __name__ == '__main__':
    unittest.main()