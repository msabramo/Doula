from doula.models.rules.git_rules import *

class RuleFactory(object):
    """
    This is the meat-and-taters of the rule world.
    """
    def __init__(self, 
            service_name,
            node_ip,
            web_app_dir="/opt/webapp",
            keyfile="~/.ssh/id_rsa_doula"):

        self.service_name = service_name
        self.node_ip = node_ip
        self.web_app_dir = web_app_dir
        self.keyfile = keyfile

    def rules(self, **kwargs):
        """
        Returns validated rules.

        What can you do with rules?  Oh, all kinds of stuff, like:

        {% for rule in rules: %}
            <h1>{{rule.description()}}</h1>
            {% if rule.is_valid %}
                <p>Passing!</p>
            {% else %}
                <p>Failing!</p>
                <p>{{rule.error_text()}}</p>
            {% endif %}
        {% endfor %}
        """
        self.args = kwargs
        rules = []

        # git branch
        rule = self._get_one(ValidateGitBranch)
        rule.validate(self.args['branch'])
        rules.append(rule)

        # git origin
        rule = self._get_one(ValidateServiceOrigin)
        rule.validate(self.args['code_org'], self.service_name)
        rules.append(rule)

        return rules


    def _get_one(self, the_type):
        return the_type(self.service_name,
                self.node_ip,
                self.web_app_dir,
                self.keyfile)

