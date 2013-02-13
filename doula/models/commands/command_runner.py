class CommandRunner(object):

    def __init__(self, service_name, host_or_ip):
        self.service_name = service_name
        self.host_or_ip = host_or_ip

    def get_one(self, command_type):
        command =  CommandFactory(self.service_name,
                                self.host_or_ip,
                                Config.get('bambino.webapp_dir'),
                                Config.get('doula.keyfile_path')).get_one(command_type)
        return command


