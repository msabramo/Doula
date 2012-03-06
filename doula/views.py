from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from prism.resource import IApp


_ = TranslationStringFactory('Doula')


class RootHandler(object):
    """
    a handler
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(renderer='index.html', context=IApp)
    def index(self):
        return {}


