class Config(object):
    """
    Holds onto the config settings for the entire application
    """
    _instance = None
    def __init__(self, settings):
        self.settings = settings

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def load_config(settings):
        c = Config(settings)

    @staticmethod
    def get(key):
        """Get a key out of the settings dict."""
        return Config._instance.settings.get(key, None)