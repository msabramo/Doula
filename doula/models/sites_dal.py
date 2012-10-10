import simplejson as json
import logging

from datetime import datetime
from doula.cache import Cache
from doula.util import dirify

log = logging.getLogger('doula')


class SiteDAL(object):
    cache = None

    def __init(self):
        pass

    @staticmethod
    def get_cache():
        if not SiteDAL.cache:
            SiteDAL.cache = Cache.cache()
        return SiteDAL.cache

    @staticmethod
    def list_of_sites_and_services():
        sas = {'sites': [], 'services': []}

        for s, site in SiteDAL.get_sites().iteritems():
            sas['sites'].append(s)

            for name, service in site.services.iteritems():
                if not name in sas['services']:
                    sas['services'].append(str(name))

        return sas

    @staticmethod
    def save_service_as_deployed(app, tag):
        SiteDAL._add_to_deploy_set(app, tag)
        SiteDAL._set_app_tag_as_deployed(app, tag)

    @staticmethod
    def _add_to_deploy_set(app, tag):
        set_key = SiteDAL._get_deployed_app_set_key(app)
        app_details = SiteDAL._deployed_app_details(app, tag)

        cache = SiteDAL.get_cache()
        cache.sadd(set_key, json.dumps(app_details))

    @staticmethod
    def _set_app_tag_as_deployed(app, tag):
        app_key = SiteDAL._get_deployed_app_key(app)

        cache = SiteDAL.get_cache()
        cache.set(app_key, tag.name)

    @staticmethod
    def is_deployed(app, tag):
        cache = SiteDAL.get_cache()
        deployed_tag = cache.get(SiteDAL._get_deployed_app_key(app))

        return deployed_tag == tag.name

    @staticmethod
    def _deployed_app_details(app, tag):
        """
        Returns a dictionary with the values
        { datetime: value, tag: value, comment: value }
        """
        return {
            'tag': tag.name,
            'message': tag.message,
            'datetime': SiteDAL._timestamp()
        }

    @staticmethod
    def _timestamp():
        return datetime.now().isoformat()

    @staticmethod
    def _get_deployed_app_set_key(app):
        return '_'.join([app.site_name, app.name_url, 'deploy_tags'])

    @staticmethod
    def _get_deployed_app_key(app):
        return '_'.join([app.site_name, app.name_url, 'deployed'])

    @staticmethod
    def register_node(node):
        node = SiteDAL._lower_keys(node)
        site = SiteDAL._get_site_as_json(node['site'])
        site['nodes'][node['name']] = node

        log.info('Registering site')
        log.info(json.dumps(site))

        cache = SiteDAL.get_cache()

        # Add to the doula sites set
        cache.sadd("doula.sites", node['site'])

        # Set the site json
        site_cache_key = SiteDAL._get_site_cache_key(node['site'])
        cache.set(site_cache_key, json.dumps(site))

    @staticmethod
    def _lower_keys(node):
        lower_node = {}
        for k, v in node.iteritems():
            lower_node[k.lower()] = v.lower()
        return lower_node

    @staticmethod
    def unregister_node(node):
        cache = SiteDAL.get_cache()

        site = SiteDAL._get_site_as_json(node['site'])
        name = node['name'].lower()
        del site['nodes'][name]

        site_cache_key = SiteDAL._get_site_cache_key(node['site'])
        cache.set(site_cache_key, json.dumps(site))

        # If the site has no nodes left remove from cache
        if len(site['nodes']) == 0:
            cache.srem(node['site'])
            cache.delete(site_cache_key)

    @staticmethod
    def _get_site_cache_key(name):
        return 'site:' + dirify(name)

    @staticmethod
    def _get_site_as_json(name):
        """
        Get the site jsonified object from cache. If the site
        doesn't exist create one.
        Site is a dict:
            {'name':'value',
            nodes: [{'name':{'name':value, 'site':value, 'url':value}}]}
        """
        name = name.lower()
        cache = SiteDAL.get_cache()
        site_as_json = cache.get(SiteDAL._get_site_cache_key(name))

        print 'SITE AS JSON'
        print site_as_json

        if site_as_json:
            return json.loads(site_as_json)
        else:
            log.info('Unable to find site by name "{0}"'.format(name))
            return {'name': name, 'nodes': {}}

    @staticmethod
    def nodes(name):
        site = SiteDAL._get_site_as_json(name)

        return site['nodes']

    @staticmethod
    def _all_site_keys():
        cache = SiteDAL.get_cache()
        site_names = cache.smembers("doula.sites")

        return [site for site in site_names]

    @staticmethod
    def get_simple_sites():
        """
        Get a list of the sites that are registered
        Returned objects are dictionaries
        """
        simple_sites = {}

        for site_name in SiteDAL._all_site_keys():
            simple_sites[site_name] = SiteDAL._get_site_as_json(site_name)

        return simple_sites

    @staticmethod
    def get_sites():
        """
        Get list of registered sites. Returns actual Site object.
        """
        all_sites = {}

        for site_name in SiteDAL._all_site_keys():
            all_sites[site_name] = SiteDAL.get_site(site_name)

        return all_sites

    @staticmethod
    def get_site(site_name):
        from doula.models.site import Site
        simple_site = SiteDAL._get_site_as_json(site_name)
        return Site.build_site(simple_site)

    @staticmethod
    def get_master_site():
        """
        Return the master site. In prod will be MT1 or MTPrime.
        For Development the master site is mt1 if found or the first site found.
        """
        site_keys = SiteDAL._all_site_keys()

        if len(site_keys) < 1:
            raise Exception("No sites registered")

        if "mt1" in site_keys:
            return "mt1"
        else:
            return site_keys[0]

    @staticmethod
    def get_node_ips():
        cache = SiteDAL.get_cache()
        ips = []

        for site in SiteDAL.get_sites():
            site_cache_key = SiteDAL._get_site_cache_key(site)
            site_obj = json.loads(cache.get(site_cache_key))

            for name, node in site_obj['nodes'].iteritems():
                ips.append(node['ip'])

        return ips

    @staticmethod
    def get_service(site, app):
        site = SiteDAL.get_site(site)
        return site.services[app]
