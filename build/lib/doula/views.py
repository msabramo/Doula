from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from doula import resources


_ = TranslationStringFactory('Bambino')


class RootHandler(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(renderer='index.html', context=resources.App)
    def index(self):
        return {}


