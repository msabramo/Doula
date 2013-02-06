from doula.models.rules.rule import Rule
from doula.util_fabric import *
import re

class ValidateGitBranch(Rule):

    def description(self):
        return "Validate that this service is on the correct branch."

    def validate(self, branch):
        self.branch = branch
        with warn_only(self._service_path()):
            self.result = run("git symbolic-ref HEAD 2>/dev/null | cut -d'/' -f 3")
        return self.validate_logic(self.result == branch)


    def error_text(self):
        output = "The branch '%s' does not match \
                      the intended branch '%s'" % (self.result, self.branch)
        return self.error_logic(output)


class ValidateServiceOrigin(Rule):

    def description(self):
        return "Validate that the serice origin is properly configured."

    def validate(self, org, service_name, fqdn='code.corp.surveymonkey.com'):
        with warn_only(self._service_path()):
            self.result = run("git remote -v | head -1 | awk '{print $2}'")

        self.origin = "git@%s:%s/%s" % (fqdn, org, service_name)
        return self.validate_logic(self.result == self.origin)


    def error_text(self):
        output = "The origin '%s' does not match \
                      the intended origin '%s'" % (self.result, self.origin)
        return self.error_logic(output)


