

class ExampleRule(object):

    def __init__(self):
        self.category = 'Example'

    def description(self):
        return "Validate that this service does what it should"

    def validate(self, branch):
        self.branch = branch
        with warn_only(self._service_path()):
            self.result = run("git symbolic-ref HEAD 2>/dev/null | cut -d'/' -f 3")
        return self.validate_logic(self.result == branch)

    def error_text(self):
        output = "The branch '%s' does not match \
                      the intended branch '%s'" % (self.result, self.branch)
        return self.error_logic(output)