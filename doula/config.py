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
        return c

    @staticmethod
    def get(key):
        """Get a key out of the settings dict."""
        return Config._instance.settings.get(key, None)

    @staticmethod
    def get_safe_site(site):
        """
        Get the safe name of a site. If we're on localhost we default to
        'mt3' because that has a history, while the name of our local machine does not.
        """
        if Config.get('env') == 'dev':
            return 'mt3'
        else:
            return site

