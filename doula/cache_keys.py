# Collection of Redis Keys that we will use for Doula

from string import Template

_keys = {
  # Cheeseprism keys
  "cheeseprism_packages": "cheeseprism:packages",
  "cheeseprism_package": "cheeseprism:package:$name",

  # GitHub appenv keys
  "repos_appenvs": "repos:appenvs",

  # GitHub config keys
  "service_configs": "service:configs:$site:$service",
  "service_config_sha": "service:configs:$site:$service:$sha",

  # Release keys
  "releases": "releases:$site:$service",
  "release_counter": "release:$site:$service:counter",
  "release": "release:$site:$service:$release_number"
}


def key_val(name, subs={}):
    """
    Return the redis key with the variables replaced with
    values from the subs dict
    """
    tmpl = Template(_keys[name])
    return tmpl.substitute(subs)
