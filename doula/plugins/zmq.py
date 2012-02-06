def includeme(config):
    config.add_tween(zmqtween)


class zmqtween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        request.zmq = zmq
        return handle(request)


class WithTween(object):
    def __init__(self, cm, handler, registry, initializer, *args, **kw):
        self.cm = cm
        self.args = args
        self.kw = kw
        self.handler
        self.registry
        if initializer is not None:
            self.cm = self.initializer(cm, registry, *args, **kw)

    def caller(self, request):
        with self.cm:
            return self.handle(request)
