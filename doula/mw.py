from geventutil.server import Exiting


class CallbackExiting(Exiting):
    
    def __init__(self, app, callback=None, suffix='pid'):
        super(CallbackExiting, self).__init__(app, suffix='pid')
        self.callback = None

    def __call__(self, environ, start_response):
        self.logger.debug("Exiting status: %s", self.exiting)
        if self.exiting and self.callback:
            self.callback(environ, start_response)
        return self.app(environ, start_response)
