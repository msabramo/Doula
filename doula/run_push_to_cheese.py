from doula.models.package import Package
from doula.config import Config

job_dict = {
    'package_name': 'smlib.memcached',
    'remote': 'git@code.corp.surveymonkey.com:devmonkeys/smlib.memcached.git',
    'branch': 'master',
    'version': '0.1'
}

config = {
    "debug_routematch": False,
    "doula.github.html.domain": "http://code.corp.surveymonkey.com",
    "pyramid.reload_templates": False,
    "debug_templates": False,
    "task_interval_pull_bambino": "600",
    "task_interval_pull_appenv_github_data": "900",
    "github.scope": "user, repo",
    "default_locale_name": "en",
    "github.consumer_key": "c013d2a652ef96a800e0",
    "reload_resources": False,
    "pyramid.debug_authorization": False,
    "task_interval_cleanup_queue": "36240",
    "doula.github.packages.org": "devmonkeys",
    "github.domain": "code.corp.surveymonkey.com",
    "reload_assets": False,
    "env": "prod",
    "pyramid.prevent_http_cache": False,
    "bambino.webapp_dir": "'/opt/webapp'",
    "js_path": "/Users/alexvazquez/Projects/Doula/doula/static/js",
    "prod_js_path": "/Users/alexvazquez/Projects/Doula/doula/static/prodjs",
    "doula.github.doula.admins.org": "DoulaAdmins",
    "jinja2.directories": "doula:templates",
    "task_interval_pull_cheesprism_data": "900",
    "doula.session.secret": "d4c84eed159abf6049dc53c1aa7ec85edb150fb2",
    "pyramid.debug_templates": False,
    "task_interval_pull_github_data": "1800",
    "reload_templates": False,
    "redis.host": "localhost",
    "pyramid.debug_routematch": False,
    "pyramid.reload_assets": False,
    "debug_notfound": False,
    "doula.cheeseprism_url": "http://yorick.corp.surveymonkey.com:9003",
    "doula.github.token": "17e6642dca429043725ad6a98ce966e5a67eac69",
    "doula.github.api.domain": "http://api.code.corp.surveymonkey.com",
    "debug_authorization": False,
    "pyramid.reload_resources": False,
    "doula.assets.dir": "/mnt/smassets/",
    "github.consumer_secret": "cc70b42f79bdad7765f89c39325d474e8bc79f0b",
    "token": "bagels_with_no_holes",
    "redis.port": "6379",
    "prevent_http_cache": False,
    "pyramid.debug_notfound": False,
    "jinja2.extensions": ["jinja2.ext.i18n"],
    "doula.keyfile_path": "~/.ssh/id_rsa",
    "pyramid.default_locale_name": "en",
    "github.secure": "False",
    "doula.github.appenvs.org": "AppEnv"}

# {'status': 'queued', 'user_id': 'alexv', 'time_started':
# 1350516859.581536, 'package_name': 'dummycode', 'job_type':
# 'build_new_package', 'site': 'alexs-macbook-pro-6.local',
# 'service': 'createweb', 'version': '2.7.103-test', 'branch':
# 'test', 'remote': 'git@code.corp.surveymonkey.com:devmonkeys/dummycode.git',
# 'id': '2c4a4a1c18b311e2ac8ab8f6b1191577', 'exc': ''}
Config.load_config(config)

p = Package(job_dict['package_name'], '0', job_dict['remote'])
p.distribute(job_dict['branch'], job_dict['version'])
