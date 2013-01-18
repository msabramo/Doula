import re

class WebHook(object):

    def parse_payload(self, payload_object):
        # example payload:
        # https://gist.github.com/2732972
        # payload explained:
        # https://help.github.com/articles/post-receive-hooks

        search = re.search('^refs\/heads\/(.+)$', payload_object['ref'])
        self.branch = search.group(1)

        self.org = payload_object['repository']['organization']
        self.repo = payload_object['repository']['name']
        self.sha1 = payload_object['head_commit']['id']
        self.compare_url = payload_object['compare']

        self.payload = payload_object
