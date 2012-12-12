from doula.models.push import Push
from doula.models.push_java import PushJava

class PushFactory(object):

    @classmethod
    def get_push_object(service, node, job_dict, config, debug):
        if 'type' in job_dict && job_dict['type'] == 'java':
            push = PushJava(
                service.name,
                node.ip,
                job_dict['user_id'],
                config['bambino.java_dir'],
                config['doula.cheeseprism_url'],
                config['doula.keyfile_path'],
                config['doula.assets.dir'],
                debug
            )
        else:
            push = Push(
                service.name,
                node.ip,
                job_dict['user_id'],
                config['bambino.webapp_dir'],
                config['doula.cheeseprism_url'],
                config['doula.keyfile_path'],
                config['doula.assets.dir'],
                debug
            )
        return push



