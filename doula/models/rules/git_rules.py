from doula.models.fabric_base import FabricBase
from doula.util_fabric import *
import re

class ValidateGitBranch(FabricBase):

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

class ValidateServiceOrigin(FabricBase):

    def description(self):
        return "Validate that the serice origin is properly configured."

    def validate(self, org, service_name, is_etc=False, fqdn='code.corp.surveymonkey.com'):
        if is_etc:
            path = self._etc_path()
        else:
            path = self._service_path()

        with warn_only(path):
            self.result = run("git remote -v | head -1 | awk '{print $2}'")

        self.origin = "git@%s:%s/%s.git" % (fqdn, org, service_name)
        return self.validate_logic(self.result == self.origin)


    def error_text(self):
        output = "The origin '%s' does not match \
                      the intended origin '%s'" % (self.result, self.origin)
        return self.error_logic(output)


