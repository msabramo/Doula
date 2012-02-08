from mock import patch, Mock
from nose.tools import raises
import unittest


class TestPluginLoader(unittest.TestCase):

    def makeone(self):
        from doula import plugin; reload(plugin)
        plugin_text = """
        doula.plugins.vv
        doula.notexist
        doula.plugins.appenv # builds the resource tree for appenvs
        """
        return plugin.load(plugin_text)
    
    def test_plugin_loader(self):
        from doula.plugins import vv
        plugs = self.makeone()
        assert next(plugs) is vv
        
    def test_notfound_plugin(self):
        _, exc, _ = self.makeone()
        from doula import plugin
        assert isinstance(exc, plugin.PluginNotFoundError)

    def test_unexpected_plugin(self):
        error = NotImplementedError('Surprise!!!!')
        with patch('pyramid.util.DottedNameResolver.maybe_resolve',
                   Mock(side_effect=error)):
            _, exc, _ = self.makeone()
        assert exc is error

    def test_commented_plugin(self):
        plugs = list(self.makeone())
        from doula.plugins import appenv
        assert plugs[-1] == appenv

    def test_cleaner(self):
        from doula import plugin
        assert plugin.cleaner('  hello #a comment\n') == 'hello'

    @raises(ValueError)
    def test_cleaner_error(self):
        from doula import plugin
        plugin.cleaner('???')

    @raises(ValueError)
    def test_cleaner_error_empty_string(self):
        from doula import plugin
        plugin.cleaner('')        

        
