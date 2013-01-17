# Collection of Redis Keys that we will use for Doula

from string import Template

_keys = {
  # Site + Service keys
  "site_service_label": "label:$site:$service",

  # Cheeseprism keys
  "cheeseprism_packages": "cheeseprism:packages",
  "cheeseprism_package": "cheeseprism:package:$name",

  # GitHub appenv keys
  "repos_appenvs": "repos:appenvs",

  # GitHub config keys
  "service_configs": "service:configs:$site:$service",
  "service_config_sha": "service:configs:$site:$service:$sha",

  # Release keys

  # sorted set, sorted by date, we can't do by release num
  # because older releases simply don't have a release number
  "release_counter"     : "release:$site:$service:counter",
  "releases_for_service": "releases:$site:$service",
  "release_by_number"   : "release:$site:$service:$release_number",
  "release_by_date"     : "release:$site:$service:$date"
}


def key_val(name, subs={}):
    """
    Return the redis key with the variables replaced with
    values from the subs dict
    """
    tmpl = Template(_keys[name])
    return tmpl.substitute(subs)
